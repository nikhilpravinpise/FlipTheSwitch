# Round 5 fixes

**VN-01:** 01 section 1.4 now reserves 180 minutes, including all six attacks and controls, and fails closed on failure or timeout. RSpace academic Team minimum checked against https://www.researchspace.com/pricing on 2026-11-05; seat terms remain unverified.

**VP-01, VP-02, VP-03:** 04 sections 4.3 and 4.6 align certification and baseline, and define viewer recruitment, bounded review and unverified fallback.

**VT-02:** core template kickoff requests the three named role holders.

**VT-01, VT-02, VT-03, VT-04; VP-03:** 08 sections 8.1-8.3 sequence unclaimed probes and claimed personas, fund a 20-minute kickoff and role check and bounded recovery, correct server fallback funding, and reserve viewer work. Added work uses 20 minutes from defect slack; total remains 2,470 minutes and slack is 30.

**VT-01, VT-02, VT-03:** templates README describes fixture order, holder assertions and kickoff recovery.

**VT-01, VT-03:** 03 section 3.2 aligns identity and kickoff handling.

**VT-01, VT-02, VT-03:** 06 EDGE-04 and S4 manual checks specify identity order, role assertions and recovery verification.

**VT-01:** 07 R14 aligns identity order.

**VT-03:** plan README reflects reduced slack.

**VT-02, VT-03, VP-03:** 10 Agent count corrects scope; Schedule records slack and room sensitivity references Saturday review. Subjective scores are retained and weighted totals and margins remain unchanged.

**VP-03:** 09 scoring remains prospective, not an earned result; viewer evidence is subject to the unverified fallback in 04 and 08.

**VT-03, VP-03 propagation:** 06 S4 and 07 R07 cover fresh-room enrollment and holder failure; 08 and 04 fund five-minute outreach before Friday baseline filming and 20-minute Saturday review; 09 section 9.6 marks the viewer-dependent projection unverified if the gate is unmet.

## Checks

- `rg -n "\x{2014}" --pcre2 docs`: no matches. `rg -n '120-minute certification|120-minute installed-runtime|20:15-22:15|50 min defect|50 minutes defect|835 min|645 min|separately budgeted 60' docs/plan docs/README.md`: no stale matches.
- `python "$env:TEMP\round5_check.py"`: parsed all 3 YAML templates with PyYAML; 193 unique test definitions, no duplicates or missing explicitly referenced IDs in the plan/templates/README; 120 edge rows (22 + 12 + 16 + 14 + 10 + 12 + 8 + 6 + 12 + 8); schedule Thu 855, Fri 990, Sat 625, total 2,470 minutes. The checker scans Markdown relative inline links and heading anchors under docs without reading docs/inputs, and checks scheduled row durations. It found one pre-existing broken link: `docs/review/round4/v-technical.md` points to `08-build-schedule.md` in its own directory; the correct relative destination is `../../plan/08-build-schedule.md`. That historical review is outside the assigned edit scope and remains unresolved. Links into docs/inputs were checked for path existence only, not read or anchor-checked, per instruction.
- `python -c "import yaml; print('PyYAML',yaml.__version__)"`: 6.0.3.
- Opened the primary vendor page https://www.researchspace.com/pricing once: academic Team minimum EUR 5,000 / USD 6,000 annually; seat count and additional-user tariffs remain UNVERIFIED. One web fetch used.
- These are static plan checks; installed behavior, role leases, viewer feedback, certification and submission remain unexecuted.
