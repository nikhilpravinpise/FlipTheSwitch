## Verdict

**7.0/10** for novelty, evidence and decisions, not a prediction of a judging result. Rubric: prior-art accuracy and restrained claims 2.0/2.5; demonstrable differentiation 1.5/2.5; evidence, source quality and evaluation 1.5/2.5; decision quality and arithmetic 2.0/2.5. All scores are reviewer judgments on a plan, not implemented outcomes.

The three biggest remaining problems are: (1) the distinctive correction-to-release cycle is optional and untested, so the baseline may only show a stale warning; (2) the decision table gives 32 of 33 unrelated decisions the same two vectors without option-specific evidence or sensitivity analysis; (3) contradictory matching and historical-protocol tests can undo the corrected evidence design. The citation audit is incomplete under the 20-fetch budget, so this review cannot certify every link and claim.

To reach 9/10: complete and demonstrate a correction, denied old release, regeneration and fresh authorized decision, or explicitly recast the baseline as a booking prototype with stale detection and reduce novelty claims; reconcile U-C02 and U-S02 with the architecture; specify numeric-claim and paired counterfactual acceptance criteria; replace copied decision vectors with decision-specific evidence, estimates and weight sensitivity; and finish a claim-by-claim citation audit with accessible primary sources. An independently timed same-task comparison is needed before asserting user advantage.

## Previous findings status

| ID | Status | Evidence |
|---|---|---|

