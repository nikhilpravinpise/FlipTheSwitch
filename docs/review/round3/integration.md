# Round 3 integration

## Changes

## Checks


- Applied booking-only template scope and kickoff; aligned U-C10, observation, decision sensitivities and master-plan numbers. Corrected adapter scope and added adapter citation. Nature exact results remain unverified; LabArchives pricing checked against the vendor.
- Restored the full core room configuration after scoping its agent instructions; aligned the Saturday 00:15 freeze, Friday recording time, decision-record roadmap choices and judging-weight context. Corrected a relative link in the editor log.
- Reconciled architecture with the now-funded, unexecuted certification and fixture; removed obsolete cut-line and optional-agent instructions. Optional template import is outside S4.

## Check results

- `python $env:TEMP\plan_counts.py`: read all 24 requested plan, template and round-three files (343,775 characters); 187 unique catalogue rows, no duplicate or undefined explicit IDs outside raw inputs; 78 weighted totals checked with zero arithmetic errors; 39 decisions; zero U+2014 characters in text files. Raw `docs/inputs/` was not read by this audit.
- `python $env:TEMP\plan_audit.py`: 47 Markdown files; zero broken inline relative links or heading anchors; 120 distinct edge-case rows. Its initial 179-ID pattern omitted the eight P-01 through P-08 property IDs; the expanded `plan_counts.py` result above supersedes that test count.
- `rg -n "\x{2014}" docs`: no matches. `rg -n '38 h 10|68\.5|66\.5|freeze Fri 22:45|allow rule only|reconcile conflicting test text' docs/plan`: no matches.
- Schedule table sum: 2,410 minutes, or 40 h 10 min; 25 productive rows. Decision margin audit: 39 checked, zero errors.
- PyYAML `safe_load` of all three templates: valid; core has four agents, optional lab five, project zero. This is a syntax check, not installed Switch import or behavior certification.
- Primary-source checks: Switch Claude adapter code confirms host-supplied MCP server names are added to permission allow rules; [LabArchives](https://www.labarchives.com/pricing) confirms scheduler academic $35 per user per year and free up to five users and resources; the [Nature preview](https://www.nature.com/articles/533452a) does not expose the exact survey results. Installed behavior, the authenticated form, participant evidence and timing remain unverified. Four web opens and three page finds were used.
- Review files preserve historical counts and earlier reviewer judgments as dated snapshots; current counts are those in the plan. The link checker covers inline Markdown links and generated heading anchors, not remote URL availability or code-formatted future artifact paths.
