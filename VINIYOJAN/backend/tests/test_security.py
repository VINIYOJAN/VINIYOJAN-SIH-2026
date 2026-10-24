import os
os.environ['DATABASE_URL']='sqlite:///./test_viniyojan.db'
os.environ['VAULT_DIR']='./test_vault'
from fastapi.testclient import TestClient
from app.main import app
from app.db import SessionLocal
from app.models import Base, Institution, User, FDR
from app.db import engine
from app.security import passwords
from datetime import date,timedelta

def setup_module():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        a=Institution(aicte_id='TEST-1',name='One',spoc_name='A',email='a@x.test')
        b=Institution(aicte_id='TEST-2',name='Two',spoc_name='B',email='b@x.test')
        db.add_all([a,b]);db.flush()
        db.add_all([User(email='one@x.test',full_name='One',role='College_Admin',password_hash=passwords.hash('testpassword'),institution_id=a.id),User(email='two@x.test',full_name='Two',role='College_Admin',password_hash=passwords.hash('testpassword'),institution_id=b.id)])
        db.flush()
        db.add(FDR(institution_id=b.id,instrument_number='OTHER-123',bank_name='Sample',amount=1000,issue_date=date.today()-timedelta(days=100),maturity_date=date.today()+timedelta(days=100),file_key='not-present.pdf',file_sha256='0'*64,original_filename='test.pdf'))
        db.commit()

def test_tenant_isolation():
    with TestClient(app) as client:
        res=client.post('/auth/login',json={'email':'one@x.test','password':'testpassword'})
        assert res.status_code==200
        headers={'Authorization':'Bearer '+res.json()['access_token']}
        assert client.get('/fdrs',headers=headers).json()['total']==0
        with SessionLocal() as db: foreign=db.query(FDR).first().id
        assert client.get('/fdrs/'+foreign,headers=headers).status_code==404
        assert client.get('/fdrs/'+foreign+'/document',headers=headers).status_code==404
        assert client.post('/fdrs/'+foreign+'/release',headers=headers,json={'justification':'Please release the deposit based on approval'}).status_code==404
        assert client.patch('/fdrs/'+foreign+'/status',headers=headers,json={'status':'Active'}).status_code==403

def test_auth_required():
    with TestClient(app) as client: assert client.get('/fdrs').status_code==401


def test_unknown_role_cannot_access_any_fdr():
    with SessionLocal() as db:
        user = User(email='unknown@x.test', full_name='Unknown Role', role='Unexpected_Role',
                    password_hash=passwords.hash('testpassword'))
        db.add(user)
        db.commit()
    with TestClient(app) as client:
        response = client.post('/auth/login', json={'email':'unknown@x.test','password':'testpassword'})
        assert response.status_code == 200
        headers = {'Authorization': 'Bearer ' + response.json()['access_token']}
        assert client.get('/fdrs', headers=headers).status_code == 403
        assert client.get('/dashboard', headers=headers).status_code == 403
        with SessionLocal() as db:
            fdr_id = db.query(FDR).first().id
        assert client.get('/fdrs/' + fdr_id, headers=headers).status_code == 403
        assert client.get('/fdrs/' + fdr_id + '/document', headers=headers).status_code == 403


def test_college_user_without_institution_is_denied():
    with SessionLocal() as db:
        user = User(email='orphan@x.test', full_name='Orphan College User', role='College_Admin',
                    password_hash=passwords.hash('testpassword'), institution_id=None)
        db.add(user)
        db.commit()
    with TestClient(app) as client:
        response = client.post('/auth/login', json={'email':'orphan@x.test','password':'testpassword'})
        assert response.status_code == 200
        headers = {'Authorization': 'Bearer ' + response.json()['access_token']}
        assert client.get('/fdrs', headers=headers).status_code == 403
        assert client.get('/dashboard', headers=headers).status_code == 403
