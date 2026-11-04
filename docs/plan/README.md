# LabQuorum: master plan

A researcher asks for a shared instrument in a Switch room; the agent proposes a conflict-free slot and an eligible human reviews the exact decision. This is a solo Windows build with Wispr Flow Pro redeemed. Submit through the website by Saturday 2026-11-07 23:59 IST; the working target is 19:00 IST, leaving 4 h 59 min contingency. Inspect the authenticated form in the next available session before packaging.

## Mechanism and scope

`@labops` checks seeded booking rules and routes a proposal to `@pi-desk`. A native Switch permission card is usable for a binding booking only after the installed runtime passes the identity, effective-tool, repeated-consent and full-card tests. The transaction compares the canonical action-specific payload, hash and revision and enforces booking invariants. Use Allow once for each decision; fail closed on truncated or oversized cards. A ledger hash is not an authenticated human receipt, and a malicious process running as the same OS user is outside this boundary. If certification fails, disable binding commits and show a proposal-only workflow; a separately tested steward is currently unfunded. See [architecture](03-architecture.md) and [tests](06-testing.md).

If certification fails, the filmed workflow is proposal-only: an unapproved alternative and no committed booking, subject to recorded status evidence. The funded baseline is booking only, in one room with `@labops`, `@scout`, `@pi-desk` and `@analyst`. Literature, synthetic analysis, stale detection, inventory and release are deferred until separately scheduled and tested. The builder plays the student and PI using distinct accounts. An expanded demo may show stale descendants after a correction; claiming blocked release and renewed approval requires the complete, separately tested cycle. Citation metadata and retraction signals do not prove claim support. See [scope](02-product.md) and [demo](04-demo.md).

## What could be new

Switch already provides agent rooms and routing, and scientific-agent systems already use human feedback ([Switch](https://github.com/sandbox-quantum/switch/blob/main/docs/official/using/hand-off-work.md), [Agent Laboratory](https://aclanthology.org/2025.findings-emnlp.320/)). The hypothesis is a lab-specific combination of a decision bound to a revision and a dependency trail connecting corrected evidence to a later release decision. This combination is proposed, not established as unique or superior; the funded booking prototype does not demonstrate that full loop. The [market comparison](01-problem-market-usp.md) describes the evidence and its limits. Crossref exposes retraction signals, whose absence does not prove a source reliable ([Crossref](https://www.crossref.org/blog/retraction-watch-retractions-now-in-the-crossref-api/)).

## Decisions

| Decision | Choice | Detail |
| --- | --- | --- |
| Approval | Certified native card; proposal-only if certification fails; steward unfunded | [Architecture](03-architecture.md) |
| Scope | One room, four agents, booking-only funded baseline | [Product](02-product.md) |
| Build | Claude Code, Python, SQLite and MCP, with gate-only CLI fallback only if separately tested | [Architecture](03-architecture.md) |
| Research evidence | OpenAlex and Crossref, pinned labeled fixtures and separate human claim review; deferred | [Testing](06-testing.md) |
| Demo | Booking-only cut; expanded evidence and stale sequence only if built and tested | [Demo](04-demo.md) |
| Delivery | Friday baseline; Saturday clean room, recording and website submission | [Schedule](08-build-schedule.md) |
| Alternatives | Weighted choices and revisit triggers | [Decision record](10-decision-record.md) |

## Numbers and first actions

The Thu 00:20 booking-only forecast is 40 h 10 min including 1 h 40 min defect slack, 15 min Insights retry and 30 min submission; literature and assay are deferred. Rebase on the actual clock; elapsed time cannot be recovered. Full scope was estimated at 71-109 h. The catalogue contains 187 planned test IDs and 120 planned edge cases, not executed results. The 3:50 expanded video and 2:00 booking-only cut are internal targets, not published limits. The unbuilt plan has no earned score; conditional booking-only, separately funded stale-detection and full-release projections are 68, 72.75 and 82.75 out of 100; no score is earned, and proposal-only has no projection. See [submission and risks](09-submission-and-risks.md).

1. Inspect the Submit form and record its actual fields and limits. Capture the Wispr Insights baseline and test mention-first dictation; capture final Insights by Saturday 18:00 and attach and check by 18:30.
2. Rebase the [schedule](08-build-schedule.md), run server, identity and permission spikes, build the behavioral red harness, and record versions, results and timings. The self-host fallback remains unavailable until its separate preflight succeeds.
3. Implement and test the booking loop and the mandatory decision gates. Record a causal Friday baseline, label synthetic material and role-play, and preserve the submission window. If the gate fails, demonstrate proposals only.

## Plan index

| File | Contents |
| --- | --- |
| [01](01-problem-market-usp.md) | Market, prior art and bounded claims |
| [02](02-product.md) | People, agents, scope and cut lines |
| [03](03-architecture.md) | Authority boundary, state, APIs and analysis |
| [04](04-demo.md) | Script, evidence and fallbacks |
| [05](05-wispr-flow.md) | Voice workflow and evidence |
| [06](06-testing.md) | Planned tests and evaluation |
| [07](07-edge-cases.md) | Failure modes and coverage |
| [08](08-build-schedule.md) | Spikes, schedule and cuts |
| [09](09-submission-and-risks.md) | Submission, scoring and risks |
| [10](10-decision-record.md) | Weighted decision record |
| [Templates](templates/README.md) | Draft templates and fixtures |
| [Reviews](../review/) | Findings, editor changes and integration logs |
