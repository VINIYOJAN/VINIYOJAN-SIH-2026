import hashlib, io, json, os, re, secrets
from pathlib import Path
from datetime import date
from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError
from pypdf import PdfReader
from .config import settings

VALID = {'.pdf':'application/pdf','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg'}

def validate_and_store(content: bytes, filename: str):
    suffix = Path(filename).suffix.lower()
    if suffix not in VALID: raise HTTPException(415, 'Only PDF, JPG and PNG permitted')
    if not content or len(content) > settings.max_upload_bytes: raise HTTPException(413, 'Empty or oversized document (max 8 MB)')
    try:
        if suffix == '.pdf':
            if not content.startswith(b'%PDF-'): raise ValueError('Invalid PDF signature')
            reader = PdfReader(io.BytesIO(content), strict=True)
            if len(reader.pages) < 1: raise ValueError('Empty PDF')
            if reader.is_encrypted: raise ValueError('Encrypted PDF not accepted in demo')
        else:
            with Image.open(io.BytesIO(content)) as image:
                if image.format != ('PNG' if suffix == '.png' else 'JPEG'): raise ValueError('File signature mismatch')
                image.verify()
    except Exception: raise HTTPException(422, 'File contents invalid or corrupted')
    digest = hashlib.sha256(content).hexdigest()
    key = f'{secrets.token_hex(16)}{suffix}'
    path = Path(settings.vault_dir)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    target = path / key
    with open(target, 'xb') as f: f.write(content)
    os.chmod(target, 0o600)
    return key, digest

def extract_ocr(content: bytes, filename: str):
    text = ''
    try:
        if filename.lower().endswith('.pdf'):
            reader = PdfReader(io.BytesIO(content))
            text = '\n'.join((page.extract_text() or '') for page in list(reader.pages)[:3])[:10000]
        else:
            import pytesseract
            text = pytesseract.image_to_string(Image.open(io.BytesIO(content)))[:10000]
    except Exception: pass
    # Text extraction is a suggestion only, never a verification decision.
    amount = re.search(r'(?:amount|deposit)\s*[:₹Rs. ]+([\d,]+(?:\.\d{1,2})?)', text, re.I)
    instrument = re.search(r'(?:instrument|fdr|receipt)\s*(?:number|no\.?|#)\s*[:\- ]+([A-Za-z0-9\-/]{3,80})', text, re.I)
    bank = re.search(r'(?:bank)\s*[:\-]\s*([^\n]{3,70})', text, re.I)
    date_match = re.search(r'(?:maturity\s*date)\s*[:\- ]+([\d/\-]{8,10})', text, re.I)
    return {'instrument_number':instrument.group(1).strip() if instrument else None,'bank_name':bank.group(1).strip() if bank else None,'amount':amount.group(1).replace(',','') if amount else None,'maturity_date':date_match.group(1) if date_match else None,'text_found':bool(text.strip()),'engine':'PDF text / optional Tesseract','review_required':True}

def risk_signals(content: bytes, filename: str):
    reasons = []
    if filename.lower().endswith('.pdf'):
        try:
            reader = PdfReader(io.BytesIO(content))
            metadata = reader.metadata
            if metadata and metadata.get('/ModDate'): reasons.append('PDF modification date is present; review document history')
        except Exception: pass
    return {'level':'Review' if reasons else 'Unknown', 'signals':reasons, 'note':'Heuristic signals are not evidence of forgery. Manual verification required.'}


def compare_extracted_fields(extracted, submitted):
    """Suggest field matches, never an authenticity or fraud verdict."""
    from decimal import Decimal, InvalidOperation
    from datetime import datetime
    results = {}
    for field in ('instrument_number','bank_name','amount','maturity_date'):
        raw = extracted.get(field)
        if not raw:
            results[field] = {'result':'not_extracted','extracted':None}
            continue
        expected = str(submitted[field]).strip()
        observed = str(raw).strip()
        if field == 'amount':
            try: match = Decimal(observed.replace(',','')) == Decimal(expected)
            except InvalidOperation: match = False
        elif field == 'maturity_date':
            try:
                parsed = datetime.strptime(observed, '%d/%m/%Y').date().isoformat() if '/' in observed else datetime.strptime(observed, '%Y-%m-%d').date().isoformat()
                match = parsed == expected
            except ValueError: match = False
        else:
            match = ' '.join(observed.lower().split()) == ' '.join(expected.lower().split())
        results[field] = {'result':'match' if match else 'review_mismatch','extracted':observed}
    return results
