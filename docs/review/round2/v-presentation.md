## Verdict

**6.9/10 for presentation readiness**, a judgment of the plan rather than a predicted organizer score. Rubric: demo feasibility 6/10 at 25%, shot timing and legibility 6/10 at 25%, Wispr evidence 8/10 at 20%, submission readiness 8/10 at 20%, judging honesty 7/10 at 10%. Calculation: 1.50 + 1.50 + 1.60 + 1.60 + 0.70 = 6.90.

The three biggest problems are the booking request whose duration and valid alternative are unspecified, mandatory inventory and release shots outside the scheduled build, and the lack of measured per-shot timing. These are plan defects, not evidence that an implementation has failed. Form fields, installed runtime and real recordings were not accessible to this review.

**To reach 9/10:** fix VP-01 through VP-05 and VP-09; document an exact seed-to-output script for both full and cut scopes; rehearse and time the actual provider, demonstrate readable 720p footage from one traceable run, and publish genuine build-by-voice evidence with an accessible Insights image. Inspect the real form, prove a clean-clone path and successful manual submission packaging, and label scenario scores as conditional. These are acceptance gates, not a promise of a judge's score.

## Previous findings status

| ID | Status | Evidence quote or location |
| --- | --- | --- |

| JD-01 | Resolved | 04 4.3: “Preview actual Maya refusal, PI acceptance and booking” in first 20 seconds. |
| JD-02 | Partly | 04 4.3 requires three rehearsals and elapsed captions, but has no per-shot raw/edit worksheet or measurements. |
| JD-03 | Partly | 04 4.2 seeds “22 mL” against “20 mL”; inventory hold and reorder are roadmap and slot duration is unspecified as an explicit parameter. |
| JD-04 | Resolved | 04 4.2: “C5 (8 ug/mL, replicate 2)” and one-value correction. |
| JD-05 | Partly | README makes release conditional; 04 4.3 also unconditionally directs “new PI decision,” conflicting with fallback. |
| JD-06 | Resolved | README: “Booking is the only binding core action”; helpers can write observations and drafts. |
| JD-07 | Resolved | 05 5.3 and both lab-template passages say “Each binding request requires its own PI decision” and no batch approval. |
| JD-08 | Resolved | 04 4.3 leads with refusal and commit; citation is a short supporting beat. |
| JD-09 | Resolved | 04 4.2 and seed-data pin an unrelated retraction and notice, plus a separate unresolved negative, and disclaim claim support. Live recheck remains required. |
| JD-10 | Resolved | 04 4.3 says “a researcher must review claim support” and labels simulated day and technical replicates. |
| JD-11 | Partly | 04 4.6 specifies full-width decision and >=16 px at 720p, but short dense shots are not measured. |
| JD-12 | Partly | 04 4.3 ends on output and README, but a booking-only cut cannot show required dataset/run/draft references. |
| JD-13 | Partly | 04 4.4 specifies the four-agent core and separates optional template checks; actual import is unverified. |
| JD-14 | Resolved | 04 4.6 matches 08's 09:00 clean room, 10:30 takes and 13:15 edit; 08 8.4 skips solo core work. |
| JD-15 | Resolved | 04 4.5 requires known-good baseline or fresh provider-sensitive tests for pi-desk. |
| JD-16 | Resolved | 04 4.5 requires “one uninterrupted successful causal run” and labels reseeded retakes as new scenarios. |
| JD-17 | Partly | 09 9.6 labels projections subjective, gives a reduced estimate and correct sums; current-plan score presumes unbuilt behavior. |
| JD-18 | Resolved | 05 introduction distinguishes 2,000 warning, 5,000 block and paid/trial exemption. |
| JD-19 | Resolved | 05 5.6 and 09 9.2 set final Insights by 18:00 and attachment check by 18:30. |
| JD-20 | Resolved | 05 5.6 states UTC days, retry, conditional rankings and account-window limitation. |
| JD-21 | Resolved | 05 5.2 labels categories “Expected category, verify in app”; 5.4 checks three pastes, routing and observed category. |
| JD-22 | Resolved | 05 5.1 distinguishes iPhone keyboard from Android bubble and sets 30-minute test cap. |
| JD-23 | Resolved | 05 5.1 limits API claim and states MCP eligibility, BAA restriction and zero core hours. |
| JD-24 | Resolved | 05 5.1 separates training, cloud storage, local history and Notetaker; Wispr BAA does not certify the whole system. |
| JD-25 | Partly | 05 5.7 links three build clips and excludes automated E2E as voice evidence; actual clips and artifact linkage are unverified. |
| JD-26 | Resolved | 09 9.2 requires manual S8 inventory and labels exact fields and limits UNVERIFIED. |
| JD-27 | Resolved | 09 9.8 asks about simultaneous awards, not already permitted entry combinations, without blocking work. |
| JD-28 | Resolved | 09 9.4 asks for a reproducible tutorial and actual failures, with a clean-room transcript if no newcomer. |
## New findings

