# 9. Submission, prizes, judging, risks

Back to the [master plan](README.md). Event facts are in [`../flip-the-switch-hackathon.md`](../flip-the-switch-hackathon.md).

## 9.1 Prize stacking

| Prize | Evidence we submit | Award signal | Priority |
| --- | --- | --- | --- |
| **Track 1: Best Business Workflow** | Real room workflow, human gate, completed outputs, reproducible repo, video | $2,000 cash (main page) | Highest |
| **Code with Wispr** | Voice used for prompts, agent instructions, docs and a voice-first product feature; Insights screenshot; voice log | $500 cash | High: nearly all effort compounds with the build |
| **Best Blog** | First-timer guide to Switch approvals with exact steps and screenshots | AirPods 5: one advertised on main page; DTA differs | High after the core works |
| **#HowISwitch** | Short honest clips and the final video | Logitech keyboards: 5 advertised on main page; DTA differs | Medium, low effort |
| Core Contribution | Skipped solo ([08](08-build-schedule.md#84-core-contribution-pr)) | $100/PR | Skip solo for this submission |

The [main event page](https://www.wemakedevs.org/hackathons/switch) currently lists 20 random project swag recipients and a certificate for every submission; its 20 core-PR prizes conflict with its own judging section and the [DTA page](https://www.devtoolsacademy.com/hackathons/flip-the-switch), which say 10. Count UNVERIFIED. A solo core PR is skipped: at a 4-hour cap even a certain $100 is at most $25/hour before costs.

Named cash opportunity: $2,500 for Track 1 plus Wispr, conditional on winning and on legitimate stacking (the event allows Wispr alongside a track and a blog alongside a workflow; it does not guarantee every combination). We do not enter the second workflow track with the same build.

## 9.2 Submission (website Submit form)

Submission is through the **Submit button on the hackathon website**. During S8, the builder manually inspects the authenticated form for 10 minutes without submitting a dummy entry; the builder also submits manually ([event rules](https://www.wemakedevs.org/hackathons/switch/rules)). Record actual field names, required flags, accepted formats, video/hosting limits and side-track mapping; the [public route](https://www.wemakedevs.org/hackathons/switch/submit) exposes a loading shell, so those details remain UNVERIFIED. Put direct evidence links in the README if no matching form field exists:

- [ ] Public GitHub repo, logged-out accessible, MIT or Apache-2.0 license, no vendored Switch code (Switch's license includes a Commons Clause)
- [ ] README (outline below) naming every agent, provider, room and bridge and how Switch is used
- [ ] Demo video link (YouTube, public or unlisted, verified logged out) plus a copy as a GitHub release asset
- [ ] Wispr Insights final screenshot (`docs/wispr-insights-final.png`) by 18:00 after last dictation; attach/check by 18:30. Keep baseline and earlier complete backup; link three authentic build clips and voice log
- [ ] Blog link and #HowISwitch post links
- [ ] Choose Best Business Workflow and include Code with Wispr / Best Blog evidence using the controls actually found in S8; do not assume track selectors exist
- [ ] Clean-room reproduction done (M-03); CI green; `docs/test-evidence.md` current
- [ ] gitleaks clean; no em dash anywhere; no secrets or private URLs in video or screenshots
- [ ] Synthetic data, role-play and any replay labeled
- [ ] Submitted by Saturday 19:00 IST; confirmation screenshot saved; every link re-checked in incognito afterwards

## 9.3 README outline

Target opening, publish only after the stated behaviors pass:

> # LabQuorum
> Request lab work in a Switch room. Approve the exact request. See what becomes invalid when data changes.
>
> A student asks `@labops` for an instrument; it proposes an available slot and hands the request to `@pi-desk`. Switch checks who may answer and records the decision. LabQuorum rechecks the request revision and lab rules before committing. Corrected data marks dependent outputs stale; release is refused and a new decision required only if that path passed its tests.
>
> Watch the demo, inspect a sample output, or follow the tested Windows setup. Data are synthetic; the builder plays both labeled personas. Cached scholarly responses are labeled with retrieval dates.

First screenful or one click: refusal/acceptance GIF, video, sample output folder and one tested reproduction path. Include installed versions, provider and API prerequisites, measured setup time, rooms, bridge, exact first message, expected output, current data/run/draft references and shipped/simulated/roadmap labels. Attribute routing and permission primitives to Switch; LabQuorum adds lab state and evidence-version consequences. Link test evidence, limitations, voice reel and full Insights image; put planner provenance in acknowledgments. Budget 0.5 hour; a reader must find one current output and its inputs within 60 seconds. Metadata checks establish identity/retraction signals, not whether a claim is supported.

Summarize five installed-version invariants with actual traces: PI accepted, student refused with no change, changed revision rejected, session choice followed by a fresh card, disconnect produced no offline commit. This 0.5-hour summary reuses required tests; 5/5 pass before advertising the native gate. If the steward is selected, replace all card-as-decision wording with the authenticated revision-bound message and its own passing tests.

## 9.4 Blog (Best Blog: clarity for a first-time Switch user)

Title: "One corrected CSV invalidated our results: a first-time Switch build with Wispr Flow." Spend 1.5 hours in the existing blog block. Open with the actual input hash, correction, stale reason and refused release only if demonstrated; otherwise describe stale detection accurately. Show the original human decision, then a bounded reproducible path: installed Console/Mattermost/provider prerequisites, claimed PI identity, helper and gate, project MCP and permission settings, proposal, wrong-person refusal and PI decision. Distinguish routing, provider consent and application invariants. Include only failures actually reproduced, with versions, red/green output and recovery; link the 0.5-0.75 hour rejection/recovery artifact and the three voice-build examples. Publish a copy in `docs/blog.md` and link the public article. Test: one newcomer completes the bounded task and distinguishes silence, unavailable session and refusal; if unavailable, report only a clean-room transcript, not independent validation.

## 9.5 #HowISwitch

Reuse 20-30 seconds of genuine refusal, accepted decision and stale-release refusal, if implemented. Spend <=15 extra minutes; side-award odds are unknown. Draft for the builder to post: "A corrected CSV should invalidate its figure and draft. LabQuorum shows the change and refuses release until a new run and PI decision. Switch carries the agents, handoff and human approval in team chat. Synthetic demo, built with Wispr Flow. Demo: <link> Code: <link> #HowISwitch". Remove any unproven clause. If an already-reachable participant is available after the core is green, spend <=0.5 hour asking them uncoached to find a protocol, approver and figure provenance; record success, active time and wait time separately. One labeled observation is not a demand estimate.

## 9.6 Judging scorecard self-assessment

These are subjective projections, not measured marks or winning probabilities. [Published rubric](https://www.devtoolsacademy.com/hackathons/flip-the-switch): 30/25/25/20. Planned test IDs are not passed tests; every improved score requires a link to actual footage, output, test result or clean-clone transcript.

| Criterion | Current plan /10 (weighted) | Improved /10 (weighted) | Evidence gate and reason |
| --- | --- | --- | --- |
| Use of Switch, 30% | 8.0 (24.00) | 9.0 (27.00) | Handoff, wrong-person refusal, accepted decision and actual workflow stops without Switch; platform primitives credited. |
| Technical execution, 25% | 6.5 (16.25) | 8.0 (20.00) | Fixed fixtures, pinned versions, meaningful tests passed, real E2E and clean clone. Counts of planned tests alone earn no points. |
| Creativity and impact, 25% | 6.5 (16.25) | 7.5 (18.75) | Demonstrated stale-release block and new decision plus one labeled usability observation; no assumed ROI. A stale badge alone supports less. |
| Presentation, 20% | 6.0 (12.00) | 8.5 (17.00) | Early Switch proof, legible upload, honest timing/fixture labels, runnable README and current output. |
| Total | **68.50/100** | **82.75/100** | Improved score is conditional on every gate, not a forecast of an award. |

Reduced-build independent estimate: Switch 7.5, technical 6.5, creativity 5.5, presentation 7.0 = 22.5 + 16.25 + 13.75 + 14 = **66.5/100**, assuming real decision and stale detection but no release block or user observation. A three-agent build can score higher if it proves the full gates; agent count is not a rubric. Retraction beat scores 4/8 versus refusal/commit 7/8 and stale block/new decision 7/8 on Switch specificity, consequence, novelty and clarity (0-2 each); allocate screen time accordingly.

## 9.7 Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Windows Console or server path fails | Medium-high | Critical | S0 first; two paths; Linux host as last resort |
| Folder `.mcp.json` or `ask` rules ignored under Console (S2) | Medium | High | Distinguish MCP launch from settings enforcement: gate-only CLI only if enforcement passed; otherwise repair or use tested steward |
| Session allow leaks across requests (S3b) | Low-medium | Critical | Ask rules, gate hook, E2E-11; steward fallback |
| Identity claim mismatch (S1) | Medium | Medium | Open policy/unclaimed allows; owner policy/unclaimed refuses; claimed PI owner allows. Verify all three |
| Room sessions exceed laptop capacity (S6) | Medium | Medium | Measure actual 3 + 5R sessions, clean prior takes, require 20% RAM headroom; cut `@scribe` if needed |
| LLM variance while recording | High | Medium | Deterministic core, tight instructions, baseline video, one traceable causal run and labeled new-scenario retakes |
| OpenAlex new-account pacing or budgets | Medium | Medium | Key created Wednesday; cache; cassettes; labeled replay |
| Scope creep | High | High | Cut lines A-D; freeze Fri 22:45 |
| Solo fatigue | High | High | Scheduled sleep |
| Overclaiming (privacy, compliance, IRB, Wispr API) | Medium | High | Limits section in README; honest labels |
| Submit form surprises | Low-medium | High | S8 on Wednesday; submit five hours early |

**Operational ownership and costs:** For the solo demonstration the builder operates and backs up the standalone ledger, verifies restore, reconciles any external record manually, and monitors the PI queue. The PI is the planned decision owner; a named real human fallback must be agreed before any real deployment, otherwise requests remain pending or expire. No external purchasing is performed. Estimate total cost as hosting + model/API usage + storage/backups + operator and PI time + reconciliation and recovery; all components and actual demand remain unmeasured. For an illustrative monthly cost, assuming $0 hosting, $10 model/API, $2 backup storage, two operator hours and 10 PI minutes at an assumed $20/hour, total is 0 + 10 + 2 + (2 + 10/60) x 20 = $55.33; replace every assumption with observed values, including reconciliation and recovery time. Do not equate self-hosting with free operation. If 0.5-0.75 h remains after core and delivery are green, test whether lineage is readable in the existing room message; record active task and wait separately.

## 9.8 Questions for the organizers (WeMakeDevs Discord, Wednesday)

Bundle into one concise request, <=15 minutes excluding form inspection: Can one entrant receive the main award and side awards together? What form fields, media formats, video length/hosting requirements and evidence-link methods apply? Resolve the conflicting core-prize count only if relevant. The event already permits Wispr and Blog entries alongside a track; simultaneous awards are UNVERIFIED. Ask about synthetic role-play and labeled API replay only if the form or rules make them unclear. Continue building and package honestly while awaiting replies; none is a prerequisite for the authorized submission.
