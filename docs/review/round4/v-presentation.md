## Verdict

**7.5/10. Does not pass** the 9/10 and no-open-high bar. Rubric for the plan: demo and fallback 6.5/10 x 30% = 1.95; shot realism 7/10 x 20% = 1.40; Wispr evidence 7/10 x 20% = 1.40; submission readiness 9/10 x 15% = 1.35; judging assessment 9/10 x 15% = 1.35. Total 7.45, rounded to 7.5. These are judgments about the written plan, not predicted organizer scores. No points are removed merely because build-time evidence is not yet available.

The three biggest problems are the deferred protocol fixture in the mandatory demo, the missing voice-clip failure branch and its baseline sequencing, and the absence of a viable presentation fallback when the room or proposal cannot be made.

To reach 9, make the exact file-and-section edits in VP-01 through VP-06 below, including both high findings and the consistency and timing repairs. These are plan changes; runtime certification, recorded clips and authenticated form access remain future gates. The brief names round3/judging.md, which is absent; round3/v-presentation.md is the matching presentation review. Its new findings and all underlying high/blocker JD findings are assessed below; all 13 underlying medium JD findings are sampled. Historical evidence quotes are checked against the current plan.

## Previous findings status

| ID | Status | Evidence |
|---|---|---|
| JD-03 | resolved | 04 4.3: "Inventory is background; no stock hold ... is required" for the funded booking. |
| JD-04 | resolved | 04 4.2: "C5 (8 ug/mL, replicate 2)" and the corrected CSV is "identical except C5 = 0.830". |
| JD-05 | resolved | 04 4.3: "stale draft detected"; release blocking and fresh decision require separate implementation and tests. |
| JD-06 | resolved | README Mechanism confines binding to booking and discloses same-OS-user exclusion; 04 4.3 separates native and steward narration. |
| JD-07 | resolved | 05 5.3: "Each binding request requires its own PI decision. Use Allow once"; 04 4.3 certifies fresh cards. |
| JD-08 | resolved | 04 4.3 opens with refusal and decision; 09 9.6 ranks refusal/commit 7/8 versus retraction 4/8. |
| JD-09 | resolved | 04 4.2 requires "pinned unrelated generic retraction and notice" with retrieval date; 4.3 caps selection at 30 min. |
| JD-11 | resolved | 04 4.6 specifies "full-width chat for decisions", key text >=16 px at 720p and two-viewer review. |
| JD-15 | resolved | 04 4.5: for pi-desk use "known-good baseline or rerun S2/S3a-c and affected E2E on the alternative before filming". |
| JD-16 | resolved | 04 4.5 requires "one uninterrupted successful causal run" and logs source identities, with reseeded retakes labeled. |
| JD-19 | resolved | 05 5.6: final capture by 18:00, attach by 18:30, submit by 19:00, retaining earlier backup. |
| JD-25 | partly | 05 5.6-5.7 specifies three authentic build clips, original scorecard and artifact links; failure and timing remain open under VP-03. |
| JD-10 | resolved | 04 4.3 says "researcher reviews claim support" and labels the plate "synthetic" and "technical-replicate". |
| JD-13 | resolved | 04 4.4 requires verified four-agent core membership and specifies optional project/HQ counts. |
| JD-14 | resolved | 04 4.6 schedules baseline, takes and edit; 09 9.1 skips core contribution solo. |
| JD-18 | resolved | 05 introduction distinguishes 2,000 warning, 5,000 block and paid/trial exemption, with active-plan check. |
| JD-20 | resolved | 05 5.6 states UTC days, conditional rankings and account rather than project-only delta, plus bounded retry. |
| JD-21 | resolved | 05 5.2 says "Expected category, verify in app" and 5.4 tests the detected category. |
| JD-22 | resolved | 05 5.1 distinguishes "iPhone Flow keyboard or Android floating Flow bubble" with 30-minute cap and desktop fallback. |
| JD-23 | resolved | 05 5.1 says "No supported public dictation API or SDK verified" and identifies MCP prerequisites and BAA exclusion. |
| JD-24 | resolved | 05 5.1 separates training, cloud storage and local history and limits BAA claims. |
| JD-27 | resolved | 09 9.8 asks "Can one entrant receive the main award and side awards together?" without waiting to build. |
| VP-01 | resolved | 04 4.3: "three distinct 5 s holds plus 1 s total transitions make 20 s" after 4 s narration; measured rehearsal required. |
| VP-02 | resolved | 09 9.6 supplies separate booking, stale and full-release columns, with independent gates and totals 68, 72.75 and 82.75. |
| VP-03 | partly | 04 4.3 provides a timed proposal-only cut and status export; its unconditional ending conflicts with unverified status. See VP-02 below. |
| VP-04 | resolved | 05 5.6: "17:45-18:00 ... bounded refresh/retry"; 09 9.2 requires an actual supported route, otherwise marks entry uncertain. |
| VP-05 | resolved | 09 9.4: "optional blog is dropped" from the funded block and gives branch-specific titles. |
| VP-06 | resolved | 04 4.4 distinguishes "local synthetic Mattermost test users" from "single real event account" and requests clarification. |
| VP-04 (round 2) | resolved | 04 4.3 budgets 4 + 15 + 1 seconds and requires three rehearsals and two viewers. |
| VP-06 (round 2) | resolved | 09 9.6 says "No score is earned yet" and makes each scenario conditional on independent evidence. |
| JD-01 | resolved | 04 4.3 requires both unfamiliar viewers to identify "Switch as the router and the decision role by 0:20". |
| JD-02 | resolved | 04 4.3 supplies word, hold and transition budgets, a measured worksheet and cut rule. |
| JD-12 | partly | 09 9.3 has a branch-specific proposal replacement and omits nonexistent outputs; the certainty mismatch remains in VP-02. |
| JD-17 | resolved | 09 9.6 distinguishes booking, stale and full-release projections and requires scenario-specific evidence. |
| JD-26 | resolved | 09 9.2 tests an actual form-supported image route for 10 min and labels acceptance uncertain if unconfirmed. |
| JD-28 | resolved | 09 9.4 drops the unfunded blog and provides titles conditional on demonstrated branch. |

