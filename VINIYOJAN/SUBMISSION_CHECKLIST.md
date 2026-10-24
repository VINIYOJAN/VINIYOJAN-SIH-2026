# VINIYOJAN — Pre-submission checklist

**Status: candidate deliverable. NOT certified submission-ready until local verification succeeds.**

- [ ] Rebuild services: `docker compose up --build -d`
- [ ] Seed only on fresh database: `docker compose exec api python -m app.seed`
- [ ] Open UI at `http://localhost:5173` and API at `http://localhost:8000/docs`
- [ ] Run automated Python tests: `docker compose exec api pytest -q`
- [ ] Compile frontend: `docker compose exec web npm run build`
- [ ] Log in as College 1 and submit a new synthetic FDR
- [ ] Log in as officer and confirm new record appears
- [ ] Confirm activation is blocked before simulated Valid bank result
- [ ] Record simulated valid check for a known valid FDR and activate with 10+ character note
- [ ] Request release as College 1, then approve/reject as assigned officer with 15+ character evidence
- [ ] Confirm released record cannot be modified
- [ ] Check document audit timeline and OCR comparisons
- [ ] As system admin, POST `/demo/alerts` and view `/alerts` for visible records
- [ ] Verify College 2 cannot access College 1 FDRs, documents, or alerts
- [ ] Make sure screenshots and narration say **prototype, simulated bank validation, synthetic demo data**
- [ ] Test on target demonstration laptop, including database persistence after refresh
- [ ] Remove publicly exposed demo accounts before any deployment to shared infrastructure
- [ ] Store `.env` safely and back up database/vault; do not commit secrets

## Demonstration flow (approx. 3–5 minutes)
1. Problem: manual tracking / compliance difficulties.
2. College login, FDR submission, secure evidence storage.
3. Officer sees assigned submission, original PDF, OCR suggestion and mismatch review.
4. Mock bank verification (explicitly simulated); officer records decision.
5. College requests release, officer reviews and records demo decision.
6. View lifecycle timeline, maturity alerts and audit trail.
7. Close with security / role separation and next production steps.

## Outstanding future engineering
Alembic migrations, multi-officer routing/permissions, calibrated OCR confidence, virus scanning, secure notifications, real audit exports, and deployment hardening.
