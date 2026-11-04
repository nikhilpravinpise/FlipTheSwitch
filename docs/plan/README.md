# LabQuorum: master plan

Request a shared lab resource in a Switch room, review the exact proposal, and see which results become stale after corrected data. The target is a solo Windows build using Wispr Flow Pro. Submission is through the website Submit form by Saturday 2026-11-07 23:59 IST (18:29 UTC); target 19:00 IST, leaving 4 h 59 min. Inspect the form manually before relying on its fields.

## Pitch and mechanism

A student asks `@labops` for a plate-reader slot. It checks the seeded rules and hands a proposal to `@pi-desk`. Switch and the provider enforce the eligible human decision on the certified installed runtime; the ledger compares the visible canonical decision payload and revision in its transaction and enforces lab invariants. The builder plays both student and PI. If the native gate fails certification, use a separately tested steward or disable binding commits. Direct invocation by the same OS user is outside this boundary; a ledger hash is not an authenticated human receipt. Each binding request needs its own decision; use Allow once.

The four-agent, one-room core is `@labops`, `@scout`, `@pi-desk` and `@analyst`: a booking, a pinned citation fixture, a synthetic CSV, a descriptive figure and a small stale check. Helpers can record observations and drafts. Booking is the only binding core action; local purchase-request approval, protocol release and final research release are roadmap and would require a permitted linked human decision through the tested gate. A local purchase request does not place an order or change stock. If the schedule slips, cut literature and assay first. If implemented and tested, changed evidence blocks release through LabQuorum until a fresh eligible-human decision on current artifacts; stale artifacts remain readable. Otherwise demonstrate stale detection only. Citation metadata and retraction signals do not establish claim support.

## What is new

Switch already supports agent rooms, routing and approvals; human review in scientific agents is also prior art ([Switch](https://github.com/sandbox-quantum/switch/blob/main/docs/official/using/hand-off-work.md), [Agent Laboratory](https://arxiv.org/html/2501.04227v1)). The proposed contribution is their lab-specific combination: a visible eligible-human decision bound to a revision plus a dependency trail that can make a corrected dataset invalidate its downstream result. Its advantage over existing tools is a hypothesis, not measured demand or a proven unique feature; see the [bounded comparison](01-problem-market-usp.md). Crossref supplies indexed retraction signals, not a complete guarantee of correctness ([Crossref](https://www.crossref.org/blog/retraction-watch-retractions-now-in-the-crossref-api/)).

## Decisions

| Decision | Selected | Detail |
| --- | --- | --- |
| Human gate | Certified native card; separately tested steward or proposal-only fallback | [Architecture](03-architecture.md) |
| Scope | One room and four agents; fifth agent and second room are roadmap | [Product](02-product.md) |
| Execution | Claude Code, Python, SQLite; fixed descriptive analysis | [Architecture](03-architecture.md) |
| Evidence | OpenAlex and Crossref; pinned labeled fixture, human claim review | [Testing](06-testing.md) |
| Demo | 3:50 target, 4:00 internal ceiling; truthful conditional stale sequence | [Demo](04-demo.md) |
| Delivery | Friday baseline, Saturday clean room and final recording, submit by 19:00 | [Schedule](08-build-schedule.md) |
| Tradeoffs | Explicit weighted alternatives, costs, risks and revisit triggers | [Decision record](10-decision-record.md) |

## Numbers and first actions

The Thu 00:20 reforecast is 38 h 10 min scheduled work including 1 h 55 min defect slack and 30 min submission; rebase on the actual clock. Full scope is estimated at 71-109 h. The proposed catalogue has 186 planned test IDs and 120 planned edge cases, not executed results. The schedule has S0-S8 with S3 split into four checks, 12 named checks in total; S5 is deferred. A 3:50 video is the target, not a published event limit. The scorecard is 68.5/100 baseline and 82.75 only after all evidence gates; reduced scope is independently estimated at 66.5 under its stated assumptions ([09](09-submission-and-risks.md)).

1. Wispr Flow Pro is redeemed. Capture a baseline Insights screenshot and test mention-first dictation; final Insights by Saturday 18:00, attach and check by 18:30. Free Windows defaults warn above 2,000 and block above 5,000 weekly words, subject to account/platform changes ([Wispr](https://docs.wisprflow.ai/articles/4760791189)).
2. Manually inspect the Submit form and record actual fields; verify time remaining. Run S0 and identity checks, then certify effective provider tools, permissions and fresh decisions on the installed versions. Record actual failures and timings.
3. Build and test the booking loop first. Record one causal baseline Friday, preserve the submission buffer, and label synthetic data, builder-played personas and replayed API responses.

## Plan index

| File | Contents |
| --- | --- |
| [01](01-problem-market-usp.md) | Competitor and incumbent landscape and bounded comparison |
| [02](02-product.md) | People, agents, scope and cut lines |
| [03](03-architecture.md) | Authority boundary, data model, APIs and analysis |
| [04](04-demo.md) | Script, evidence and fallbacks |
| [05](05-wispr-flow.md) | Voice workflow and evidence |
| [06](06-testing.md) | Planned tests and evaluation |
| [07](07-edge-cases.md) | Failure modes and coverage |
| [08](08-build-schedule.md) | Spikes, schedule and cuts |
| [09](09-submission-and-risks.md) | Submission, scoring and risks |
| [10](10-decision-record.md) | Weighted decision record |
| [Templates](templates/README.md) | Draft templates and fixtures |
| [Reviews](../review/round1/) | Findings, editor changes and integration log |
