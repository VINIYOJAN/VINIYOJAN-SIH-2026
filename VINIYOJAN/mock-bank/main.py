from fastapi import FastAPI
from pydantic import BaseModel
app=FastAPI(title='SIMULATED BANK API - DEMO ONLY')
class Query(BaseModel):
    instrument_number:str
    bank_name:str
@app.post('/verify')
def verify(q:Query):
    # Deterministic synthetic registry, never a real bank connection.
    valid=q.instrument_number.upper() in {'DEMO-FDR-1001','DEMO-FDR-1002','DEMO-FDR-2001'}
    return {'valid':valid,'source':'SYNTHETIC_TEST_REGISTRY','disclaimer':'No banking system contacted'}