| ID | Severity | File and section | What is wrong | Evidence | Exact fix | Reasoning metric |
| --- | --- | --- | --- | --- | --- | --- |

| VP-01 | High | 04 4.2-4.3, 02 booking instructions | The 14:00-17:00 request does not say whether this is a three-hour booking or an availability window, or specify a duration for an alternative. | Existing booking 14:00-15:30, cleaning gap 15 min; 02 requires nearest free slot of same length. | Request a 60-minute booking within 14:00-17:00 and explicitly seed and test 15:45-16:45, or specify an acceptable wider search window and its exact valid result. | If interpreted as a three-hour booking, 15:30 + 15 min = 15:45 and only 75 min remain before 17:00, less than 180. A shorter request needs an explicit duration. |
| VP-02 | High | 04 4.3, 08 8.2, 02 2.4 | Mandatory purchase-proposal and stock-hold proof depends on inventory functionality marked roadmap. | 04 requires a purchase proposal and a 20 mL hold; 02 labels stock/reorder inventory roadmap; 08 says inventory orders are roadmap. | Drop inventory proof and stock-hold acceptance from the core shot unless that subsystem is explicitly promoted, budgeted and tested; use 22 mL only as background. | One video beat depends on an unbudgeted roadmap subsystem; 22 - 20 = 2 mL does not prove a hold exists. |
| VP-03 | High | 04 4.3, 08 8.2 | Stale fallback conflicts with unconditional new decision and release in shot action; release enforcement is not scheduled. | 3:10-3:25 says “Rerun, refresh draft, new PI decision”; adjacent fallback says do not claim reapproval; README puts final release on roadmap. | Give two complete mutually exclusive shot rows: core stale detection only, and expanded refusal/rerun/new decision/release only after tests and allocated build time. Fix booking-only final frame. | Core needs zero release actions; expanded path requires four observable transitions in an unmeasured 15-second segment. |
| VP-04 | High | 04 4.3 and 4.6 | No current per-shot raw worksheet or measurement exists; dense proof and three build clips have short holds. | 417-651 s describes the former script; three clips share 15 s; 30 s includes dataset, hashes, figure, exclusions and replicate label. | Count spoken words, interactions, readable holds, raw waits and edited seconds per shot; rehearse a complete real run and inspect 720p export. Put detailed voice proof in the linked reel and cut optional beats if needed. | 15/3 = 5 s per clip including transitions; 30 s at 120-150 wpm is 60-75 words. Three 4-minute smoke checks use 12 of 120 minutes before resets and takes. |
| VP-05 | Medium | 04 4.3 and 09 9.3 | Generic narration attributes authorization to Switch even if the steward branch is used. | 04 says “Switch ... restricts who can answer” but separately substitutes a revision-bound steward message; 09 asks for branch-specific wording. | Provide distinct native and steward narration naming the tested identity-checking component, its boundary and Switch's role. | Two branches share one generic first-shot script; one branch lacks specific wording. |
| VP-06 | Medium | 09 9.6 and README numbers | Current-plan scores assume real behavior; improved scores depend on roadmap work and user observation outside the scheduled core. | 09 requires real E2E and a stale-release block; README calls 186 tests planned, not passed. | Rename both columns scenario projections, state baseline assumptions explicitly, show unbuilt/unverified status without an earned score, and label the improved path unfunded stretch unless scheduled. | 24+16.25+16.25+12=68.50; 27+20+18.75+17=82.75; reduced 22.5+16.25+13.75+14=66.5. Arithmetic is correct. |
| VP-07 | Medium | 05 5.1-5.5 and 08 8.2 | Bench parsing is a claimed voice feature but is roadmap, and unitless OD conflicts with generic missing-unit clarification. | 05 5.5 displays “no unit expected” yet asks about numbers without units; 08 excludes general bench parsing. | Mark the feature roadmap unless scheduled and tested; exempt dimensionless OD from the unit prompt; base side-track evidence on authentic build clips. | One product voice path has no dedicated core build block and is not in the shot list. |
| VP-08 | Low | 09 9.7-9.8 and 08 8.1 | Form inspection and questions still say Wednesday although the reforecast starts Thursday. | 09 says S8 Wednesday; 08 puts S8 on Thursday and requires rebasing. | Replace Wednesday with the next available session and inspect before packaging. | Two outdated Wednesday references; past time cannot be recovered. |
| VP-09 | Medium | 04-demo 4.3 and 08 8.2-8.3 | Cut policy removes literature and analysis first, but the only shot list still requires citation, plate import, figure, draft and stale correction, and its final frame requires run/dataset/draft references even for a booking-only result. | 08 explicitly says cut literature and assay if core slips; 04 allocates 1:30-3:25 to these dependent beats. | Add a complete reduced-cut shot list ending on the committed booking and its request/decision record, plus README and Wispr proof; remove all unbuilt artifacts and adjust durations before recording. | The affected 1:30-3:25 interval is 115 s, exactly half of the 230 s target; unused time must be intentionally reallocated or the film shortened. |

