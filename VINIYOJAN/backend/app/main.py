from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
from typing import Annotated
import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Depends, File, Form, HTTPException, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .config import settings
from .db import engine, get_db
from .models import Base, User, Institution, FDR, AuditLog, AlertLog
from .security import passwords, create_token, current_user, require_roles
from .services import validate_and_store, extract_ocr, risk_signals, compare_extracted_fields
from .alerts import run_alerts

scheduler = BackgroundScheduler(timezone='Asia/Kolkata')
@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)  # use Alembic migrations in production
    if settings.enable_scheduler:
        scheduler.add_job(run_alerts,'cron',hour=0,minute=0,id='maturity-alerts',replace_existing=True)
        scheduler.start()
    yield
    if scheduler.running: scheduler.shutdown()

app = FastAPI(title='VINIYOJAN | FDR Intelligence API', version='0.1.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[settings.cors_origin], allow_credentials=False, allow_methods=['GET','POST','PATCH'], allow_headers=['Authorization','Content-Type'])

def audit(db, user, fdr, action, detail=''):
    db.add(AuditLog(user_id=user.id if user else None,fdr_id=fdr.id if fdr else None,action=action,detail=detail))

def visible(db, user):
    q = select(FDR)
    if user.role == 'College_Admin':
        if not user.institution_id:
            raise HTTPException(403, 'No institution assigned')
        return q.where(FDR.institution_id == user.institution_id)
    if user.role == 'AICTE_Verification_Officer':
        return q.where(FDR.assigned_officer_id == user.id)
    if user.role == 'System_Admin':
        return q
    raise HTTPException(403, 'Unrecognized role')

def get_visible_fdr(db, user, fdr_id):
    rec = db.scalar(visible(db,user).where(FDR.id==fdr_id))
    if not rec: raise HTTPException(404,'FDR not found')
    return rec

def serialize(db, f):
    institution = db.get(Institution,f.institution_id)
    return {'id':f.id,'institution_id':f.institution_id,'institution_name':institution.name,'instrument_number':f.instrument_number,'bank_name':f.bank_name,'amount':str(f.amount),'issue_date':str(f.issue_date),'maturity_date':str(f.maturity_date),'days_to_maturity':(f.maturity_date-date.today()).days,'status':f.status,'bank_result':f.bank_result,'ocr':json.loads(f.ocr_json),'risk':json.loads(f.risk_json),'discrepancy_note':f.discrepancy_note,'release_justification':f.release_justification,'release_status':f.release_status,'created_at':f.created_at.isoformat(),'assigned_officer_id':f.assigned_officer_id,'file_url':f'/fdrs/{f.id}/document'}

class Login(BaseModel):
    email: str
    password: str
@app.post('/auth/login')
def login(data: Login, db: Session=Depends(get_db)):
    user = db.scalar(select(User).where(User.email==data.email.lower()))
    if not user or not user.is_active or not passwords.verify(data.password,user.password_hash): raise HTTPException(401,'Invalid credentials')
    return {'access_token':create_token(user), 'token_type':'bearer'}

@app.get('/auth/me')
def me(user: User=Depends(current_user), db: Session=Depends(get_db)):
    inst=db.get(Institution,user.institution_id) if user.institution_id else None
    return {'id':user.id,'email':user.email,'name':user.full_name,'role':user.role,'institution':inst.name if inst else None}

@app.get('/health')
def health(): return {'status':'ok','service':'VINIYOJAN'}

@app.get('/fdrs')
def list_fdrs(status: str | None=None, search: str | None=None, page:int=Query(1,ge=1),limit:int=Query(12,ge=1,le=100),db:Session=Depends(get_db),user:User=Depends(current_user)):
    q=visible(db,user)
    if status: q=q.where(FDR.status==status)
    if search: q=q.where(FDR.instrument_number.ilike(f'%{search[:80]}%'))
    total=db.scalar(select(func.count()).select_from(q.subquery()))
    records=db.scalars(q.order_by(FDR.created_at.desc()).offset((page-1)*limit).limit(limit)).all()
    return {'items':[serialize(db,x) for x in records],'total':total,'page':page,'limit':limit}

@app.get('/dashboard')
def dashboard(db:Session=Depends(get_db),user:User=Depends(current_user)):
    records=db.scalars(visible(db,user)).all()
    statuses={}
    for f in records: statuses[f.status]=statuses.get(f.status,0)+1
    return {'total':len(records),'active':sum(f.status in ('Active','Expiring') for f in records),'expiring':sum(f.status not in ('Released','Discrepancy') and 0 <= (f.maturity_date-date.today()).days <= 30 for f in records),'action_required':sum(f.status in ('Pending','Discrepancy') or f.release_status=='Requested' for f in records),'statuses':statuses,'total_amount':str(sum((f.amount for f in records), Decimal(0)))}

@app.post('/fdrs',status_code=201)
async def upload_fdr(instrument_number:Annotated[str,Form()],bank_name:Annotated[str,Form()],amount:Annotated[Decimal,Form()],issue_date:Annotated[date,Form()],maturity_date:Annotated[date,Form()],file:UploadFile=File(...), db:Session=Depends(get_db),user:User=Depends(require_roles('College_Admin'))):
    if not user.institution_id: raise HTTPException(403,'No institution assigned')
    if amount<=0 or amount>Decimal('9999999999999999.99'): raise HTTPException(422,'Invalid amount')
    if issue_date>=maturity_date: raise HTTPException(422,'Maturity must follow issue date')
    if not (3<=len(instrument_number.strip())<=80 and 2<=len(bank_name.strip())<=200): raise HTTPException(422,'Invalid FDR fields')
    if db.scalar(select(FDR).where(FDR.institution_id==user.institution_id,FDR.instrument_number==instrument_number.strip())): raise HTTPException(409,'Instrument already exists')
    content=await file.read(settings.max_upload_bytes+1)
    key,digest=validate_and_store(content,file.filename or 'unknown')
    ocr=extract_ocr(content,file.filename or '')
    ocr['comparison']=compare_extracted_fields(ocr,{'instrument_number':instrument_number,'bank_name':bank_name,'amount':amount,'maturity_date':maturity_date})
    risk=risk_signals(content,file.filename or '')
    officer=db.scalar(select(User).where(User.role=='AICTE_Verification_Officer',User.is_active.is_(True)).order_by(User.email))
    if not officer: raise HTTPException(503,'No active verification officer available; contact administrator')
    rec=FDR(institution_id=user.institution_id,assigned_officer_id=officer.id,instrument_number=instrument_number.strip(),bank_name=bank_name.strip(),amount=amount,issue_date=issue_date,maturity_date=maturity_date,file_key=key,file_sha256=digest,original_filename=(file.filename or '')[:200],ocr_json=json.dumps(ocr),risk_json=json.dumps(risk))
    db.add(rec);db.flush();audit(db,user,rec,'FDR_UPLOADED',f'File SHA256: {digest}');audit(db,user,rec,'OFFICER_ASSIGNED',f'Officer ID: {officer.id}');db.commit()
    return serialize(db,rec)

@app.get('/fdrs/{fdr_id}')
def detail(fdr_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    return serialize(db,get_visible_fdr(db,user,fdr_id))

@app.get('/fdrs/{fdr_id}/document')
def document(fdr_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    rec=get_visible_fdr(db,user,fdr_id)
    p=Path(settings.vault_dir)/rec.file_key
    if not p.is_file():raise HTTPException(404,'Document missing')
    ext=p.suffix.lower()
    return FileResponse(p,media_type={'.pdf':'application/pdf','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png'}[ext],headers={'Cache-Control':'no-store','Content-Disposition':'inline; filename="fdr-document'+ext+'"','X-Content-Type-Options':'nosniff'})

class StatusUpdate(BaseModel):
    status: str
    note: str = Field('',max_length=2000)
@app.patch('/fdrs/{fdr_id}/status')
def update_status(fdr_id:str,body:StatusUpdate,db:Session=Depends(get_db),user:User=Depends(require_roles('AICTE_Verification_Officer','System_Admin'))):
    rec=get_visible_fdr(db,user,fdr_id)
    if body.status not in ('Active','Discrepancy','Released'):raise HTTPException(422,'Unsupported transition')
    if rec.status=='Released':raise HTTPException(409,'Released record is immutable')
    if body.status=='Discrepancy' and rec.status not in ('Pending','Active','Expiring','Matured','Discrepancy'):raise HTTPException(409,'Cannot flag this record')
    if body.status=='Discrepancy' and len(body.note.strip())<5:raise HTTPException(422,'Provide discrepancy details')
    if body.status=='Released':raise HTTPException(409,'Use the dedicated release decision endpoint')
    if body.status=='Active':
        if rec.status not in ('Pending','Discrepancy'): raise HTTPException(409,'Only pending or flagged records can be verified')
        if rec.bank_result!='Valid': raise HTTPException(409,'A valid simulated bank check is required before activation')
        if len(body.note.strip())<10: raise HTTPException(422,'Record review evidence (at least 10 characters)')
        if rec.status=='Discrepancy' and len(body.note.strip())<20:raise HTTPException(422,'Document the discrepancy resolution (at least 20 characters)')
    previous=rec.status;rec.status=body.status
    if body.status=='Discrepancy':rec.discrepancy_note=body.note.strip()
    if body.status=='Active' and previous=='Discrepancy':rec.discrepancy_note=None
    audit(db,user,rec,'STATUS_CHANGED',f'{previous} -> {body.status}; note={body.note}')
    db.commit();return serialize(db,rec)

class ReleaseRequest(BaseModel):
    justification: str = Field(min_length=15,max_length=3000)
@app.post('/fdrs/{fdr_id}/release')
def request_release(fdr_id:str,body:ReleaseRequest,db:Session=Depends(get_db),user:User=Depends(require_roles('College_Admin'))):
    rec=get_visible_fdr(db,user,fdr_id)
    if rec.status not in ('Active','Expiring','Matured'):raise HTTPException(409,'FDR is not eligible for a release request')
    if rec.release_status=='Requested':raise HTTPException(409,'Release already requested')
    if rec.release_status.startswith('Approved'):raise HTTPException(409,'Release already approved')
    rec.release_justification=body.justification;rec.release_status='Requested'
    audit(db,user,rec,'RELEASE_REQUESTED',body.justification);db.commit();return serialize(db,rec)

class ReleaseDecision(BaseModel):
    decision: str
    note: str = Field(min_length=15, max_length=2000)

@app.post('/fdrs/{fdr_id}/release/decision')
def release_decision(fdr_id:str,body:ReleaseDecision,db:Session=Depends(get_db),user:User=Depends(require_roles('AICTE_Verification_Officer','System_Admin'))):
    rec=get_visible_fdr(db,user,fdr_id)
    if rec.release_status!='Requested':raise HTTPException(409,'No pending release request')
    if body.decision not in ('Approved','Rejected'):raise HTTPException(422,'Invalid release decision')
    if body.decision=='Approved' and rec.status not in ('Active','Expiring','Matured'):
        raise HTTPException(409,'FDR is not eligible for release approval')
    rec.release_status=body.decision+' (demo only)'
    if body.decision=='Approved':rec.status='Released'
    audit(db,user,rec,'RELEASE_'+body.decision.upper(),body.note.strip())
    db.commit()
    return serialize(db,rec)

@app.get('/alerts')
def list_alerts(db:Session=Depends(get_db),user:User=Depends(current_user)):
    allowed=visible(db,user).with_only_columns(FDR.id)
    alerts=db.execute(select(AlertLog,FDR).join(FDR,FDR.id==AlertLog.fdr_id).where(FDR.id.in_(allowed)).order_by(AlertLog.created_at.desc()).limit(100)).all()
    return [{'id':alert.id,'fdr_id':record.id,'instrument_number':record.instrument_number,'threshold_days':alert.threshold_days,'maturity_date':str(alert.maturity_date),'created_at':alert.created_at.isoformat()} for alert,record in alerts]

@app.get('/fdrs/{fdr_id}/timeline')
def timeline(fdr_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    rec=get_visible_fdr(db,user,fdr_id)
    logs=db.scalars(select(AuditLog).where(AuditLog.fdr_id==rec.id).order_by(AuditLog.created_at.asc())).all()
    return [{'action':x.action,'detail':x.detail,'at':x.created_at.isoformat()} for x in logs]

@app.post('/fdrs/{fdr_id}/bank-check')
async def bank_check(fdr_id:str,db:Session=Depends(get_db),user:User=Depends(require_roles('AICTE_Verification_Officer','System_Admin'))):
    rec=get_visible_fdr(db,user,fdr_id)
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response=await client.post(settings.mock_bank_url+'/verify',json={'instrument_number':rec.instrument_number,'bank_name':rec.bank_name})
            response.raise_for_status(); result=response.json()
        outcome='Valid' if result.get('valid') is True else 'Invalid'
    except (httpx.HTTPError,ValueError): outcome='Unavailable'
    if rec.status=='Released':raise HTTPException(409,'Released record is immutable')
    rec.bank_result=outcome;audit(db,user,rec,'MOCK_BANK_CHECK',outcome+' (simulated)');db.commit()
    return {'result':outcome,'is_simulated':True}

@app.get('/audit')
def audit_entries(db:Session=Depends(get_db),user:User=Depends(require_roles('AICTE_Verification_Officer','System_Admin'))):
    allowed=[f.id for f in db.scalars(visible(db,user)).all()]
    logs=db.scalars(select(AuditLog).where(AuditLog.fdr_id.in_(allowed)).order_by(AuditLog.created_at.desc()).limit(100)).all()
    return [{'action':l.action,'detail':l.detail,'created_at':l.created_at.isoformat(),'fdr_id':l.fdr_id} for l in logs]

@app.post('/demo/alerts')
def demo_alerts(user:User=Depends(require_roles('System_Admin'))):
    if not settings.demo_mode:raise HTTPException(404,'Unavailable')
    return {'messages':run_alerts()}
