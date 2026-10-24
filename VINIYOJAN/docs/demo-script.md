# Three-minute demo storyboard

**0:00–0:20 · Problem.** “A deposit isn't simply a PDF in a folder. It has an owner, a timeline, evidence, and a decision trail. VINIYOJAN makes those parts visible.” Show overview and alerts.

**0:20–0:55 · College journey.** Sign in as `college1@demo.test`. Show portfolio counts, then open **New Submission**. Submit a synthetic PDF of your own or use seeded records. Point out exact fields and restricted upload size.

**0:55–1:20 · Document intelligence.** Open the seeded `DEMO-FDR-1001` record. Present left-hand original document and right-hand structured facts. Explain that extraction assists the reviewer and confidence is never falsely claimed as a bank verification.

**1:20–2:00 · Officer workflow.** Log in as `officer@demo.test`, reopen that FDR. Click **Check synthetic bank registry**; it returns Valid. Flag a different record for discrepancy with a meaningful note; show the change on college view. Explain role-scoped records.

**2:00–2:25 · Time intelligence.** Log in as `admin@demo.test`, run `./scripts/demo-alerts.sh` in a terminal. Show milestone alert text for 7/15/30 days. Run it again: idempotency prevents duplicate sends.

**2:25–2:45 · Traceability.** Open **Audit Activity** as officer. Show distinct upload, bank check and verification events.

**2:45–3:00 · Closing.** “This demo doesn't fake bank connectivity or legal approvals. The ambition is a dependable decision-support workflow with clear room for official clearances, bank integrations and stronger security.”

## Before stage time

- Docker containers healthy; run seed once only.
- Keep browser tabs for officer, admin and college accounts in separate browser profiles or sign in sequentially.
- For a quick PDF upload, use any **synthetic** PDF you created, not real account details.
- Set laptop/browser scale to 90%; pre-open a terminal in the project folder.
- Demo is network-independent after Docker images/dependencies are fetched.
