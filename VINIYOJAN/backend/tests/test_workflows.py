"""Workflow regression tests. Run in the backend environment with dependencies installed."""
import io
import os
os.environ.setdefault('DATABASE_URL', 'sqlite:///./test_workflows.db')
os.environ.setdefault('VAULT_DIR', './test_workflows_vault')
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.main import app
from app.db import SessionLocal, engine
from app.models import Base, Institution, User, FDR
from app.seed import synthetic_pdf
from app.security import passwords


def test_assigned_submission_and_review_gates():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        inst = db.scalar(select(Institution).where(Institution.aicte_id == 'TEST-WORKFLOW-1'))
        if inst is None:
            inst = Institution(aicte_id='TEST-WORKFLOW-1',name='Test Institute',spoc_name='Verifier',email='test@sample.invalid')
            db.add(inst);db.flush()
        college = db.scalar(select(User).where(User.email=='workflow-college@demo.test'))
        officer = db.scalar(select(User).where(User.email=='workflow-officer@demo.test'))
        if not college:
            college=User(email='workflow-college@demo.test',full_name='College',role='College_Admin',institution_id=inst.id,password_hash=passwords.hash('secure-test-password'))
            db.add(college)
        if not officer:
            officer=User(email='workflow-officer@demo.test',full_name='Officer',role='AICTE_Verification_Officer',password_hash=passwords.hash('secure-test-password'))
            db.add(officer)
        db.commit()
    with TestClient(app) as client:
        def auth(email):
            r=client.post('/auth/login',json={'email':email,'password':'secure-test-password'})
            assert r.status_code==200,r.text
            return {'Authorization':'Bearer '+r.json()['access_token']}
        college_auth=auth('workflow-college@demo.test');officer_auth=auth('workflow-officer@demo.test')
        number='FLOW-'+date.today().strftime('%Y%m%d')
        upload=client.post('/fdrs',headers=college_auth,data={
            'instrument_number':number,'bank_name':'Synthetic Bank','amount':'12500.50',
            'issue_date':str(date.today()-timedelta(days=1)),'maturity_date':str(date.today()+timedelta(days=90))
        },files={'file':('synthetic.pdf',synthetic_pdf('SYNTHETIC TEST'), 'application/pdf')})
        assert upload.status_code in (201,409),upload.text
        if upload.status_code==201:record=upload.json()
        else:
            listing=client.get('/fdrs',headers=college_auth).json()['items']
            record=next(x for x in listing if x['instrument_number']==number)
        assert record['assigned_officer_id']
        rid=record['id']
        officer_records=client.get('/fdrs',headers=officer_auth).json()['items']
        assert any(x['id']==rid for x in officer_records)
        assert client.patch(f'/fdrs/{rid}/status',headers=officer_auth,json={'status':'Active','note':'Reviewed original document'}).status_code==409
        assert client.post(f'/fdrs/{rid}/release',headers=college_auth,json={'justification':'Please release this test financial instrument'}).status_code==409
        assert client.get(f'/fdrs/{rid}/timeline',headers=college_auth).status_code==200
