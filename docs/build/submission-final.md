# Submission text

Evidence basis: `docs/build/evidence/p4/certification.json` and `docs/test-evidence.md` at v1.0.2 (`b1a5b14`), plus Darshan's Saturday retest once it is recorded. Paste each section below into the matching form field. The checklist at the end is not part of the submission.

## Project title

LabQuorum

## Tracks

Best Business Workflow; Code with Wispr

## Project description

Shared lab instruments are scarce, and a student who asks for time on one usually waits for someone to check a spreadsheet, spot a clash and reply. LabQuorum puts that workflow in the lab's Switch team chat. A student asks `@labops` for an instrument and a time window. LabOps checks the requester's training, the instrument's rules and existing bookings against a local ledger, names any conflicting booking and proposes the nearest free slot of the same length. The result is a pending request with an ID, not a reservation. Committing a booking is reserved for the PI: `@pi-desk` accepts messages only from its owner, and the commit tool runs only after the PI answers a native Switch approval card that shows the exact decision. Every proposal, decline and commit is recorded in a hash-chained audit log.

It is for lab members who need a clear answer about instrument time, and for PIs who want to approve bookings without losing the context. The current deployment is proposal-only: binding commits stay off until the remaining certification checks pass. Demo people and lab records are synthetic.

## GitHub repository URL

https://github.com/nikhilpravinpise/FlipTheSwitch

## Demo video

TODO(Darshan): checked unlisted YouTube link, under 3:00, verified while logged out.

## Live demo

Leave blank: the Switch Console deployment runs on a team laptop and is not a public instance.

## Blog post

TODO(Darshan): published article URL.

Pull requests: leave blank; we are not entering Best Core Contribution.

## Wispr usage card

Upload both cards exported at the end from Wispr Flow: Insights > Your usage > Share.

## #HowISwitch post

TODO(Darshan): public post URL.

## How did you use Switch in your project?

Switch is where the people and agents meet. We run Switch Console with two Codex agents, configured for `gpt-6-luna` with high reasoning effort and created from a LabQuorum room template: `rao-labops`, addressable by anyone as `@labops`, and `rao-pi-desk`, addressable only by its owner as `@pi-desk`. The template creates a private Mattermost room, `rao-labquorum`, bridged by Switch, with a lab handbook and bench-manager and approver roles. Both agents reach the booking ledger through a LabQuorum MCP server whose tool profile depends on the agent: LabOps can only read and propose, and only the PI desk profile can request a commit. The team joins the room over Tailscale with separate student and PI accounts.

What we verified on the live deployment:

- Proposal: LabOps named Dr. Lena Okafor's committed 14:00-15:30 booking and proposed 15:45-16:45 the same day. The request (AR-0042) stayed pending with no commit event and no approval card on the proposer side.
- Owner-only PI desk: when Darshan addressed `@pi-desk` from his student account, Switch itself refused the message. In the P4 run, the PI desk also refused Maya's request to approve on her behalf, and the ledger was unchanged.
- Approval path, in an isolated certification session on a test ledger: the native card showed the complete decision, the PI chose Approve once, and exactly one matching booking and one commit audit event were written (AR-0043). A PI decline left the request pending (AR-0044). A student's Approve answer did not settle the owner-only card (AR-0045). Two prompt-injection probes recorded matching cards and no commit (I-36, I-37).

What is not proven yet, and why binding stays off: the one-commit-per-process limit was not exercised live because no verified Console session ID was available; three of five injection probes (I-38 to I-40) failed before capturing a request or card; and no live trace showed the model and effort actually used. Darshan's real student run also exposed bugs (read-only tools prompting for approval, requester fixed to one person, card answers misread as training claims). Those were fixed and merged. TODO(Darshan): one sentence with the post-fix retest result (request ID, what the reply said, pending state), or delete this sentence if the retest did not happen. Evidence: `docs/test-evidence.md`.

## What did you like about Switch, and what would you improve?

Rooms, agent aliases, owner-only addressing and identity claims gave us a real human-plus-agent workflow without writing a chat integration. The owner-only refusal is enforced by Switch itself, and native approval cards let a person review the exact tool call before it runs.

What we would improve, from what we hit:

- Hosted agents must call `post_message` to be visible; their final assistant text is not shown in the room. Some live turns produced an activity summary and a pending proposal but no answer within three to five minutes, and the cause is still unverified. A clear default or a warning would help.
- Approval choices can persist for a session. Per-decision consent controls would make one-use approvals easier to guarantee.
- In our Codex 0.166.0 spike, server-initiated MCP elicitation was not forwarded to the app-server client and returned cancel, so we used Codex's native tool-call approval instead.
- After a Console relaunch, agents sometimes did not re-attach to the controller stream until reloaded, and running hosts could keep an old MCP configuration.
- Understanding global versus per-session Codex homes took time, and on first launch we had to repair the inherited Windows PATH so Docker's credential helper could be found. Clearer setup diagnostics and configuration visibility would help.

## Before submitting (not for the form)

- [ ] Replace the three link TODO lines with links that open while logged out.
- [ ] Resolve the retest TODO in the Switch section from issue #8 evidence. No TODO may remain in pasted text.
- [ ] Re-read `docs/build/evidence/p4/certification.json`; if any scenario changed, update both Switch sections to match.
- [ ] Confirm the repository is public and the README renders.
- [ ] Both Wispr cards exported after the last genuine dictation and attached.