## Verified facts

- [Event page](https://www.wemakedevs.org/hackathons/switch) advertises a $2,000 Business Workflow prize and a $500 Code with Wispr side track; the latter requests spoken prompts, instructions and documentation plus a desktop Insights screenshot. Entry alongside a track is stated; simultaneous awards are not assured.
- [Organizer submission and rubric](https://www.devtoolsacademy.com/hackathons/flip-the-switch) list a public repository, short running-workflow video and reproducible Switch README, with weights 30/25/25/20. No numeric video duration or host is specified there. The authenticated Submit form was not inspected, so its fields and limits remain unknown.
- [Official rules](https://www.wemakedevs.org/hackathons/switch/rules) prohibit automated registration or submission and permit AI development subject to challenge rules. The user-supplied cutoff of 23:59 IST equals 18:29 UTC; the 19:00 IST target leaves 4 h 59 min.
- [Wispr Insights](https://docs.wisprflow.ai/articles/8760230576-your-usage-tab-track-your-dictation-stats-in-wispr-flow) is desktop-only; lifetime words include mobile, categories are desktop-only word-based measures and the heatmap uses UTC dates. A 05:30 IST start corresponds to 00:00 UTC. Insights does not prove project-only usage or productivity.
- [Wispr's free-tier documentation](https://docs.wisprflow.ai/articles/4760791189) says default desktop warnings start after 2,000 words, blocking above 5,000; active paid plans and trials are exempt. Pro redemption is supplied by the user, not verified in the app.
- [Wispr IDE guide](https://docs.wisprflow.ai/articles/6434410694-use-flow-with-cursor-vs-code-and-other-ides) documents Ctrl+Win on Windows, variable recognition in supported editors, and file tagging only in Cursor/Windsurf chat; [Command Mode](https://docs.wisprflow.ai/articles/4816967992-how-to-use-command-mode) is disabled by default and uses Ctrl+Win+Alt on Windows.
- Arithmetic checks: shot boundaries sum to 230 seconds; 42 wells = 6 rows x 7 concentrations; C5 is 8 ug/mL under the declared column mapping; 10 matched notes x 4 fields = 40 checks per modality; example monthly cost 12 + (2 + 10/60) x 20 = $55.33 rounded. These are arithmetic checks of proposed data, not proof generated files or tests exist.
- The Crossref relationship and cited pinned Switch renderer source could not be fetched in this review; the plan's fixture and source claims remain contingent on the specified build-time recheck. No product, live Switch/Wispr session, uploaded video, authenticated form, or test results were inspected.





