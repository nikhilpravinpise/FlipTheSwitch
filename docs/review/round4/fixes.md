# Round 4 fixes

VN-02, VN-03: 01 sections 1.2 and opening correct the price and ledger scope. Primary source checked: https://www.researchspace.com/pricing (2026-11-05); the page states the minimum but no seat terms.

VT-01, VT-03: templates/README, 02 section 2.3 and 06 E2E setup align core-only S4 and shared scenario state.

VP-01: 04 sections 4.2-4.3 and templates/seed-data remove the unfunded protocol from AR-0042; protocol remains roadmap only.

VT-04: 03 injection guard and 06 mandatory I-36 through I-41 define six booking attacks, legitimate controls, cards, transactions and ledger outcomes; missing or failed cases disable binding.

VP-02, VP-03, VP-05, VP-06: 04 cuts, 05 sections 5.6-5.7, README and 09 checklist use request-scoped status, conditional clips, optional links and a 10-word draft shot with two-second interaction.

VT-02, VT-04, VP-03, VP-04: 08 sections 8.1-8.3 allocate stub preparation, 60 minutes for attacks/controls, 45 minutes voice, a 20-minute smoke gate and 30-minute fallback; 04, 07 and 09 describe failure and scoring. The 70-minute blocker-fix block and 5 minutes of baseline are cut; arithmetic totals 2,470 minutes, including 50 minutes defect slack.

VN-01: 10 Method and High-impact sensitivity bounds document subjective anchors, low/base/high ranges, 100% weight perturbations, flip thresholds and overlap choices; gates override scores. Existing inputs and weighted totals remain unchanged.

Schedule decision: 10 Schedule updates contingency 5 to 4, total 5.60 and margin 2.20; 03 certification duration updated.

Checks (2026-11-05): `python "$env:TEMP\round4check.py"` scanned docs excluding inputs: 0 em-dash files, 193 defined test IDs and 0 missing plan references, 120 edge rows, all 3 YAML templates parse; link audit found 1 pre-existing broken link in docs/review/round4/v-technical.md to 08-build-schedule.md, outside the owned plan/README and requested fix-log scope. No input contents were read, so their internal links and characters were not checked.

Schedule verification: a Python regex over 08 table summed Thu 835, Fri 990, Sat 645 = 2,470 minutes; all productive row durations match their clocks. Certification 25+35+25+20+15+60 = 180; late block 20+30+50+15 = 115. Smoke fallback moved to Saturday 09:00 before final takes and the corresponding clean-room 30 minutes moved into the late block. `rg -n` located review findings and propagated references; primary source fetched once via `web.open` at the RSpace URL above. Runtime gates, clips and submission remain unexecuted.
