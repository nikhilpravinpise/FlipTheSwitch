# Issue 3: Dev.to blog draft

Status: draft prepared on 5 November 2026. Not published. Genuine Wispr dictation has not been performed for this draft. The article uses directly inspected repository behavior and clearly labels runtime checks still needed. Session verification is recorded in [facts for the blog](../facts-for-blog.md). No live-room success, benchmark or user result is claimed.

Proposed platform: Dev.to. Proposed tags: `python`, `ai`, `opensource`, `productivity`.

## Article begins

# LabQuorum: making a lab booking proposal precise enough to review

A shared laboratory instrument can have several calendars at once: a spreadsheet, a chat conversation, and the person who remembers when the last experiment finishes. Someone asks for an hour on the plate reader. Another researcher already has a booking. A supervisor replies "approved," but the conversation has moved on to a different time.

LabQuorum explores a small part of that problem: turning a booking request into an explicit proposal that an eligible human can review. The intended place to have that conversation is a Switch room. The part available in this repository is a Python booking ledger and an MCP tool interface. The live Switch approval boundary still needs its own certification; a working tool call alone does not establish that a human approved it.

## Two agents, with different jobs

The booking baseline assigns `@labops` the proposer role and `@pi-desk` the approver role. Their tool lists differ.

The proposer can list instruments, check availability, and create a pending booking request. Its tool list does not include `commit_booking`. The approver can retrieve a request, check its policy, decline it, or submit its exact fields for commitment.

That distinction is useful for a first-time Switch user: asking for a booking and approving a booking are separate steps. It also has an important limit. A tool profile is not a human identity check. The installed Switch runtime must separately establish who may answer an approval request and whether each binding action receives a fresh decision.

The repository also reserves profiles for `@scout` and `@analyst`. Literature, analysis, inventory, and protocols are deferred. The baseline room focuses on the agents with booking work to do.

## A concrete conversation to try

Once the host has provided the private room and confirmed the current demo date, a student can start with an explicit request:

> @labops, can I book the plate reader on 9 November 2026 from 15:45 to 16:45 Asia/Kolkata for my assay?

This is an example prompt to try, not a transcript or a claim that this interval is free. Ask the agent to confirm the date, instrument, and time zone before proceeding. If the room has been reseeded for another day, use that day instead.

Underneath the conversation, booking tools require ISO 8601 datetimes with an explicit offset, such as `2026-11-09T15:45:00+05:30`. The tool descriptions specify that a conflict names the existing booking owner and provides the nearest free interval of the same length when one is available. The seeded requester is Maya; the prototype does not infer the student's identity from arbitrary tool arguments.

Read a proposed alternative carefully. A suggestion for 15:45 is a different decision from a request for 14:00. A pending proposal is also different from a committed booking. Ask for the request ID and its current state when the conversation is unclear.

## What the reviewer needs to see

The proposal contains an instrument ID and name, requester handle and display name, project text, local and UTC time endpoints, a request ID, a revision, and a content hash. The approver retrieves those same fields before committing.

The ledger compares the supplied revision, hash, and complete canonical decision against its stored request. It also checks booking policy inside the write transaction. Changing a time or another decision field should therefore require a matching current proposal rather than borrowing approval from an older version.

The implementation bounds the complete serialized proposal to fewer than 900 characters. That is a transport constraint, not proof of readable approval cards. Human identity, full card rendering, repeated consent, and the installed provider configuration need live checks. The build contract requires proposal-only operation if those checks fail. In that fallback, a demonstrated proposal must not be described as an approved reservation.

## Exploring the local ledger

Joining the team's live room is the light setup path: obtain the Tailscale connection and Mattermost invitation from the host, create your own account, and join as the requester. The server and agents run on the host's machine. You do not need to reproduce the host deployment just to participate in QA.

Developers can inspect the local ledger separately. The project declares Python 3.12 and uses `uv`. From a checkout, these commands match the current CLI parser and the repository's MCP notes:

```powershell
uv sync --locked
uv run lq init
uv run lq seed --demo --anchor-date 2026-11-06
uv run lq audit verify
uv run lq audit tail -n 5
```

This sequence is documented from inspected source; it still needs a clean-machine run before being presented as a verified quickstart. The anchor date controls the synthetic demo schedule and should be chosen deliberately. On Windows, the default ledger is `%LOCALAPPDATA%\LabQuorum\ledger.sqlite`; the implementation refuses a ledger under OneDrive. Keep demo state in the supported data location rather than beside a synced checkout.

`uv run lq doctor` provides diagnostics, including agent configuration checks. An incomplete host setup can report blocking errors. It is not a promise that cloning the source creates a working Switch room.

