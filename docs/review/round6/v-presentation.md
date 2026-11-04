## Verdict

**9.2/10. PASS:** score at least 9 and no open blocker or high finding in this scope. This scores the plan, not a built product or a prediction of judge scores. The previous round's only new high and both medium findings are resolved. The authenticated form, installed behavior, voice captures and footage remain unexecuted, but the plan gives bounded procedures and failure paths.

Rubric: demo and branch safety 9/10 x 30% = 2.70; shot realism and viewer validation 9/10 x 20% = 1.80; Wispr evidence 9.5/10 x 20% = 1.90; submission 9/10 x 15% = 1.35; honest judging assessment 9.5/10 x 15% = 1.425. Total 9.175/10, rounded to 9.2. Scores are editorial judgments.

Three largest remaining problems or uncertainties: the proposal-only opener does not explicitly identify routing within its own viewer deadline (VP-01); the recording checklist requests unfunded draft material (VP-02); and the logged-in submission form and local test-user interpretation of the rules are unverified, though the plan labels and bounds them. No edit is required to reach 9 under the stated scoring rule. Recommended exact edits are in VP-01 and VP-02.

The requested `round5/judging.md`, named editor logs and `integration.md` do not exist in this checkout. The available `round5/v-presentation.md` and `round5/fixes.md` were used. Its new findings comprise one high and two medium, all checked below; the inherited JD findings were already checked in that review, and JD-14 was rechecked because it was partly open. This cannot exclude additional findings in an absent file.

## Previous findings status

| ID | Status | Evidence quote or location |
| --- | --- | --- |
| VP-01 (round 5) | resolved | 04 4.3 specifies a "separate 180-minute certification block", separates the 120-minute E2E block, and disables binding on failure or timeout; 08 8.2 budgets the same. |
| VP-02 (round 5) | resolved | 04 4.6 schedules "Friday 20:20-22:15" and identifies 08 as schedule authority; 08 8.2 allocates 115 minutes. |
| VP-03 (round 5) | resolved | 08 8.2 reserves 5 minutes outreach and 20 minutes for review, simplification and retest; on failure or unavailability it says to "submit the best legible cut and mark the viewer gate UNVERIFIED". |
| JD-14, inherited from round 5 | resolved | 04 4.6 now says "Friday 20:20-22:15 (115 minutes, including 5 minutes of viewer outreach and 110 minutes for rehearsal and recording)" and 08 8.2 matches. |

## New findings

| ID | Severity | File and section | What is wrong | Evidence | Exact fix | Reasoning metric |
| --- | --- | --- | --- | --- | --- | --- |
| VP-01 | medium | 04 4.3, proposal-only cut and viewer gate | The proposal-only opening does not explicitly identify Switch as router within the same 20 seconds in which the viewer must identify it. The room identification is scheduled after that point, so the fallback relies on an unstated visual or viewer inference. | The opening only says to show the request and alternative, while the gate requires viewers to "identify Switch as router" by 0:20; the room is identified at 0:20-0:35. | Add a legible opening caption or spoken phrase such as "Switch routes the request" within 0:00-0:20; budget its words and holds, then retain the existing bounded viewer test and fallback. | 20 seconds allowed; explicit room identification starts at second 20. |
| VP-02 | low | 04 4.6, pixel pass | The default recording instructions ask for two draft sentences to be highlighted even though drafts are outside funded booking-only scope. | 04 4.3 says "omit citation, datasets, run, draft and stale claims" for the reduced cut; 4.6 says "highlight two draft sentences". | Make draft highlighting conditional on the separately built expanded draft; for the funded cuts highlight the request, alternative and applicable decision or status instead. | 0 funded draft artifacts; 2 draft sentences requested. |

## Verified facts


- [Event page](https://www.wemakedevs.org/hackathons/switch): a solo participant is allowed, the Wispr side track requests a usage scorecard, and both side tracks can be entered alongside a track. [DTA judging and submission page](https://www.devtoolsacademy.com/hackathons/flip-the-switch) specifies 30/25/25/20 weights and a public repository, short video of a running workflow and reproducible README. A non-running prototype has uncertain eligibility. The [rules](https://www.wemakedevs.org/hackathons/switch/rules) prohibit multiple participation accounts and identities; whether local fictional test accounts fall within that prohibition remains uncertain, as the plan acknowledges. The authenticated form was not inspected.
- [Wispr Insights](https://docs.wisprflow.ai/articles/8760230576-your-usage-tab-track-your-dictation-stats-in-wispr-flow) is desktop-only; total words include desktop and mobile, and heatmap dates use UTC. The lifetime counter difference does not identify project-only work. UTC midnight is 05:30 IST. Unchanged vendor citations were carried forward from prior review; four page opens were used in this round.
- Scorecard arithmetic: booking 24 + 16.25 + 13.75 + 14 = 68; stale 24 + 17.5 + 16.25 + 15 = 72.75; full release 27 + 20 + 18.75 + 17 = 82.75. Shot priority sums are 4/8, 7/8 and 7/8. These are subjective, conditional estimates, not achieved points.
- Expanded shot budgets sum to 20 + 15 + 30 + 25 + 20 + 30 + 15 + 50 + 15 + 10 = 230 seconds. At 120 words/minute, maximum narration plus minimum holds by row is 20 including transitions, 15, 18.5, 15.5, 16, 18, 13, 25.5, 12.5 and 10 seconds. Zero-spare rows demand exact execution; interactions and waiting are unmeasured. Each reduced or proposal cut spans 120 seconds. The optional expanded interval is 115 seconds; overall target duration falls by 110 seconds because other shots change. The plan requires measured rehearsal, legibility review and cuts.
- Seed math: 15:30 plus 15 minutes gives 15:45; a 60-minute slot ends 16:45, before 17:00. B-G by columns 2-8 gives 6 x 7 = 42 wells; C5 is 8 ug/mL, replicate 2. The one-cell correction changes the six-replicate mean by (0.830 - 0.083)/6 = 0.1245. Only people, instrument and booking fixtures are funded; paper, plate and draft shots are explicitly conditional. None were executed.
- Certification allocations total 25 + 35 + 25 + 20 + 15 + 60 = 180 minutes, separate from 120 minutes E2E. Friday baseline is 5 + 110 = 115 minutes. Three 15-25 second clips total 45-75 seconds of source footage, inside an estimated 45-minute capture window. Ten notes x four fields = 40 checks per modality. The 19:00 submission target leaves 4 hours 59 minutes until 23:59. $100 / 4 hours = $25/hour, $2,000 + $500 = $2,500 conditional opportunity, and 10 + 2 + (2 + 10/60) x 20 = $55.33 rounded. All timings and costs remain estimates.
- The 04/08 procedure documents failure, timeout and unexecuted certification as fail-closed; read/propose smoke and the alternative have 20- and 30-minute boxes and a labeled non-running fallback. Wispr capture and form inspection have 45- and 10-minute caps, with uncertainty disclosed on failure. Viewer review has 20 minutes and an unverified fallback. These are procedures, not proof of actual operation.
