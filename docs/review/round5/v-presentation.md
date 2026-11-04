## Verdict

**8.8/10. Does not pass**: VP-01 is an open high finding, and the score is below 9. This is a score for the written plan, not a prediction of judges' marks. Runtime evidence does not lower it when a complete bounded test and fallback are specified.

Rubric: demo and branch safety 8.5/10 x 30% = 2.55; shot realism and viewer validation 8.5/10 x 20% = 1.70; Wispr evidence 9/10 x 20% = 1.80; submission 9/10 x 15% = 1.35; honest judging assessment 9.5/10 x 15% = 1.425. Total 8.825/10, rounded to 8.8.

The three biggest remaining problems are the contradictory certification duration, overlapping Friday baseline and voice capture, and a viewer gate with no availability or failed-review fallback. To reach 9 and clear the no-open-high bar, make all exact edits in VP-01 through VP-03; no build-time result is being demanded as a plan edit.

The requested `docs/review/round4/judging.md`, the named editor logs and `integration.md` are absent from this checkout. The available `round4/v-presentation.md` and `round4/fixes.md` were used instead. The table covers every finding in that presentation review and also checks all inherited JD-01 through JD-28 against current text; this cannot establish whether an absent judging file contained additional findings.

## Previous findings status

| ID | Status | Evidence |
|---|---|---|

| VP-01 (round 4) | resolved | 04 4.2 calls PRT-007 a "Roadmap protocol (not used in funded booking)"; 4.3 request contains no protocol. |
| VP-02 (round 4) | resolved | 04 4.3: "Only if that query returns zero may opener and ending say no booking was created by AR-0042"; README Mechanism uses unverified status otherwise. |
| VP-03 (round 4) | resolved | 08 8.2 schedules "Capture and verify authentic prompt clip first" 19:35-20:20 before baseline; 04 4.3 says "otherwise actual voice evidence and mark Wispr competitiveness uncertain". |
| VP-04 (round 4) | resolved | 08 8.3 specifies a 20-minute real-room proposal gate and a 30-minute alternative; failure yields "a plainly labeled non-running prototype" with uncertain eligibility. |
| VP-05 (round 4) | resolved | 09 9.2 marks blog and social links optional; 9.4 drops the blog. |
| VP-06 (round 4) | resolved | 04 4.3 draft row: "<=10 / 2 / 8 s" in 15 s, leaving 2 s after 5 s narration and 8 s hold. |
| JD-01 | resolved | 04 4.3 requires both viewers to identify "Switch as the router and the decision role by 0:20". Viewer availability remains a new issue, VP-03. |
| JD-02 | resolved | 04 4.3 requires three rehearsals and a worksheet of "raw start/end and wait, edited seconds"; omitted waits carry measured captions. |
| JD-03 | resolved | 04 4.3: "Inventory is background; no stock hold, purchase proposal or order is required." |
| JD-04 | resolved | 04 4.2: "C5 (8 ug/mL, replicate 2)"; corrected CSV is "identical except C5 = 0.830". |
| JD-05 | resolved | 04 4.3 limits the optional claim to "stale draft detected" unless release cycle is separately scheduled and tested. |
| JD-06 | resolved | README Mechanism limits the binding action to booking and excludes "a malicious process running as the same OS user". |
| JD-07 | resolved | 05 5.3: "Each binding request requires its own PI decision. Use Allow once." |
| JD-08 | resolved | 04 4.3 previews refusal, decision and booking; 09 9.6 ranks refusal/commit 7/8 and retraction 4/8. |
| JD-09 | resolved | 04 4.2 requires a "pinned unrelated generic retraction and notice" with retrieval date and 4.3 caps selection at 30 minutes. |
| JD-10 | resolved | 04 4.3 says "researcher reviews claim support" and labels the plate synthetic and technical-replicate. |
| JD-11 | resolved | 04 4.6 calls for "full-width chat for decisions" and key text >=16 px at 720p, with two-viewer inspection. |
| JD-12 | resolved | 09 9.3 proposal replacement links the actual proposal and inputs "rather than nonexistent data/run/draft references". |
| JD-13 | resolved | 04 4.4 requires verification of the four-agent core, and separates optional project and HQ counts. |
| JD-14 | partly | 04 4.6 and 08 agree on Saturday final takes and edit; their Friday baseline differs by five minutes, VP-02. |
| JD-15 | resolved | 04 4.5 requires the "known-good baseline or rerun S2/S3a-c and affected E2E" before replacing the gated provider. |
| JD-16 | resolved | 04 4.5 requires "one uninterrupted successful causal run" and labels reseeded retakes as new scenarios. |
| JD-17 | resolved | 09 9.6: "No score is earned yet" and separate evidence-gated booking, stale and full-release projections. |
| JD-18 | resolved | 05 introduction distinguishes 2,000 warning, 5,000 blocking threshold and exemption of active paid plans and trials. |
| JD-19 | resolved | 05 5.6 final capture by 18:00, attach/check by 18:30 and 09 9.2 submit by 19:00. |
| JD-20 | resolved | 05 5.6 says "Final minus baseline measures account usage ... not authenticated project-only work or productivity" and bounds retry. |
| JD-21 | resolved | 05 5.2 calls categories "Expected category, verify in app". |
| JD-22 | resolved | 05 5.1 distinguishes "iPhone Flow keyboard or Android floating Flow bubble" with desktop fallback. |
| JD-23 | resolved | 05 5.1 says "No supported public dictation API or SDK verified" and states MCP restrictions. |
| JD-24 | resolved | 05 5.1 separates "training, cloud storage and local history" and limits BAA claims. |
| JD-25 | resolved | 05 5.6-5.7 specifies three authentic build clips with artifact links and 45-minute cap; 5.2 states automated E2E "is not voice evidence". |
| JD-26 | resolved | 09 9.2 tests the form-supported image route in 10 minutes and marks acceptance uncertain on failure. |
| JD-27 | resolved | 09 9.8 asks "Can one entrant receive the main award and side awards together?" without awaiting a reply. |
| JD-28 | resolved | 09 9.4 drops the unfunded blog and supplies branch-specific truthful titles. |

