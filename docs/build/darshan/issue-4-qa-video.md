# Issue #4: QA, accessibility and demo edit

Status: preparation and static review completed on 2026-11-05. Real-user chat QA, first-time live setup, screen-reader and keyboard checks, recording, editing and upload are UNVERIFIED. This file is a working handoff, not evidence that those activities passed.

## Static review actually performed

| Observation | Evidence | Result and implication |
| --- | --- | --- |
| At cloned baseline `86f71c3`, README contained only the project title and error-code table. | Baseline `README.md:1-37`; current `README.md` | Setup documentation blocker fixed locally: prerequisites, private-room onboarding, disposable-ledger commands, expected output and troubleshooting are now included. Live-room setup still needs its actual invitation. |
| Interval formatting includes weekday, date, time and a time-zone abbreviation; approval-card endpoints have their own local-time formatter. | `src/labquorum/domain/timeutil.py:112-140` | Useful source-level support. Actual chat wording, UTC-offset clarity and the abbreviation's intelligibility to a new user are UNVERIFIED. |
| Tool results retain error code, message and details; oversized JSON results become a short error. | `src/labquorum/mcp/tools_lab.py:42-61` | A transport byte cap is present. It does not establish short, understandable rendered chat replies or screen-reader compatibility. |
| Tool descriptions name instrument, requester, local endpoints, UTC endpoints, revision and hash. | `src/labquorum/mcp/profiles.py:42-60` | Relevant decision fields are described. Card visibility, order, truncation and reading order require live inspection. |
| Native human approval and runtime policy remain an explicit certification task. | `docs/build/codex-boundary.md:15-31`; `docs/plan/04-demo.md:4.3` | Ledger or MCP tests alone must not be described as proof of student refusal or authenticated PI consent. |
| No tracked `.mp4`, `.webm` or `.mov` source recording was found by the repository file search. | `rg --files -g '*.mp4' -g '*.webm' -g '*.mov'` returned no match (exit 1). | A real video cannot yet be edited from this checkout. |

No GitHub issue was filed and no live finding was invented. Parent-run dependency and test results belong in the session evidence separately.

## Setup finding resolved locally

The following records the baseline finding. The current README fixes the missing instructions, so do not file it as an unresolved missing-documentation issue. CLI initialization, seeding, audit verification and diagnostics passed against a disposable TEMP ledger in this session. See [verified facts](../facts-for-blog.md) for exact commands and limits.

Title: `First-time setup: README has no installation or room-join instructions`

- Context: fresh checkout of this revision, Windows, first-time LabQuorum user.
- Steps: open the repository root README and follow its instructions without consulting internal build plans.
- Exact visible text: `# FlipTheSwitch`, followed by `## Error codes` and the error-code table.
- Expected: prerequisites, install command, configuration, private-room onboarding, example request, success criteria and troubleshooting.
- Actual: there is no runnable setup sequence or room-join path.
- Impact: new users cannot perform the Saturday setup test from the README.
- Screenshot: capture the actual rendered README before filing; not captured in this static review.
- Source: `README.md:1-37`.

## Live QA procedure

Run as Darshan's own student account when Nikhil supplies the actual private Mattermost address and invite. Use synthetic lab data. Record the exact deployed revision, Console/provider versions, room, account role, instrument, anchor date and IANA time zone. Save private URLs and credentials outside the repository. Do not initialize or reseed the shared ledger while another take is running.

1. Join from a clean browser session and record every unclear setup step. Use the README verbatim first; record any help received so this remains an honest first-time test.
2. Discover available instruments as a new student: `@labops, which instruments can I book?` Capture the exact reply. Check that names and training requirements are understandable without reading internal identifiers alone.
3. After confirming the live seed date, send: `@labops, propose a 60-minute plate-reader booking on YYYY-MM-DD between 14:00 and 17:00 Asia/Kolkata.` Replace the date explicitly. Preserve the exact sent text and reply. Check the returned conflict, owner, alternative and cleaning gap against the actual ledger; do not assume the planned 15:45-16:45 alternative is the deployed result.
4. As the student, try the actual approval control presented for that request once. Expected: refusal and zero request-scoped booking mutation. Record the full refusal and a timestamped request-ID-scoped ledger check. If no approval control exists because binding is disabled, record NOT TESTABLE rather than a refusal pass.
5. Read the alternative aloud without coaching: instrument, calendar date, start, end, time zone, requester and pending/committed state. Compare the local values with the corresponding UTC fields. Ask for clarification if needed and preserve the reply.
6. Enter an ambiguous date in a separate read/propose request, such as `tomorrow afternoon`. Expected: the agent obtains a definite date/time before creating a binding decision. Record actual behavior; the MCP ISO-input contract does not prove the agent's natural-language handling.
7. With keyboard only, navigate login, room, composer, mention selection, request, reply, and any eligible controls. Check visible focus, logical order, Enter/Space behavior and ability to leave a dialog. Do not test a PI-only confirmation while signed in as the student.
8. With the user's available screen reader, navigate the same conversation. Check names, message boundaries, status, table headers/rows, bold emphasis and card labels in reading order. Record reader/version and exact confusing speech. No screen reader used means UNVERIFIED.
9. Inspect the same messages in grayscale or without relying on color: conflict, refusal and pending status must have explicit text. At 200% browser zoom, check readable content and usable controls. Record actual browser/zoom and screenshots.
10. File each observed problem separately using the template below. Retest any fix against the same saved steps and distinguish first result from retest.