| RS-01 | resolved | 01 Related work: "Neither specialist role names nor a scientist in the loop is our invention." |
| RS-02 | resolved | 01 Related work credits Switch payments room for "collaboration, role routing and restricted agents". |
| RS-03 | resolved | 01 USP: "cost, latency and completion benefits are unmeasured"; four/five comparison optional. |
| RS-04 | resolved | 03 3.2 Injection: proposals can be corrupted; six argument/handoff attacks and controls specified. |
| RS-05 | resolved | 03 3.4: 300-character limit "is a size limit, not a privacy guarantee"; source guard optional and bounded. |
| RS-06 | resolved | 03 3.2 requires canonical action, requester, resource and interval or quantity on card, checked transactionally. |
| RS-07 | resolved | 03 3.2 says "one authorized human, not a multi-person quorum"; scoped delegation deferred in 10. |
| RS-08 | resolved | template handbook: "Session-wide provider permission never authorizes another"; requires Allow once. |
| RS-09 | partly | 01 USP makes numeric enforcement conditional on 4/4 tests; template says render structured numeric claims, but 03 3.3 still describes free text and run IDs without a numeric schema. |
| RS-10 | partly | 03 3.5 requires structured library IDs and separates claim support; 06 U-C10 still specifies author-year parsing without specifying rejection and wrong-support tests. |
| RS-11 | partly | 03 3.5 uses token_set_ratio for search, not automatic identity; review negative tests and automatic full-string criteria remain unclear. |
| RS-12 | resolved | 01 USP: "unresolved cases remain unresolved" and general recall is unmeasured. |
| RS-13 | resolved | 06 golden set specifies 40 regression, 24 source-separated holdout, DOI baseline and confusion matrices, with no population recall claim. |
| RS-14 | resolved | 01 P4 quotes 35 fabricated plus 64 erroneous among 176, 56.25%, and acknowledges discrepancy. |
| RS-15 | resolved | 01 Related work credits build systems and PROV-O; no new provenance algorithm claimed. |
| RS-16 | partly | 03 3.8 preserves performed version and distinguishes copyedit, recipe and critical change; 06 U-S02 still demands old runs become stale on a new protocol release. |
| RS-17 | resolved | 03 3.5 makes retraction snapshots draft parents and requires a fresh check within 24 h for finalization. |
| RS-18 | partly | 03 results packet names input, recipe source, lockfile, parameters and reproduction command, but ZIP is optional and core has no reproduction artifact. |
| RS-19 | resolved | 01 Related work credits workflow-run RO-Crate and treats base export as optional, with no unvalidated compliance claim. |
| RS-20 | partly | 03 3.6 restricts to descriptive statistics; 04 opening still calls concentrations sub-inhibitory without MIC evidence. |
| RS-21 | partly | 06 6.5 requires reordered, missing and reversed evidence tests, but demo 04 only corrects one cell and has no paired expected narrative criterion. |
| RS-22 | partly | 03 results packet includes exclusions and runtime versions, but rejected analyses and failed attempts are not clearly captured. |
| RS-23 | partly | 01 P9 cites voice ELN prior work and says no speed proof; no explicit voice/type error comparison is scheduled. |
| RS-24 | resolved | 01 validation separates active decision, model wait and PI wait, and compares the same task with existing tools. |
| RS-25 | partly | README and 04 make release claims conditional and offer honest stale-only fallback; the distinctive release loop remains optional, so substantive demo risk persists. |
| MK-01 | resolved | 01 P1 uses 44.3% from 2018 FDP and excludes specific booking savings. |
| MK-02 | resolved | 01 P3 distinguishes 84% any use, 62% research use, and missing guidelines and training. |
| MK-03 | resolved | 01 P2 removes causal attribution to bad records. |
| MK-04 | resolved | 01 P4 links JMIR primary and limits scope to six GPT-4o mental-health reviews. |
| MK-05 | resolved | 01 P5 calls Crossref a limited-coverage signal, not retraction frequency or clearance. |
| MK-06 | resolved | 01 P6 identifies secondary reporting and excludes savings claims. |
| MK-07 | resolved | 01 P7 describes one sharing case and drops the unsupported area figure. |
| MK-08 | resolved | 01 P12 gives 155 respondents, 21% academic, from vendor primary survey. |
| MK-09 | resolved | 01 P11 names Calira and LabArchives small-lab scheduling and requires comparison. |
| MK-10 | resolved | 01 story explicitly labels fictional scenario and target-lab demand UNVERIFIED. |
| MK-11 | partly | 01 job validation calls PI-only a demo policy, measures PI wait, and asks for real approver and fallback; actual user need remains unvalidated. |
| MK-12 | resolved | 01 USP names local Mattermost and 10.5-minute onboarding; existing-chat adoption is a hypothesis. |
| MK-13 | resolved | README says purchase request places no order and receipt is required for stock; 04 tests 12 mL refusal and 22 mL hold. |
| MK-14 | resolved | 01 USP rejects universal detection and separates metadata from claim support. |
| MK-15 | partly | 01 USP conditions numeric enforcement on four tests; 03 draft schema does not yet require structured metric/value binding. |
| MK-16 | partly | README conditions release block on implementation and testing, avoiding false claim; actual release gate remains non-core. |
| MK-17 | partly | 03 3.6 removes inference for synthetic single plate; 04 opening retains unsupported sub-inhibitory framing. |
| MK-18 | resolved | README limits core to one room; 01 excludes human-subject data and says policy is not confidentiality guarantee. |
| MK-19 | resolved | README confines binding core action to booking and acknowledges helpers write observations and drafts. |
| MK-20 | resolved | 01 USP says cost, latency and completion benefits of narrow agents are unmeasured. |
| MK-21 | resolved | 01 competitor table and gap analysis include Scispot specialist agents, governed data and approved work. |
| MK-22 | resolved | 01 competitor table describes Sapio agentic ELN and avoids passive-forms category claim. |
| MK-23 | resolved | 01 Edison row includes Slack/Teams/email collaboration and mid-run steering. |
| MK-24 | resolved | 01 Cenevo row includes agents, human review and MCP access. |
| MK-25 | resolved | 01 Calira row acknowledges AI workflows and requires conflict comparison. |
| MK-26 | resolved | 01 comparison acknowledges Slack agents and Teams approvals. |
| MK-27 | resolved | 01 Zotero row links its existing retraction warnings and limits proposed advantage. |
| MK-28 | partly | 01 Benchling row acknowledges traceable AI output and confirmation; source link is generic and the current specific claims need verification. |
| MK-29 | resolved | 01 RSpace row states EUR5,000/USD6,000 managed minimum and distinguishes self-hosted. |
| MK-30 | resolved | 01 LabArchives row gives $35/user/year and free small-team tier. |
| MK-31 | resolved | 01 Quartzy row says $50/month for three users, not ten. |
| MK-32 | resolved | 01 Elicit row acknowledges team live collaboration rather than single-user category. |
| MK-33 | partly | 01 corrects scite, Undermind and Slack prices and marks Paperpal unverified, but price source freshness/access is not fully independently confirmed. |
| MK-34 | resolved | 01 rows acknowledge sharing, Consensus Teams and ResearchRabbit+ retraction filters. |
| MK-35 | resolved | 01 Related work credits co-scientist feedback; PI-only explicitly labeled demo policy. |
| MK-36 | resolved | 01 uses official product sources and says funding does not establish task fit. |
| MK-37 | resolved | 01 TCO lists provider, hosting, backups and operator time, explicitly unmeasured. |
| MK-38 | resolved | README distinguishes 2,000-word warning from 5,000-word Windows block and notes redeemed Pro. |
| MK-39 | partly | 01 validation compares task and records active, model and PI waits; inventory and analysis claims remain conditional on current data and implemented measurement. |
| MK-40 | partly | 03 3.5 adds retraction freshness and 03 3.8 preserves historical protocol; 06 U-S02 conflicts with latter. |
| MK-41 | resolved | README labels test catalogue planned and scores as conditional estimates. |
| MK-43 | resolved | 01 long-term hypothesis calls for separate Switch license assessment before paid Switch-dependent hosting. |
| MK-44 | resolved | 01 USP allows card or supported text and conditions guarantees on S2/S3 runtime tests. |
| MK-46 | resolved | 01 1.3 replaces categorical quadrant with documented overlap and not-established cells. |