## New findings

| ID | Severity | File and section | What is wrong | Evidence | Exact fix | Reasoning metric |
|---|---|---|---|---|---|---|
| VP-01 | high | 04 4.3 certification; 08 8.1-8.2 | Two explicit time boxes conflict for the same safety-critical certification, creating an ambiguous stop rule. | 04 calls it the "separate 120-minute certification block"; 08 reserves "180 min maximum" plus a separate 120-minute E2E block. | In 04 4.3 replace 120 with 180 minutes, explicitly distinguish the separately scheduled 120-minute E2E block, and say that all certification checks and controls must pass before filming a commit. | 180 - 120 = 60 min discrepancy; 08 allocates that 60 minutes to six attacks and their controls. |
| VP-02 | medium | 04 4.6; 08 8.2 | The Friday baseline's start time and duration disagree with the funded schedule and overlap the voice capture block. | 04 says "Friday 20:15-22:15"; 08 allocates voice capture 19:35-20:20 and baseline 20:20-22:15. | Change 04 4.6 to Friday 20:20-22:15, 115 minutes, and identify 08 as schedule authority. | 5 minutes overlap; the stated baseline is 120 minutes versus 115 funded. |
| VP-03 | medium | 04 4.3 and 4.6; 08 8.2 | The comprehension gate depends on two unfamiliar viewers, but the solo schedule neither reserves their availability nor defines a fallback if they are unavailable or fail after the editing box. | 04 demands "two unfamiliar viewers" both identify the router and outcome; 08 only budgets final takes/review and edit without recruiting or a failed-review decision. | In 04 4.3 and 08 8.2 reserve outreach before filming and a bounded review in the final-takes/edit block; if either viewer is unavailable or fails, simplify and retest within the box, then submit the best legible available cut and explicitly report the viewer gate as unverified, preserving submission time. | 2 independent viewers required, 0 identified and 0 explicit minutes or failure decision allocated. |

## Verified facts


- The [event page](https://www.wemakedevs.org/hackathons/switch) asks entrants to use Flow for prompts, room instructions and README, and add a desktop Insights screenshot. It permits the Wispr track alongside any track. The [organizer's submission and judging page](https://www.devtoolsacademy.com/hackathons/flip-the-switch) gives the 30/25/25/20 weights and requests a public repo, short running-workflow video and reproducible README. A non-running fallback has uncertain eligibility. Authenticated form fields and screenshot acceptance were not inspected.
- [Wispr Insights documentation](https://docs.wisprflow.ai/articles/8760230576-your-usage-tab-track-your-dictation-stats-in-wispr-flow) says Insights is desktop only, total words combine desktop and mobile, heatmap dates use UTC, and manual retries depend on the displayed failure. UTC midnight is 05:30 IST. Prior citation checks were reused for unchanged vendor claims. Three web page opens were used.
- The scorecard arithmetic in 09 9.6 is correct: booking 24 + 16.25 + 13.75 + 14 = 68; stale 24 + 17.5 + 16.25 + 15 = 72.75; full release 27 + 20 + 18.75 + 17 = 82.75. Priorities are 4/8, 7/8 and 7/8. These are subjective, conditional estimates and not earned points.
- The 04 4.3 expanded rows are 20 + 15 + 30 + 25 + 20 + 30 + 15 + 50 + 15 + 10 = 230 seconds. At 120 words per minute, maximum narration plus minimum holds is respectively 20 including opener transitions, 15, 18.5, 15.5, 16, 18, 13, 25.5, 12.5 and 10 seconds. The zero-spare rows require exact execution or cuts; other rows have 2-24.5 seconds for interactions and transitions, not proof of feasibility. Reduced and proposal cuts each span 120 seconds; the expanded optional section from 1:30 to 3:25 is 115 seconds, while the overall cuts differ by 110 seconds because other shots shift. The plan requires measured rehearsal, a worksheet and cuts.
- Seed reasoning: 15:30 plus a 15-minute cleaning gap is 15:45; a 60-minute booking ends at 16:45, within the 17:00 limit. The treatment grid is 6 x 7 = 42 wells and column 5 maps to 8 ug/mL. Booking uses the funded people, instrument and booking fixtures; optional protocol, citation and plate shots require separately built fixtures. The seed and live workflow were not executed here.
- The scheduled certification sums to 25 + 35 + 25 + 20 + 15 + 60 = 180 minutes; the separate E2E block is 120 minutes. The voice reel consists of three 15-25-second clips, or 45-75 seconds of source footage, within an estimated 45-minute capture box. The 19:00 submission target leaves 4 hours 59 minutes to 23:59. The $100 / 4 hours upper bound is $25/hour; the illustrative operating cost is $12 + (2 + 10/60) x $20 = $55.33 rounded. Ten notes x four fields equals 40 checks per modality. None of these figures establishes measured execution time.
- Actual permission behavior, installed runtime, seed generation, voice evidence, viewer comprehension, logged-in form and submission remain unverified. The plan specifies bounded certification and failure paths; VP-01 concerns contradictory instructions for the certification cap, not missing live proof.
