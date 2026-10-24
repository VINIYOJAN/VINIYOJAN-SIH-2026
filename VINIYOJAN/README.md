# VINIYOJAN — Next-generation Instrument & Deposit Health Intelligence

**Student-built AICTE-inspired FDR management prototype. Not an official government product, production system, or connected bank service.**

A complete runnable MVP with role-scoped dashboards, original-document review, audit history, OCR assistance, integrity cues, mock-bank verification, release requests and maturity alert generation.

## Quick start — Docker

1. Install Docker Desktop / Docker Engine with Compose.
2. In this folder run `cp .env.example .env` and replace both secret placeholders with random secrets.
3. Run `docker compose up --build -d`.
4. Seed once: `docker compose exec api python -m app.seed`.
5. Open **http://localhost:5173**. Backend API docs: **http://localhost:8000/docs**.

If dependencies changed, rebuild with `docker compose up --build -d`.

| Demo identity | Login email | Password |
|---|---|---|
| College 1 | college1@demo.test | Demo@12345 |
| College 2 | college2@demo.test | Demo@12345 |
| AICTE-style officer | officer@demo.test | Demo@12345 |
| Platform admin | admin@demo.test | Demo@12345 |

**Local-only demo credentials. Never use them in a public deployment.** All seed data and PDFs are synthetic.

## What is implemented

- React/Vite responsive design for college and officer roles, review workbench, live status counts and portfolio chart.
- FastAPI documented endpoints with JWT expiry and Argon2 password hashing.
- PostgreSQL persistence with scoped record lookups, UUIDs, per-institution instrument uniqueness, decimal-valued FDR amounts, event audit trail.
- Restricts colleges to their own institution; officers only see assigned records; system admin sees all.
- Type and signature validation, PDF parse checks, file size cap, random nonpublic vault keys, checksum; bytes served only after authorization.
- Text extraction from born-digital PDFs and optional Tesseract OCR for images; heuristic metadata review signals. Neither proves authenticity.
- Synthetic bank check (deterministic fixture registry) with clear simulated labeling.
- College release request and officer decision; **demo approval is not a legally sufficient release authorization**.
- APScheduler daily at midnight IST, idempotent milestone alerts, stdout delivery for 30/15/7-day windows (no outbound email credentials required).
- Security-focused isolation tests and a prewritten demo story.

## Important limitations

This is a judged-demo MVP, **not government/financial production ready**. To deploy responsibly, add verified policy workflow and required multi-cell clearances, secure session architecture, refresh and revocation, MFA/SSO, hardened rate limits, malware scanning and content disarm, object storage encryption/KMS, immutable offsite audits, reviewed database migrations, secrets manager, secure ingress, backups, tenant-security review, accessibility audit, and actual email gateway. Officer approvals here are intentionally simplified.

The source of truth for maturity is the issue/maturity dates, not the status label; production should model lifecycle versus review state independently. The current UI retrieves 100 records (pagination exists in the API); add server-driven pagination for scale.

> Regulatory note: AICTE publications describe additional release documents and clearance from concerned offices. This prototype **does not** claim that a single officer can grant an official release. Verify the applicable Approval Process Handbook and any updates before implementing authoritative workflows.

## API surface

| Method | Path | Access |
|---|---|---|
| POST | `/auth/login` | Public |
| GET | `/auth/me`, `/dashboard`, `/fdrs` | Authenticated, scoped |
| POST | `/fdrs` | College |
| GET | `/fdrs/{id}`, `/fdrs/{id}/document` | Scoped |
| POST | `/fdrs/{id}/release` | College owning record |
| PATCH | `/fdrs/{id}/status` | Assigned officer / admin |
| POST | `/fdrs/{id}/bank-check` | Assigned officer / admin |
| GET | `/audit` | Officer / admin |
| POST | `/demo/alerts` | Admin, only DEMO_MODE |

## Tests and alerts

`docker compose exec api pytest -q` (after installing the bundled requirements in the image).

`./scripts/demo-alerts.sh` triggers 30/15/7-day alerts with seeded records. Output appears in the JSON response and API container logs. Running it twice shows that alert events are not duplicated. Alerts are a local proof-of-concept and **do not send messages**.

## Local development without Docker

Backend: install `backend/requirements.txt`, set `PYTHONPATH=backend` or `cd backend`, run `python -m app.seed` then `uvicorn app.main:app --reload`. The default SQLite URL is **only for local prototype development**.

Frontend: `cd frontend && npm install && npm run dev`. The API defaults to `http://localhost:8000`, overridable via `VITE_API_URL` in `frontend/.env.local`.

Mock bank: `cd mock-bank && uvicorn main:app --port 8100` and set backend `MOCK_BANK_URL=http://localhost:8100`.

## Project structure

```text
backend/app/     Database model, security, API routes, OCR, seed, alerts
backend/tests/   Authorization / tenant isolation tests
frontend/src/    React user interface and design system
mock-bank/       Synthetic external verification service
docs/            Mermaid ERD, deployment backlog and demo flow
scripts/         Alert trigger helper
```

## Branching

Suggested GitHub flow: protected `main`, integration `dev`, feature PRs (`feat/auth`, `feat/ocr`, `feat/release`, `fix/tenant-check`). Require at least one review where possible, passing CI, no force pushes, and secret scanning. Add branch rules manually under GitHub repository settings; this archive cannot create repository settings on your account.