### One finding per issue

```text
Title: [QA or accessibility] <one concrete failure>
Environment: OS/browser; screen reader if used; product revision/versions
Account role: student/requester (no credentials)
Scenario: instrument/date/IANA zone; redacted request ID
Steps: exact actions in order, including keyboard keys
Exact user message: <copy from the actual conversation>
Exact agent message or spoken output: <copy verbatim>
Expected: <one observable result>
Actual: <one observable result>
Impact: <task the user could not complete>
Evidence: screenshot, timestamp, redacted transcript, relevant ledger check
Status: observed / fixed and retested / not reproducible
```

## 2:15 edit script, proposal-only baseline

This is a planned edit decision list. Every shot below must come from one real causal room run, with actual IDs and measured waits. No source footage is currently available in this checkout. The baseline deliberately makes no claim that a student refusal or native approval passed. If no live room and proposal work, replace the workflow with actual prototype artifacts and label the whole film `Non-running prototype`; do not narrate the following script over simulated chat.

Keep a visible `Synthetic lab data` label throughout. Identify any role-play accurately. Burn in the exact voiceover as captions, proofread terminology, use readable high-contrast text and preserve sufficient reading holds. Record raw waits and caption every omitted interval with its actual duration. Never speed up silently.

| Edited time | Required actual shot | Voiceover and matching caption |
| --- | --- | --- |
| 00:00-00:15 | Actual request and its returned alternative, with pending state readable. | "Shared laboratory instruments need clear booking decisions. LabQuorum is a booking prototype inside a Switch chat. This demonstration shows a proposal, not an approved booking." |
| 00:15-00:30 | Real room, student account label, instrument listing. Crop private connection details. | "The data is synthetic. I am using the student account. Switch connects the conversation to the agents; LabQuorum checks the instrument's booking rules." |
| 00:30-00:55 | Type or genuinely dictate the explicit date/time request. Show the exact sent message and a measured-wait caption if cut. | "I ask labops for a sixty-minute plate-reader session on this date, between two and five in Asia/Kolkata. The calendar date and time zone stay explicit." |
| 00:55-01:20 | Show actual conflict, owner, and suggested interval. Hold each important field; do not manufacture the planned alternative. | "The reply checks the existing schedule and proposes an alternative. Here are the actual instrument, start and end times. A suggestion is still pending; it is not a reservation." |
| 01:20-01:40 | Show the same request's pending record and actual certification status. Optional timestamped request-scoped ledger query only if run. | "Human approval needs separate verification on the installed Switch configuration. That certification is not established here, so this cut makes no claim of an authenticated approval or completed booking." |
| 01:40-01:55 | Actual readable conversation close-up. If real voice capture exists, show it with its true status; otherwise keep the conversation. | "The user review checks clear errors, explicit time zones, keyboard navigation and screen-reader reading order. Those checks are recorded individually, including any failures." |
| 01:55-02:15 | Actual repository and current output; honest status card and repository link. | "This is the booking-only scope. Literature, analysis and inventory are future work. The current output is the proposal shown here. Live approval, accessibility results and setup evidence must be reported as they are verified." |

The 135-second timeline leaves reading time within each row; voiceover length and interaction time must be rehearsed against actual footage. Cut words or optional shots if necessary, keeping the request, response and status legible. Never claim no booking was created unless a timestamped query scoped to this same request proves it; otherwise caption `Booking status unverified`.

If native certification later passes, replace only the 01:20-01:40 row with the real same-request student refusal, eligible PI's fresh one-use decision, and scoped committed record. Require version tuple, full visible canonical fields, repeated-consent and bypass results before changing the narration. Do not stitch different takes into an implied single transaction.

## Export and issue completion

- Obtain the real workflow recordings and shot list from Nikhil; retain raw footage and a source-run/cut log.
- Edit the strongest complete causal run to 2:15, always below 3:00. Add captions and recorded voiceover. Export a video file and inspect duration, caption timing, audio and key message legibility.
- Watch the export at 720p and ask two unfamiliar viewers to identify Switch's role and the current booking state without pausing. Record the result rather than assuming a pass.
- Upload to the user's YouTube account as unlisted only when account access and the final cut exist. Open the link while logged out, play it, verify duration and audio, then post the checked URL to issue #4 under the authorized completion workflow.
- Attach observed QA findings separately. Do not close #4 until real-user QA, accessibility review, verbatim first-time setup, final export and logged-out playback are all evidenced.

Current blockers: no live room/invite supplied in this task; human-boundary certification incomplete in the checked-in evidence; no real source recording or edited/uploaded video available. Browser access reports that its host is unavailable. Live keyboard/screen-reader behavior and playback remain UNVERIFIED. The missing README instructions have been repaired locally.
