# Integration log

## Applied changes

## Checks


- Reconciled reduced four-agent core, roadmap scope, room names, descriptive science, citation status and Saturday recording schedule. Release blocking remains conditional on a complete passing cycle.
- Checked primary Switch template, Claude hooks, SQLite advisory, Crossref, Wispr and event pages; source code fetch for Switch service returned a cache miss, so installed behavior remains unverified.
- Rewrote the master plan and added a 34-decision weighted record with transparent scoring, evidence and revisit triggers. Scores are subjective estimates.
- Pinned a Crossref-confirmed original and notice as a labeled unrelated retraction example; separated the unresolved negative. Added citation holdout, numeric and counterfactual checks and operational ownership/cost model. Updated docs index.
- Added a draft four-agent one-room core template; retained the five-agent two-room templates as roadmap. Aligned S4, seed references, QC language and freeze time.
- Applied exact per-request decision wording to both core and extended lab templates; clarified core versus optional project-room test setup.

## Final check results

- `python $env:TEMP\check_links.py`: 111 relative Markdown links and anchors outside raw inputs checked; 0 errors. The script checks inline links and images and GitHub-style heading anchors.
- `python $env:TEMP\check_input_links.py` and `python $env:TEMP\check_input_anchors.py`: targeted `rg` extraction from raw inputs found 23 relative targets and 17 heading anchors; 0 missing. Raw plans were not otherwise read or modified.
- `python $env:TEMP\check_plan.py`: 186 distinct catalogue definitions (79 unit, 8 property, 16 contract, 35 integration, 6 golden groups, 12 eval, 20 E2E, 6 EDGE, 4 manual); no unresolved explicit test IDs outside raw inputs; 120 edge rows. Targeted `rg -o` over raw inputs found 99 distinct referenced IDs and 0 missing definitions. Historic reviewer counts describe the earlier reviewed revision, not the current catalogue.
- `rg -n 'U+2014' docs`: no matches, exit 1.
- `python -c` with `yaml.safe_load` over `docs/plan/templates/*.yaml`: 3 parsed. The core template has 4 agents, 4 room agent members and 3 roles. Parsing is not a Switch import test.
- Python summed the schedule table's nonzero time intervals: 2,290 minutes, or 38 h 10 min; each displayed decimal agrees within 0.01 h. There are 34 decision rows.
- Targeted identifier search covered `S0` through `S8`, `S3a` through `S3d`, test IDs, statuses, profiles, room names, prior count and schedule values. Historical review findings retain their original snapshot.
- Primary-source reads: Switch template documentation, Claude hooks, SQLite WAL advisory, Crossref/Crossmark, Wispr free-tier guidance, DTA and WeMakeDevs event pages. A Switch service source fetch returned a cache miss; installed-version authorization remains a required runtime check. The Crossmark original/notice pair is pinned as an unrelated planted example, checked 2026-11-05; cassette retrieval must be recorded during the build.

No application, Switch runtime, model evaluation, real-device, submission-form or clean-clone tests were executed in this documentation integration. The Submit form, installed runtime behavior, actual demand and measured costs remain unverified.
