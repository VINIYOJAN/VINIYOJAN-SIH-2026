# VINIYOJAN implementation status and handoff

VINIYOJAN is an **independent student prototype**, not an official AICTE or bank service.

## Implemented in this deliverable
- Product-facing identity switched from NIDHI to VINIYOJAN while preserving existing database names and demo credentials to avoid destroying local data.
- Newly submitted FDRs assigned to a deterministic active verification officer (first by email). If none exists submission returns 503. This is a single-officer MVP policy, **not** configurable institutional routing.
- Officer activation requires recorded `Valid` **synthetic** bank result and review evidence. Existing seeded Active records are preserved, not retroactively verified.
- Discrepancy resolution requires documented review notes; released records remain immutable.
- Dedicated release approval/rejection endpoint, separate from status verification, with audit events. This is a DEMO decision, not legal release authorization.
- Read-only maturity alert listing scoped by institution/officer and record audit timeline.
- OCR-assisted comparisons for number, bank, amount and maturity date, only where text was detected; `not_extracted` is not a verification failure.
- UI for alerts, field comparisons, timeline, and release decision, plus improved authorization guardrails and regression tests.
- Non-demo configuration requires a strong signing key and non-SQLite database.

## Unfinished / operational caveats
- Frontend build and full test suite have NOT been validated in this packaging environment due to unavailable npm / Python dependencies. Run the commands below on your development PC.
- OCR is pattern-based (PDF text or optional Tesseract); no calibrated confidence scores, image highlighting or field-edit history.
- Maturity events are stored and displayed, but email/SMS notification delivery has not been implemented.
- Single-officer assignment is a deterministic MVP fallback; build institution mapping and administrative reassignment before multi-officer production use.
- No production-grade migrations, report exports, full e2e browser suite, virus scanner, centralized file object store, or government/bank connectivity.
- Demo release retains a single release status field rather than a normalized decision history table; audits preserve decisions.
- No authentication rate limiting or production monitoring. Do not deploy publicly without hardening.

## Local upgrade workflow
1. Back up your existing project, Postgres data volume, and file vault.
2. Unzip this full source into a separate directory. Keep `.env` secrets private.
3. `cp .env.example .env` and set secure random values (on first setup only).
4. `docker compose up --build -d`
5. For a **fresh local database**, `docker compose exec api python -m app.seed`.
6. Open `http://localhost:5173`, `http://localhost:8000/docs`, `http://localhost:8000/health`.
7. `docker compose exec api pytest -q` and `docker compose exec web npm run build`.
8. Test College 1 → upload → officer sees record → bank simulation → review decision → release → alert history.

**Existing DB note:** The current patch does not add or remove database columns. Existing PostgreSQL names are kept to preserve existing volumes. `create_all` does not perform schema migrations.

## Acceptance checks
- Login and cross-college visibility
- Newly submitted record visible to assigned officer
- Unknown role cannot view data
- Pending record cannot activate before `Valid` synthetic bank check
- Invalid and Unavailable mock checks do not authorize activation
- Approve/reject release only when request is pending
- Alerts only visible to permitted actors; retry does not duplicate events
- OCR discrepancies displayed as review suggestions, never authenticity verdicts
- Audit trail identifies decisions and timestamps

## Legal / demo disclaimer
All FDRs, institutions, accounts and the bank simulator are synthetic. No actual bank verification, government approval, transfer, refund or release is performed.