## New findings

| ID | Severity | File and section | What is wrong | Evidence | Exact fix | Reasoning metric |
|---|---|---|---|---|---|---|
| VP-01 | high | 04 4.2-4.3; 08 8.2; templates/seed-data | The mandatory booking script requests and inspects PRT-007 v3, but the seed explicitly defers all protocol fixtures; the funded booking scope therefore does not specify that this input exists or can be validated. This affects both demo branches. | 04 dictates "under PRT-007 version 3" and inspects protocol; seed says "Only people, instrument and booking fixtures are funded; ... protocol ... roadmap". | Either fund a minimal immutable PRT-007 identifier/version fixture plus its validation and tests within a reforecast in 08, or remove protocol from the funded request, card inspection and booking fixture in 04 and seed; retain protocol behavior solely as separately tested stretch. | One mandatory reference depends on zero funded protocol fixtures; no runtime test can pass the scripted reference from the specified seed without an additional assumption. |
| VP-02 | medium | 04 4.3; 09 9.3; README Mechanism | The proposal script asserts no booking at the opener and ending, and README supplies the same definite language, while allowing status to be unverified. Also a global zero-bookings export is impossible with Lena's seeded committed booking. | 04 says "No booking was committed" and "If zero bookings cannot be verified, state the status is unverified instead"; 04 4.2 seeds one existing booking. | Require a request-ID-scoped ledger query showing no booking created by AR-0042, with time and ledger identity; if unavailable, replace every opener, ending and README claim with "booking status unverified" and do not use a zero-global-bookings criterion. | Seed starts with 1 committed booking, so global count 0 is false; AR-0042-specific count can be 0. |
| VP-03 | high | 05 5.6-5.7; 04 4.3 and 4.6; 08 8.2 | Authentic voice clips have pass criteria and an estimated capture budget but no predetermined failure decision. Both timed demo cuts mandate a clip even if capture fails; Friday's baseline precedes the scheduled Wispr clips block. | 05 requires "three authentic 15-25 second clips" and 04 requires one excerpt; 08 schedules baseline 20:15-22:15 and clips 22:15-00:15 Friday. | Reserve a non-overlapping capture and verification slot for at least one authentic prompt clip before Friday's baseline; cap the 3-clip reel at 45 min within a named block. Define failure: omit the clip and reel claim, describe actual voice evidence and mark Wispr competitiveness uncertain while still submitting the scorecard and core; update both cuts and 09 checklist. | Three clips have 45-75 s of footage, but 30-45 min of capture work is estimated; the currently named clips block starts after the baseline. |
| VP-04 | medium | 04 4.3-4.6; 08 8.2 | Both demo cuts require a working room and a real proposal, but a failed Switch setup or failed two-person fixture only stops binding; no time-boxed decision covers inability to produce a real room or proposal. A proposal-only script cannot execute if its prerequisites fail. | 08 8.3 says "if not proven, stop binding" after S0 and preflight; 08 S4 says fixture failure stops dependent tests; 04 requires "real request and alternative". | Add a bounded read/propose smoke gate after S0/S4 and before baseline, specifying command, expected response and conflict, evidence and deadline. If it fails, attempt only a separately tested alternative within named slack, then submit a plainly labeled non-running prototype with actual artifacts and disclose workflow submission eligibility as uncertain; never film it as a live Switch run. | At least 1 real room and 1 actual generated proposal are required by the fallback; neither is guaranteed by disabling mutations. |
| VP-06 | medium | 04 4.3, draft shot | The optional 15-second draft shot allocates up to 15 words, an 8-second hold and an interaction; at the stated non-overlap rate the maximum narration and hold already exceed the whole shot. | 15 words at 120 wpm take 7.5 s; 7.5 + 8 = 15.5 s before interaction or transition. | Cap this row at 10 words and reserve 2 s for its interaction, or lengthen it and cut elsewhere; retain measured rehearsal and omit the row when the feature is not built. | 7.5 + 8 = 15.5 > 15, a 0.5 s deficit before interaction. |
| VP-05 | low | 09 9.1-9.2, 9.4-9.5 | Submission checklist unconditionally requests blog and social links despite the blog being dropped and the social post unfunded. | 09 9.2 lists "Blog link and #HowISwitch post links"; 9.4 drops blog and 9.5 asks for up to 15 extra minutes. | Mark both optional and include only if published; allocate non-overlapping social time or omit it. Align the high blog priority in 9.1 with the funded decision. | 0 min allocated to blog or social in 08, versus up to 15 min social work. |

