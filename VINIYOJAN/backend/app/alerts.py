from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal
from .models import FDR, AlertLog, Institution

THRESHOLDS = {30, 15, 7}
def run_alerts(today: date | None = None):
    today = today or date.today()
    sent = []
    with SessionLocal() as db:
        records = db.scalars(select(FDR).where(FDR.status.notin_(['Released', 'Discrepancy']))).all()
        for record in records:
            delta = (record.maturity_date - today).days
            if delta not in THRESHOLDS: continue
            existing = db.scalar(select(AlertLog).where(AlertLog.fdr_id==record.id,AlertLog.threshold_days==delta,AlertLog.maturity_date==record.maturity_date))
            if existing: continue
            db.add(AlertLog(fdr_id=record.id, threshold_days=delta, maturity_date=record.maturity_date))
            db.commit()
            institution = db.get(Institution, record.institution_id)
            message = f'[DEMO ALERT] FDR {record.instrument_number} for {institution.name} matures in {delta} days. Review the applicable conditions before taking action.'
            print(message, flush=True)
            sent.append(message)
    return sent
