# Design notes and ERD

```mermaid
erDiagram
  INSTITUTIONS ||--o{ USERS : has
  INSTITUTIONS ||--o{ FDR_RECORDS : owns
  USERS |o--o{ FDR_RECORDS : assigned_officer
  USERS ||--o{ AUDIT_LOGS : acts
  FDR_RECORDS ||--o{ AUDIT_LOGS : tracked
  FDR_RECORDS ||--o{ ALERT_LOGS : triggers
  INSTITUTIONS { uuid id PK string aicte_id string name string spoc_name string email }
  USERS { uuid id PK string email string password_hash string role uuid institution_id FK }
  FDR_RECORDS { uuid id PK uuid institution_id FK uuid assigned_officer_id FK string instrument_number numeric amount date issue_date date maturity_date string status string file_key string file_sha256 string release_status }
  AUDIT_LOGS { uuid id PK uuid user_id FK uuid fdr_id FK string action datetime created_at }
  ALERT_LOGS { uuid id PK uuid fdr_id FK int threshold_days date maturity_date datetime created_at }
```

## Service relationships

```mermaid
flowchart LR
College[College React UI] --> API[FastAPI API]
Officer[Officer React UI] --> API
API --> PG[(PostgreSQL)]
API --> Vault[(Private Document Vault)]
API --> OCR[OCR + risk cues]
API --> Bank[Simulated Bank API]
Scheduler[Daily APScheduler] --> PG
Scheduler --> Alerts[Console Alerts]
```

## Design differentiators

**Explainable verification queue:** capture and display discrete reasons for manual review instead of a fictitious AI authenticity percentage.

**Deposit clock:** track maturity independently of administrative workflow state to stop alerts being suppressed by a stale status.

**Evidence fingerprints:** private storage with random keys, SHA-256 checksums, and audit events on decisions.

**Release-aware workflow:** separate college intent from officer decision; expand to legally required multi-party sign-off before actual release.