## New findings

| ID | Severity | File and section | What is wrong | Evidence | Exact fix | Reasoning metric |
|---|---|---|---|---|---|---|

| VN-01 | high | README What is new; 01 1.3-1.4; 04 script | The strongest proposed distinction is conditional on an optional release gate; the baseline may demonstrate only a stale badge and booking. This is honest wording but weak evidence for impact and differentiation. | README: "Otherwise demonstrate stale detection only"; 04 3:10-3:25 permits "stale draft detected". Scispot already advertises specialist agents, governed state, approved work and review: [vendor](https://www.scispot.com/scibot). | Prioritize a minimal tested release record and film corrected input, denied stale release, updated output and fresh authorized decision. If infeasible, retain the narrow stale-detection claim and do not imply the release consequence is shown. | Four causal steps, all 4 required for full claim; current plan makes at least 2 conditional. This is a checklist, not measured performance. |
| VN-02 | high | 10 decision record | Calculations are correct, but generic identical vectors effectively hard-code choices and cannot justify unrelated tradeoffs. The 70/15/15 utility split is an asserted preference, not derived from the published judging weights; hours and risk are ordinal proxies without anchors. | 32/33 decisions reuse 8/8/7/8/8/8 vs 7/7/7/7/4/5, every such gap 1.575. For that gap, judging contributes 0.525, hours 0.600 and risk 0.450; the two non-judging terms contribute 1.050, or two-thirds. The [event page](https://www.devtoolsacademy.com/hackathons/flip-the-switch) is not evidence for 70/15/15. | Replace cloned scores with explicit option-specific evidence and hour/risk anchors, identify correlated or dominated criteria, and calculate a plausible weight/score sensitivity or use unscored decision rules where evidence is missing. Clearly label the non-judging split as builder preference. | Audited 66 option totals across 33 rows: 0 arithmetic mismatches. A 1-point change in a single H or R score moves a total by 0.15; scoring precision to 0.001 is not measurement precision. |
| VN-03 | high | 01 Related work; 03 3.5; 06 U-C02 | The conservative verifier plan conflicts with a unit test that still accepts token-set ratio 90+, recreating the prior false-match hazard. | 03 3.5 limits fuzzy scoring to retrieval and sends subsets to NEEDS_REVIEW; 06 U-C02 says "Title match at token-set ratio 90+". | Rewrite U-C02 to require exact normalized full title or a separately calibrated full-string rule; add subset, negation and mismatch cases that cannot automatically verify. | One contradictory acceptance test can pass a 100-scoring subset match; require 0 automatic passes on the specified adversarial subset cases. |
| VN-04 | high | 01 Related work; 03 3.8; 06 U-S02 | Protocol history remains internally inconsistent. Treating all older runs as stale on release conflicts with preserving the performed version and avoiding numerical reruns for copyedits. | 03 3.8 states "Protocol copyedits cause zero numeric reruns"; 06 U-S02 says a new protocol marks old runs stale. | Split historical validity from current-project suitability; update U-S02 to cover copyedit, changed computation and critical scientific change with explicit REVIEW_REQUIRED and preserved performed version. | Three cases, 3/3 expected outcomes required; one existing generic assertion cannot distinguish them. |
| VN-05 | medium | 01 P9 and 1.2 | Some exact source claims remain unsupported by their cited page or inaccessible in this audit. The Benchling AI page does not visibly state mandatory confirmation for writes; the AI Scientist v2 v1 paper does not contain the word "withdraw"; the DOI for voice ELN redirects to an ACM page inaccessible to this reviewer. These access limitations do not prove the claims false. | [Benchling AI](https://www.benchling.com/ai); [AI Scientist v2 v1](https://arxiv.org/html/2504.08066v1); [voice DOI](https://doi.org/10.1145/2948992.2948998). | Add a direct primary page or document passage supporting each precise claim, or mark it unverified and remove the unsupported detail. Preserve the prior-work citation if independently identified. | Three exact claims require three independently inspectable supporting passages; 0/3 were established from these linked pages in this audit. |
| VN-06 | medium | 01 Related work; 03 3.3 and 3.5; 06 6.5 | Numeric grounding and counterfactuals remain underspecified despite a sound 4/4 claim gate. The core recipe contains no CI or p, while the draft data model still allows arbitrary prose with run IDs. Reversed-evidence tests have no explicit output comparison or independent expected result. | 01 requires altered n, effect, CI and p; 06 says core has no inferential CI or p; 03 draft_section stores text and run IDs. The [counterfactual paper](https://arxiv.org/html/2610.04915v1) tests whether answers track withdrawn or reversed evidence. | For the shipped descriptive path require run ID, metric path, value, units and rounding, render from run JSON, and compare paired original/reversed fixture outputs against independent goldens. Mark CI and p N/A for that path and never count N/A as passed. | Report applicable tests as k/n with actual denominators; 4/4 is impossible for a two-metric-only path unless separate supported CI and p fixtures exist. |
| VN-07 | medium | 04 opening; 01 USP | The demo still frames concentrations as sub-inhibitory without an MIC measurement, although the rest correctly says synthetic descriptive output supports no efficacy inference. | 04 opening: "at sub-inhibitory concentrations"; 03 3.6 says technical wells and descriptive statistics only. | Say "across illustrative concentration levels" and omit sub-inhibitory or sub-MIC everywhere unless a separately measured MIC is provided. | One unsupported biological qualifier can survive all numerical tests; acceptance is 0 unsupported MIC or efficacy assertions in the demo. |
| VN-08 | medium | 01 1.1, 1.2 and Related work; README citations | An exhaustive link-and-claim audit has not been achieved. The three scoped files contain 65 distinct external URLs, exceeding the 20-fetch/search budget before even allowing retries. Prior-round access reports are useful leads but cannot establish current content or every exact claim. | URL extraction from all three files; this review used 20 opens including duplicate attempts, and some returned access errors. | Run a later, separately budgeted claim-level audit of every remaining citation, recording final URL, access result, exact supporting passage, date and unsupported claims; replace or label inaccessible citations. | 65 unique external URLs vs at most 20 permitted fetches: at least 45 cannot receive independent individual fetches in this round; duplicate attempts increase the actual remainder. |

## Verified facts

- The [Switch payments room](https://docs.switchagents.ai/switch-rooms/building/payments-room) is an existing role-routed approval example; the [Scispot page](https://www.scispot.com/scibot) advertises governed context, specialist agents and human review. These sources support the plan's restrained combination claim, not uniqueness or superior performance.
- [Workflow Run RO-Crate](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0309210) records workflow provenance; the proposed base export is not proof of profile compliance. [Counterfactual evaluation](https://arxiv.org/html/2610.04915v1) studies evidence withdrawal and reversal.
- The [FDP survey](https://thefdp.org/wp-content/uploads/FDP-FWS-2018-Primary-Report.pdf) reports the 44.3% as an average of principal investigators' estimates for federally funded project research time. The [CU case](https://www.cu.edu/controller/i-e-awards/past-submissions/cu-ie-submission-establishing-multi-departmental-shared) lists training, scheduling, repair and contamination concerns. Neither estimates LabQuorum savings.
- [LabArchives](https://www.labarchives.com/pricing) lists the academic scheduler at $35/user/year and a free tier for at most five users and five resources. Ten paid seats at list is 10 x $35 = $350/year before discounts. [Scite](https://scite.ai/pricing) shows $12/month annual-billed Basic with 250 MCP credits and $40/month annual-billed Pro with 2,500 credits.
- Arithmetic checked: (35 + 64)/176 = 56.25%; 84% - 62% = 22 percentage points; 155 x 21% = 32.55, approximately 33; 10 people x 2 approvals x 30 seconds = 10 minutes/day; 2 hours/month x $25/hour x 12 = $600/year; 1 of 5 agents = 20%; 23:59 minus 19:00 = 4 h 59 min; IST to UTC subtracts 5 h 30 min, so 23:59 IST = 18:29 UTC. These are arithmetic checks, not independent verification of all cited inputs.
- Decision-table audit: 33 rows and 66 option totals checked with the stated formula; all match. Name and demo scenario vectors compute 7.615 and 7.300; the repeated vectors compute 7.825 and 6.250. The formula's effective coefficients are 0.21, 0.175, 0.175, 0.14, 0.15 and 0.15, summing to 1.00.
- Audit coverage: all 25 research findings and all 22 market blocker/high findings were assessed; all 22 market medium findings were also assessed. See the table for individual evidence. Status assesses the written plan, not proof of implementation. Vendor and paper facts above are from accessible source content; the citation audit is partial, not an assertion that remaining sources are broken.

