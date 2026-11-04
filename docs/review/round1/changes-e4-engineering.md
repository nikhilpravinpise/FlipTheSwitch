## Applied

- EN-01-03, EN-46-47, SW-01/02/14/16/19/21: reforecast and gate the critical path in 08 sections 8.1-8.3. Estimates are assumptions, not measured velocity.
- EN-04, EN-06-23, EN-25/27/28/30/32/33/38-42/45, SW-03/05/06/09-11/15/17/18/20: repair test contracts and add targeted tests in 06.
- EN-28/31/34-37, SW-10/12/14/17: correct edge handling and test links in 07.
- Sources checked: SQLite permits one writer under BEGIN IMMEDIATE and documents its WAL-reset bug; Claude documents deny precedence and hook failure behavior; SciPy documents Dunnett RNG and assumptions; NIST confirms Wilson intervals. These resolve the proposed race, fallback, inferential and reliability choices in favor of the findings.

## Rejected

- EN-38 SHOULD: accept Wilson intervals and pass^3; the proposed 28 trials are conditional on observed latency within 3 h, with 15 core trials otherwise. This preserves the 1 h 55 min defect reserve.
- EN upgrade REJECT-IF-SHORT-ON-TIME: defer general container execution, second provider, Telegram and extra rooms; estimated 6-12 h exceeds available 1 h 55 min defect slack.
- EN-01/02 schedule proposal: adopt a reforecast rather than copying the suggested 37 h verbatim; its starting checkpoint and task allocations conflict with our explicit 38 h 40 min blocks. Estimates remain unvalidated.

## Identifier changes

- Added I-23 through I-35, 13 planned integration IDs. No existing ID removed or renamed. Counts: 186 unique planned test IDs; 120 edge-case rows. Planned IDs are not proof of executable coverage.

## Requests for other owners

- `README.md`: replace 45-hour/full-scope claims with: "The Thu 00:20 reforecast is 38 h 40 min of scheduled work, including 1 h 55 min defect slack and 30 min submission; rebase on actual start. Full scope is estimated at 71-109 h."
- `02-product.md`, `04-demo.md`, templates: replace full-scope MVP with: "One room: labops, scout, pi-desk and analyst; one booking request, one pinned citation fixture, one synthetic CSV, descriptive figure and small stale check. Protocol release, inventory orders, general bench parsing, external rooms and other providers are roadmap."
- `03-architecture.md` approval contract: add: "A native card is an externally enforced provider boundary, not an authenticated ledger receipt. Require effective runtime checks; otherwise disable commits or use a separately tested steward. Direct same-OS-user invocation is outside this boundary." Add bounded canonical decision fields, recompute hash in the transaction and reject changed fields; show them untruncated on the actual card.
- `03-architecture.md` hook and doctor: add: "Unknown, auto and bypass modes deny; use supported `onFailure: block` and test missing executable, crash, malformed output and timeout in the installed Console process. Check effective managed or local config and revision; unknown fails."
- `03-architecture.md` store and stale: add: "Record SQLite library version; use fixed WAL version per SQLite advisory or rollback journal. Synchronize race before `BEGIN IMMEDIATE`; stage files and reconcile DB/file/outbox crash boundaries."
- `03-architecture.md` and `04-demo.md`: replace biological ANOVA/Dunnett interpretation with: "One synthetic plate contains technical wells only; show descriptive summaries and provenance, no biological p-value or significance. Verify the exact 42-well dose mapping and one-cell correction with independent goldens."
- `04-demo.md`, `05-wispr-flow.md`, `09-submission-and-risks.md`: replace late screenshot timing with: "Capture final Wispr Insights by Saturday 18:30 IST, before the 18:30-19:00 website Submit window." Select future valid booking times for the actual recording clock.
- `02-product.md`, `03-architecture.md`, templates: replace external-data confidentiality claim with: "Keep external collaborators out of internal rooms; all demo data is synthetic. Participant checks and query-length limits do not intercept every Switch attachment or establish confidentiality."
- `03-architecture.md` and `04-demo.md`: if the steward branch is selected, replace binding-card claims with: "A trusted enrolled human sends a revision-bound decision; native cards are provider consent only. Run identity, replay, expiry, takeover, gap and outbox tests before enabling mutation." Budget 3-5 h by removing optional work.

## Open questions

- S0 path B's exact pinned deployment commands and health endpoint, actual provider/tool inventory, effective settings, submission fields, per-test runtime and machine capacity remain UNVERIFIED until the builder executes the spikes.
- The plan specifies the 42-well check but the actual seed mapping and correction oracle require reconciliation by the seed/template owner before scientific output is built.
- Some existing catalogue entries describe stretch features and remain planned, not runnable. Unrelated files may retain conflicting scope, demo times and authority claims until owners apply the requests above.

