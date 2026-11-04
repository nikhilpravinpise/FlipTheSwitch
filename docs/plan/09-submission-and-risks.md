# 9. Submission, prizes, judging, risks

Back to the [master plan](README.md). Event facts are in [`../flip-the-switch-hackathon.md`](../flip-the-switch-hackathon.md).

## 9.1 Prize stacking

| Prize | Evidence we submit | Award signal | Priority |
| --- | --- | --- | --- |
| **Track 1: Best Business Workflow** | Real room workflow, human gate, completed outputs, reproducible repo, video | $2,000 cash (main page) | Highest |
| **Code with Wispr** | Voice used for prompts, agent instructions, docs and documentation; Insights screenshot; voice log | $500 cash | High: nearly all effort compounds with the build |
| **Best Blog** | First-timer guide to Switch approvals with exact steps and screenshots | AirPods 5: one advertised on main page; DTA differs | High after the core works |
| **#HowISwitch** | Short honest clips and the final video | Logitech keyboards: 5 advertised on main page; DTA differs | Medium, low effort |
| Core Contribution | Skipped solo ([08](08-build-schedule.md#84-core-contribution-pr)) | $100/PR | Skip solo for this submission |

The [main event page](https://www.wemakedevs.org/hackathons/switch) currently lists 20 random project swag recipients and a certificate for every submission; its 20 core-PR prizes conflict with its own judging section and the [DTA page](https://www.devtoolsacademy.com/hackathons/flip-the-switch), which say 10. Count UNVERIFIED. A solo core PR is skipped: at a 4-hour cap even a certain $100 is at most $25/hour before costs.

Named cash opportunity: $2,500 for Track 1 plus Wispr, conditional on winning and on legitimate stacking (the event allows Wispr alongside a track and a blog alongside a workflow; it does not guarantee every combination). We do not enter the second workflow track with the same build.

## 9.2 Submission (website Submit form)

Submission is through the **Submit button on the hackathon website**. During S8, the builder manually inspects the authenticated form for 10 minutes without submitting a dummy entry; the builder also submits manually ([event rules](https://www.wemakedevs.org/hackathons/switch/rules)). Record actual field names, required flags, accepted formats, video/hosting limits and side-track mapping; the [public route](https://www.wemakedevs.org/hackathons/switch/submit) exposes a loading shell, so those details remain UNVERIFIED. Within that 10-minute S8 inspection, identify an actual image upload or link field and its accepted format; test its selection or validation without submitting a dummy entry, and record what the interface actually accepts. Pass only if the complete image can be attached or an accessible image link is accepted by a supported field. A README link alone is UNVERIFIED as an acceptable substitute. If acceptance remains unclear, ask organizers promptly, retain the timestamped screenshot and its README link as supporting material, mark the Wispr entry uncertain, and submit the core on time. The public route does not establish authenticated form behavior:

- [ ] Public GitHub repo, logged-out accessible, MIT or Apache-2.0 license, no vendored Switch code (Switch's license includes a Commons Clause)
- [ ] README (outline below) naming every agent, provider, room and bridge and how Switch is used
- [ ] Demo video link (YouTube, public or unlisted, verified logged out) plus a copy as a GitHub release asset
- [ ] Wispr Insights final screenshot (`docs/wispr-insights-final.png`) by 18:00 after last dictation; attach/check by 18:30. Keep baseline and earlier complete backup; link three authentic build clips and voice log
- [ ] Blog link and #HowISwitch post links
- [ ] Choose Best Business Workflow and include Code with Wispr / Best Blog evidence using the controls actually found in S8; do not assume track selectors exist
- [ ] Clean-room reproduction done (M-03); CI green; `docs/test-evidence.md` current
- [ ] gitleaks clean; no em dash anywhere; no secrets or private URLs in video or screenshots
- [ ] Synthetic data, role-play and any replay labeled; one real event identity only, with two local synthetic test users distinguished from organizer accounts ([rules](https://www.wemakedevs.org/hackathons/switch/rules)); ask organizers if local test users are treated as participation identities
- [ ] Submitted by Saturday 19:00 IST; confirmation screenshot saved; every link re-checked in incognito afterwards

## 9.3 README outline

Choose the opening for the demonstrated branch, and publish only after its evidence gates pass:

> # LabQuorum
> A lab booking request reaches an agent in a Switch room. The agent proposes an alternative; an eligible person reviews the exact request before a booking is committed.
>
> A student asks `@labops` for an instrument. On the certified configuration, Switch routes the request and the tested decision path restricts the response. LabQuorum rechecks the revision and rules before committing. The data are synthetic and the builder plays both labeled local personas.

**Proposal-only replacement:** "A lab booking request reaches `@labops` in a Switch room. It proposes an alternative; this request is unapproved and no booking is committed. The approval boundary did not pass certification." Link the matching `docs/evidence/proposal-only/` transcript or screenshot and zero-booking status export, with the same request ID; if the export cannot prove zero bookings, label that status unverified. Omit approval, refusal, commit and stale claims. Link the actual proposal and its inputs rather than nonexistent data/run/draft references.
First screenful or one click: branch-appropriate proof (refusal/acceptance GIF only when certified), video, sample output folder and one tested reproduction path. Include installed versions, provider and API prerequisites, measured setup time, rooms, bridge, exact first message, expected output, current booking request and decision references, plus data/run/draft references only if built, and shipped/simulated/roadmap labels. Attribute routing and permission primitives to Switch; LabQuorum adds lab state and evidence-version consequences. Link test evidence, limitations, voice reel and full Insights image; put planner provenance in acknowledgments. Budget 0.5 hour; a reader must find one current output and its inputs within 60 seconds. Metadata checks establish identity/retraction signals, not whether a claim is supported.

Summarize five installed-version invariants with actual traces: PI accepted, student refused with no change, changed revision rejected, session choice followed by a fresh card, disconnect produced no offline commit. This 0.5-hour summary reuses required tests; 5/5 pass before advertising the native gate. If the steward is selected, replace the second sentence with: "Switch routes the request; the separately tested steward checks the sender and binds the PI message to the request revision." Publish that wording only after wrong-person, replay, expiry, changed-revision and recovery tests pass with zero unauthorized commits. Both branches exclude direct invocation by the same OS user. If neither passes, describe proposals only.

## 9.4 Blog (Best Blog: clarity for a first-time Switch user)

The Saturday 15:15-16:30 block funds 45 minutes for README and 30 minutes for link audit; the optional blog is dropped. Reconsider a short blog only if a separate non-overlapping block is found after delivery is green; no 1.5-hour block is funded. Use the actual installed versions, screenshots and reproduced failures; link the voice-build examples only if captured. Publish `docs/blog.md` and a public copy only if time remains.

- Certified booking: "A lab booking decision in a Switch room: a first build with Wispr Flow". Show request, alternative, wrong-person refusal, eligible decision and committed record, with the tested setup and limits.
- Proposal-only: "A lab booking proposal in a Switch room: what our approval test could not certify". Show request, alternative, unapproved status and the failed or timed-out gate, with the proposal artifact. Do not promise a decision or booking.
- Separately built stale detection: use "One corrected CSV marked our draft stale" only after recording the actual correction, hashes and stale result. Claim a refused release or renewed decision only if the complete release loop passed.

One newcomer completing the bounded setup would support a usability observation; if unavailable, report only the clean-room transcript.
## 9.5 #HowISwitch

Reuse 20-30 seconds of genuine refusal and accepted decision, plus stale detection if implemented. Spend <=15 extra minutes; side-award odds are unknown. Draft for the builder to post: "A shared lab booking needs a clear decision. LabQuorum proposes a slot in Switch, shows a refused request from the wrong person and records an eligible decision before booking. Synthetic demo, builder-played roles, built with Wispr Flow. Demo: <link> Code: <link> #HowISwitch". For proposal-only, replace the draft with: "LabQuorum proposes a lab booking slot in a Switch room. The request remains unapproved; no booking is committed. Synthetic demo, builder-played roles, built with Wispr Flow. Demo: <link> Code: <link> #HowISwitch"; assert zero bookings only if the status export proves it. Remove any other unproven clause. If an already-reachable participant is available after the core is green, an unfunded <=0.5-hour observation may observe one uncoached booking-conflict task, recording task completion, errors, active time and waits; this 0.5 h observation does not validate the full 1.25-1.75 h protocol in 01. Allocate a non-overlapping block before starting. It cannot validate the full pilot and same-task comparison, which need 1.25-1.75 hours if sequential; one observation is not a demand estimate.

## 9.6 Judging scorecard self-assessment

No score is earned yet: the product and runtime boundary are UNBUILT / UNVERIFIED. These are subjective conditional projections, not measured marks or winning probabilities. The [published rubric](https://www.devtoolsacademy.com/hackathons/flip-the-switch) weights Switch/technical/creativity/presentation 30/25/25/20. A planned test ID is not a pass. Each cell requires actual linked footage, output, tests or a clean-clone transcript; a failed gate invalidates that scenario's projection rather than earning its number.

| Criterion | Booking-only funded scenario /10 (weighted); independent gate | Stale-detection scenario /10 (weighted); independent gate | Full-release scenario /10 (weighted); independent gate |
| --- | --- | --- | --- |
| Switch 30% | 8 (24): real routing, wrong-person refusal, eligible decision and booking on certified runtime | 8 (24): same certified booking plus visible routed correction | 9 (27): same plus a routed fresh decision for release |
| Technical 25% | 6.5 (16.25): booking invariants, bypass tests and clean clone pass | 7 (17.5): booking gates plus verified input revision and stale descendants | 8 (20): stale gates plus tested blocked release, refresh and new approval |
| Creativity / impact 25% | 5.5 (13.75): bounded lab-specific conflict resolved; demand and advantage unverified | 6.5 (16.25): corrected input demonstrably identifies affected outputs; no release claim | 7.5 (18.75): full correction-to-release consequence shown; no assumed ROI or uniqueness |
| Presentation 20% | 7 (14): legible causal booking film, labels and reproducible README | 7.5 (15): booking presentation plus legible causal stale proof | 8.5 (17): full causal cycle and its limits legible in film and README |
| Total | **68/100** | **72.75/100** | **82.75/100** |

Stale detection and full release are unfunded until separately scheduled and tested; these scenarios are not the funded scope. A failed certification uses the proposal-only script and has no numerical projection. Scores are editorial estimates, not objective measurements. For shot priority, score Switch specificity, visible consequence, distinctiveness and clarity 0-2 each: retraction 0+1+1+2=4/8; refusal/commit 2+2+1+2=7/8; complete stale-block/new-decision 2+2+2+1=7/8. These estimates favor the certified booking beat; the complete release beat remains unfunded.

## 9.7 Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Windows Console or server path fails | Medium-high | Critical | S0 first; two paths; Linux host as last resort |
| Folder `.mcp.json` or `ask` rules ignored under Console (S2) | Medium | High | Distinguish MCP launch from settings enforcement: gate-only CLI only if enforcement passed; otherwise repair or use tested steward |
| Session allow leaks across requests (S3b) | Low-medium | Critical | Ask rules, gate hook, E2E-11; steward fallback |
| Identity claim mismatch (S1) | Medium | Medium | Open policy/unclaimed allows; owner policy/unclaimed refuses; claimed PI owner allows. Verify all three |
| Room sessions exceed laptop capacity (S6) | Medium | Medium | Measure actual 3 + 5R sessions, clean prior takes, require 20% RAM headroom; keep the optional `@scribe` deferred |
| LLM variance while recording | High | Medium | Deterministic core, tight instructions, baseline video, one traceable causal run and labeled new-scenario retakes |
| OpenAlex new-account pacing or budgets | Medium | Medium | Key created Wednesday; cache; cassettes; labeled replay |
| Scope creep | High | High | Use the escalation rules in 08; freeze Sat 00:15 |
| Solo fatigue | High | High | Scheduled sleep |
| Overclaiming (privacy, compliance, IRB, Wispr API) | Medium | High | Limits section in README; honest labels |
| Submit form surprises | Low-medium | High | S8 at the next available session before packaging; submit 4 h 59 min early |

**Operational ownership and costs:** For the solo demonstration the builder operates and backs up the standalone ledger, verifies restore, reconciles any external record manually, and monitors the PI queue. The PI is the planned decision owner; a named real human fallback must be agreed before any real deployment, otherwise requests remain pending or expire. No external purchasing is performed. Estimate total cost as hosting + model/API usage + storage/backups + operator and PI time + reconciliation and recovery; all components and actual demand remain unmeasured. For an illustrative monthly cost, assuming $0 hosting, $10 model/API, $2 backup storage, two operator hours and 10 PI minutes at an assumed $20/hour, total is 0 + 10 + 2 + (2 + 10/60) x 20 = $55.33; replace every assumption with observed values, including reconciliation and recovery time. Do not equate self-hosting with free operation. If 0.5-0.75 h remains after core and delivery are green, test whether lineage is readable in the existing room message; record active task and wait separately.

## 9.8 Questions for the organizers (WeMakeDevs Discord, next available session)

Bundle into one concise request, <=15 minutes excluding form inspection: Can one entrant receive the main award and side awards together? What form fields, media formats, video length/hosting requirements and evidence-link methods apply? Resolve the conflicting core-prize count only if relevant. The event already permits Wispr and Blog entries alongside a track; simultaneous awards are UNVERIFIED. Ask about synthetic role-play and labeled API replay only if the form or rules make them unclear. Continue building and package honestly while awaiting replies; none is a prerequisite for the authorized submission.