## Verified facts

- The [event page](https://www.wemakedevs.org/hackathons/switch) asks for voice-built prompts, room instructions and README, and an Insights screenshot with submission; it allows the Wispr track alongside a main track. The [organizer judging page](https://www.devtoolsacademy.com/hackathons/flip-the-switch) states 30/25/25/20 weights and requests a public repository, short running-workflow video and reproducible README. The authenticated form itself was not inspected.
- [Wispr Insights](https://docs.wisprflow.ai/articles/8760230576-your-usage-tab-track-your-dictation-stats-in-wispr-flow) is desktop-only; lifetime totals combine desktop and mobile, the heatmap uses UTC and rankings can be absent. Retry controls are conditional on the displayed error; merely changing tabs does not force refresh. Four web opens were used, including one unsuccessful Switch source fetch. Previously ledgered URLs were not exhaustively rechecked.
- All weighted score cells and totals in 09 9.6 check: booking 24 + 16.25 + 13.75 + 14 = 68; stale 24 + 17.5 + 16.25 + 15 = 72.75; full 27 + 20 + 18.75 + 17 = 82.75. Priority components total 4/8, 7/8 and 7/8. The conditional scores remain opinions, not earned points.
- Timing arithmetic: opener 4 + 15 + 1 = 20 s; proposal opener 6 + 12 + 2 = 20 s; expanded boundaries total 230 s; reduced and proposal cuts each span 120 s. Omitted expanded segment 1:30-3:25 is 115 s, with other boundaries shifting by 5 s. Other row maximum narration plus minimum hold fits on paper except VP-06; several leave only a few seconds for interaction and need measured rehearsal. Three 15-25 s clips give 45-75 s; 10 notes x 4 fields = 40 checks per modality. The 19:00 target leaves 4 h 59 min to 23:59; 17:45-18:00 is 15 min. $100 / 4 h = $25/h, and 12 + (2 + 10/60) x $20 = $55.33 rounded.
- Seed math: 15:30 plus 15 min cleaning gives 15:45; a 60-minute slot ends 16:45, within the 17:00 limit. Next open day is Monday after Saturday recording, within the Mon-Sat hours and training expiry. The 6 x 7 treatment region is 42 wells; C5 maps to 8 ug/mL. Neither a live generated seed nor a running workflow was inspected.
- Live Switch behavior, room creation, timing, voice clips and logged-in Submit form remain unverified. The source-code fetch failed, so this review does not independently certify the permission-card formatter. The scoped counts and 40 h 10 min schedule total are reported by the prior integration audit, not independently recounted here.