For MCP client development, `uv run lq-mcp --profile proposer` starts the proposer server over stdio after initialization. It is a protocol process for an MCP client, not an interactive chat prompt. The approver profile is for the separately controlled approver process; it should not be handed to the student to bypass the intended review.

## What this design teaches

The most useful lesson is to make the decision concrete before asking for consent. "Approve the booking" leaves too much implicit. An instrument, requester, local time, UTC time, revision, and request ID give the reviewer something specific to inspect.

A second lesson is to separate the ledger's checks from the chat platform's authority. A content hash can bind fields together. It cannot tell us which human clicked a button. An audit chain can reveal internal inconsistency. Without an external checkpoint, it cannot prove that no suffix was removed or that a whole chain was not recomputed.

Finally, local time is part of the decision. The project stores UTC values and includes readable local endpoints in the proposed decision. Clear dates and zones are especially valuable when a student and a supervisor are in different time zones.

## Honest limits

This is a booking prototype with synthetic people and instruments. It does not establish production readiness, clinical safety, or a complete laboratory management system. The live requester-to-approver flow, first-time setup, keyboard use, and screen-reader experience still require observed evidence. No timing or usability numbers are reported here.

The next useful test is deliberately ordinary: let a new lab member request an instrument without coaching, read the alternative, attempt self-approval, and explain what they believe has happened. Record the actual messages and ledger state. That evidence will tell us whether the precise decision in the backend also becomes a clear decision for the person in the room.

## Article ends

## Claim and publication checklist

| Article claim | Inspected source | Publication check |
| --- | --- | --- |
| Python requirement and CLI entry points | `pyproject.toml:6`, `pyproject.toml:14` | Source verified; run clean setup before claiming success. |
| Proposer and approver tool separation; seeded Maya | `src/labquorum/mcp/profiles.py:15`, `src/labquorum/mcp/profiles.py:22`, `src/labquorum/mcp/profiles.py:38`, `src/labquorum/mcp/profiles.py:86` | Source verified; do not equate profile separation with certified human authorization. |
| Exact decision comparison under a write transaction | `src/labquorum/store/repos.py:594`, `src/labquorum/store/repos.py:607`, `src/labquorum/store/repos.py:628` | Source inspected; no test execution result asserted. |
| Flat card fields and size constraint | `docs/build/p2-mcp.md`, `src/labquorum/mcp/tools_lab.py:410`, `src/labquorum/domain/approvals.py:124` | Inspect actual installed card before claiming readable/full rendering. |
| CLI commands | `src/labquorum/cli/main.py:48` | Commands are source verified, execution UNVERIFIED in this draft. |
| Default ledger path and OneDrive refusal | `src/labquorum/store/db.py:57`, `src/labquorum/store/db.py:94` | Source verified. |
| Two-agent baseline and light requester setup | `docs/build/resource-plan.md:15`, `docs/build/resource-plan.md:20` | Operational decision, not evidence of deployment. |
| Live certification and proposal-only fallback | `docs/build/PHASES.md:52`, `docs/build/PHASES.md:54` | Required behavior; current installed runtime UNVERIFIED. |
| Audit checkpoint limit | `docs/build/p1-ledger.md`, final paragraph | Source documentation reviewed; no stronger audit claim permitted. |

Before publication:

- Reconcile every claim with `docs/build/facts-for-blog.md` and the latest verified build state before publication. The local session checks establish ledger behavior, not live human approval or accessibility.
- Run the clean setup and record commands, outcomes, environment, and commit. Add only actual results.
- Replace the example with an observed, consented transcript if available; label synthetic data and role-play.
- Add only genuine screenshots with captions describing the observed state; do not invent assets or hide failures.
- Recheck the installed Switch provider and approval behavior against the certified tuple. Do not present earlier Claude adapter notes as proof of the current Codex runtime.
- Use Wispr for genuine revision work if desired, and record that separately. Do not retroactively claim this generated draft was dictated.
- Publish from Darshan's authenticated Dev.to account after reviewing the public text and verifying that the intended repository link is publicly accessible. Account access and permission to publish are UNVERIFIED in this session.
- Open the published article while logged out, then supply its URL for the requested GitHub issue comment. No publication or issue comment has been made.
- Optional social draft after publication: "I am building LabQuorum, a booking workflow for shared lab instruments inside Switch. Here is how we separate a proposal from an exact decision a human can review, plus the checks still needed: [published URL] #HowISwitch". Replace the placeholder and review the final claims before posting.

Issue 3 remains open until the reviewed article is published and its working URL is supplied. This file prepares the article; it is not evidence that the issue is completed.
