from datetime import date, timedelta
import json
from pathlib import Path
from .db import engine, SessionLocal
from .models import Base, Institution, User, FDR
from .security import passwords
from .config import settings
from .services import validate_and_store

def synthetic_pdf(label):
    # Valid self-contained one-page PDF built without external packages.
    safe=label.replace('(','').replace(')','').replace('\\','')
    content=f'BT /F1 18 Tf 60 740 Td ({safe}) Tj ET'.encode()
    objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',b'<< /Length '+str(len(content)).encode()+b' >>\nstream\n'+content+b'\nendstream']
    data=b'%PDF-1.4\n';positions=[0]
    for i,obj in enumerate(objs,1):
        positions.append(len(data));data+=f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n'
    xref=len(data);data+=f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode()
    for offset in positions[1:]:data+=f'{offset:010d} 00000 n \n'.encode()
    data+=f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF'.encode()
    return data

def seed():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(User).first():
            print('Existing users found; seed skipped');return
        colleges=[Institution(aicte_id='SYN-AICTE-001',name='Sahyadri Institute of Technology (Demo)',spoc_name='Ananya Kulkarni',email='spoc@sahyadri.example'),Institution(aicte_id='SYN-AICTE-002',name='Riverstone College of Engineering (Demo)',spoc_name='Vikram Shah',email='spoc@riverstone.example'),Institution(aicte_id='SYN-AICTE-003',name='Horizon Polytechnic (Demo)',spoc_name='Meera Joshi',email='spoc@horizon.example')]
        db.add_all(colleges);db.flush()
        pwd=passwords.hash('Demo@12345')
        people=[User(email='college1@demo.test',password_hash=pwd,full_name='Sahyadri College Admin',role='College_Admin',institution_id=colleges[0].id),User(email='college2@demo.test',password_hash=pwd,full_name='Riverstone College Admin',role='College_Admin',institution_id=colleges[1].id),User(email='officer@demo.test',password_hash=pwd,full_name='AICTE Regional Verification Officer',role='AICTE_Verification_Officer'),User(email='admin@demo.test',password_hash=pwd,full_name='System Administrator',role='System_Admin')]
        db.add_all(people);db.flush()
        specs=[(colleges[0],'DEMO-FDR-1001','State Bank of Demo','2500000',30,'Active'),(colleges[0],'DEMO-FDR-1002','National Sample Bank','1400000',7,'Pending'),(colleges[1],'DEMO-FDR-2001','State Bank of Demo','3500000',15,'Active'),(colleges[1],'DEMO-FDR-2002','National Sample Bank','950000',-3,'Discrepancy'),(colleges[2],'DEMO-FDR-3001','Sample Cooperative Bank','1150000',90,'Pending')]
        for inst,num,bank,amount,days,status in specs:
            pdf=synthetic_pdf('SYNTHETIC DEMO FDR - '+num+' - NOT A BANK DOCUMENT')
            key,digest=validate_and_store(pdf,num+'.pdf')
            rec=FDR(institution_id=inst.id,assigned_officer_id=people[2].id,instrument_number=num,bank_name=bank,amount=amount,issue_date=date.today()-timedelta(days=300),maturity_date=date.today()+timedelta(days=days),status=status,file_key=key,file_sha256=digest,original_filename=num+'.pdf',ocr_json=json.dumps({'text_found':True,'engine':'PDF text','review_required':True}),risk_json=json.dumps({'level':'Unknown','signals':[],'note':'Demo data'}),discrepancy_note='Bank stamp requires clarification' if status=='Discrepancy' else None)
            db.add(rec)
        db.commit()
        print('Seed complete. Accounts: college1@demo.test, college2@demo.test, officer@demo.test, admin@demo.test | Password: Demo@12345')

if __name__=='__main__':seed()
