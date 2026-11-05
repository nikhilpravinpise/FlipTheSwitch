# Demo script - target 2:15, hard cap under 3:00

Production draft. Record one genuine causal run with synthetic lab records and two real teammates: Nikhil as PI and Darshan as student. Binding shots are conditional on the complete P4 certification for the installed tuple, including refusal, complete card and fresh consent. Capture actual waits and caption edits. Source: `docs/build/team-impact.md`, `docs/build/PHASES.md`, `docs/submission-fields.md`.

| Time | Shot and on-screen caption | Spoken line | What Switch must visibly show |
| --- | --- | --- | --- |
| 0:00-0:15 | Both people and shared room. Caption: "Synthetic lab data; Darshan: student, Nikhil: PI" | Darshan: "Shared instruments get booked fast. I need a slot without a scheduling back-and-forth." | The real room, both display names and agent members. |
| 0:15-0:35 | Darshan uses Wispr in the chat input, checks the mention and sends. Caption: "Voice-assisted request" | Darshan: "@labops, can I book the instrument for an hour?" Specify the actual requested date and time. | The addressed message and `@labops` response in the same room; Flow is text entry, with deliberate send. |
| 0:35-0:55 | Hold on conflict and alternative. Caption: "Conflict: 14:00-15:30; proposed: 15:45-16:45" only if the run shows those values. | Darshan: "That conflicts with an existing booking. LabOps found a later slot." | Named conflict, alternative, request ID and routing to `@pi-desk`; use the actual values if different. |
| 0:55-1:12 | Darshan tries to address or answer `@pi-desk`. Caption: "Student cannot approve" only if observed. | Darshan: "I can request it, but I cannot approve my own decision." | Actual refusal for the distinct student identity, and no unauthorized commit. |
| 1:12-1:35 | Nikhil's view; hold the complete native approval card long enough to read. Caption: "PI reviews this exact request - Allow once" | Nikhil: "I review the requester, instrument, time, revision and decision before allowing it." | Handoff to PI-owned `@pi-desk`; actual card, identity, complete fields and Allow once. Never draw a card. |
| 1:35-1:52 | Show matching committed booking and audit entry. Caption: "Committed booking and audit" | Nikhil: "The booking and its audit record now match the approved request." | Actual result and request-linked audit, from the same run. |
| 1:52-2:05 | Show the room and relevant boundary. Caption: "Fail closed when approval cannot be verified" | Nikhil: "Pull the plug on the approval path and binding stops. A proposal is not a booking." | Show a real tested failure only if captured; otherwise present this as the design, not a demonstrated test. |
| 2:05-2:15 | README and setup. Caption: "Reproduce: README - release and clean install pending" | Darshan: "The README explains the Switch room, setup and the limits." | Actual repository and readable reproducibility instructions. |

## Proposal-only fallback

If any certification fails or is incomplete, disable binding commits. Replace 0:55-1:52 with the actual unapproved proposal and caption "Proposal only - no approval shown; booking status unverified." Say: "The approval boundary is not certified, so we stop at a proposal." Claim no booking was created by this request only if a timestamped request-scoped ledger query proves it. Do not show a simulated refusal, card, approval or committed booking. If no real room and proposal works, label the artifact non-running and do not imply live operation. Source: `docs/plan/04-demo.md`, `docs/build/team-impact.md`.

Before export, verify each caption against footage, retain raw run and actual waits, and ensure final duration is strictly below 3:00. Wispr clips and usage card are pending until actually captured. Source: `docs/plan/05-wispr-flow.md`, `docs/submission-fields.md`.
