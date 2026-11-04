## Verdict

**9.1/10, passes** the plan-level bar: no open blocker or high finding was found in the available preceding review. Rubric: approval boundary and certification 3.8/4; schedule and fallbacks 1.8/2; traceability and consistency 1.6/2; technical grounding and arithmetic 1.9/2. This score assesses the written plan, not installed behavior.

The three biggest remaining issues are the six-test discrepancy in the test pyramid (VT-02), the omitted break in the late-block explanation (VT-01), and the unmeasured installed approval and kickoff behavior. The latter is a delivery risk rather than an open plan defect: 03 section 3.2 and 08 sections 8.1-8.2 define evidence, time boxes, failure conditions and proposal-only fallback.

No edit is required to reach 9 under the stated rule. To remove the remaining identified discrepancies, make both exact edits in VT-01 and VT-02. The brief names round5/switch.md, engineering.md, research.md and editor logs, but this checkout instead contains round5/v-technical.md, v-novelty.md, v-presentation.md and fixes.md. All four findings in the available prior technical review, including both medium findings, were checked. The mechanism-related VN-01 is also checked below. Round 1 originals exist and their prior-round tracking is in round4/v-technical.md; the named round 5 originals cannot be independently assessed as files that do not exist.

## Previous findings status

| ID | Status | Evidence quote or location |
|---|---|---|

| VT-01 (round5) | resolved | 08 S1: “Before claiming, record unclaimed Maya on open helper and unclaimed PI on owner-scoped pi-desk. Then claim and re-enroll both”; S4 provisions them first. |
| VT-02 (round5) | resolved | Core template kickoff asks “scout as librarian, labops as bench-manager, and pi-desk as approver”; 08 S4 asserts `!roles` holders and disables binding if unresolved. |
| VT-03 (round5) | resolved | 08 S4 inspects kickoff card and server log, supplies a fresh-room human-message recovery within 20 minutes, and disables binding if unresolved. |
| VT-04 (round5) | resolved | 08 S0 says fallback “requires a separately funded 60-90 min reforecast”; 8.3 states the 30-minute slack cannot fund it. |

| VN-01 (round5, mechanism certification) | resolved | 01 section 1.4 now reserves 180 minutes including I-36 through I-41 and legitimate controls, with binding disabled on failure or timeout; 08 section 8.2 matches. |

## New findings

| ID | Severity | File and section | What is wrong | Evidence | Exact fix | Reasoning metric |
|---|---|---|---|---|---|---|

| VT-01 | medium | 08 section 8.1, late-block accounting | The introductory allocation claims the 115-minute late block reserves four productive allocations totaling only 95 minutes, omitting its 20-minute break. | 20 + 30 + 30 + 15 = 95; section 8.2 correctly shows a 20-minute break from 17:20 to 17:40. | Say the 115-minute elapsed block contains 95 productive minutes and a 20-minute break; preserve the 2,470-minute productive total. | 115 - 95 = 20 minutes; no additional productive slack exists. |

| VT-02 | medium | 06 section 6.3 test pyramid and section 6.4 catalogue | Two totals for the same planned test inventory disagree by six; the top table omits the later six integration cases. | Section 6.3 says 187 planned test IDs; section 6.4 says 193 = 79 + 8 + 16 + 41 + 6 + 12 + 26 + 5. | Update the affected category and total in section 6.3 to match the enumerated 41 integration cases and 193 planned IDs; retain their planned status. | 193 - 187 = 6; 79 + 8 + 16 + 41 + 6 + 12 + 26 + 5 = 193. |

## Verified facts


- The changed role-taking kickoff and recovery are consistent with Switch's leased role behavior and the reported [Mattermost kickoff issue](https://github.com/sandbox-quantum/switch/issues/1158). The issue reports a macOS reproduction, not proof of failure on the planned Windows installation. S4 tests the actual installation and caps recovery.
- [Switch's Claude adapter](https://raw.githubusercontent.com/sandbox-quantum/switch/main/console/packages/agent-providers/src/claude/claude-adapter.ts) defines once, session and decline decisions and warns that bypass can auto-approve ordinary tools. The plan's actual hook precedence and authorization must be certified on the installed version; no live certification was performed here. Prior round source inspection covers the bridge actor-to-identity and authorization path; its source page was unavailable on this recheck.
- All three template files parse as YAML. The previous source audit compared Console's [template document parser](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/console/apps/switch-console-desktop/src/main/core/agent-templates/template-document.ts), the server template language and upstream examples; no field-family error was reported. The current changed kickoff is a top-level string for a single-room template. Parsing YAML alone does not prove a successful Console import or provisioning; the pinned source page was unavailable during this recheck, and S4 remains decisive.
- Independent static inventory found 193 unique catalogue definitions and no duplicate or unresolved explicit test IDs in the plan and templates: 79 unit, 8 property, 16 contract, 41 integration, 6 golden, 12 eval, 20 E2E, 6 EDGE and 5 manual. The edge catalogue has 120 rows: 22 + 12 + 16 + 14 + 10 + 12 + 8 + 6 + 12 + 8. Scoped explicit edge identifiers resolve; manual prose checks are not executable IDs.
- The scheduled productive blocks total 855 + 990 + 625 = 2,470 minutes = 41 hours 10 minutes. The Saturday 115-minute elapsed block includes 95 productive minutes and 20 minutes break. Certification is 25 + 35 + 25 + 20 + 15 + 60 = 180 minutes; the submission contingency is 4 hours 59 minutes. The server fallback requires a fresh funded reforecast.
- The round 5 technical audit reported checking 78 weighted formulas and 39 margins; the decision scores were retained by the round 5 fix log. This review rechecked the changed schedule and test-count metrics above, but did not independently recalculate every inherited decision formula. The previous round's numerical audit is therefore inherited evidence, not a fresh complete arithmetic certification.
