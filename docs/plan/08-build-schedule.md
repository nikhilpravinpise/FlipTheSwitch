# 8. Build schedule

Back to the [master plan](README.md). All times IST; hard cutoff **Saturday 7 Nov 23:59**. The brief's starting assumption is Wed 4 Nov 22:45; the review checkpoint was Thu 5 Nov 00:20. Rebase each remaining block on the actual clock and record actual time; past slots are not available. Sleep and breaks are excluded from productive hours. The original blocks total 40.75 hours from 22:45, not 45; full scope is estimated at 71-109 hours ([engineering review](../review/round1/engineering.md)). Estimates below are assumptions, not measured velocity.

## 8.1 Day-1 spikes with go/no-go rules

Certification, the harness, and behavioral red have separate time blocks below. Of the 115-minute late block, 100 minutes is defect slack and 15 minutes is reserved for Insights retry; neither funds optional features. Certification has its own 120-minute block; its estimate is unmeasured and a timeout fails closed. All timings are estimates until measured.

Record installed versions, effective configuration hashes/revision, room/session/tool-call IDs, request revision/hash, full displayed decision and ledger outcome in `docs/adr/000-spikes.md` and `docs/test-evidence.md`. Build the minimal two-person Playwright harness and observe a behavioral red before binding commit implementation (EN-03). Each box includes its result; stop on failure.

| Spike | Box | Pass / decision |
| --- | ---: | --- |
| S0 server | 90 min native + separately budgeted 60-90 min fallback if needed | Path A: fresh Windows Console native server and Docker Mattermost; run the installed Console smoke flow and verify one agent replies. Path B: follow the [self-host guide](https://github.com/sandbox-quantum/switch/blob/main/docs/official/deploy/self-host.md) for a separate Linux/Docker Compose server and Mattermost, verify health, bridge URL and PI ownership, then Console **Connect to an existing server** and get one reply. Preflight B before relying on it; pin and record actual image digest, Compose version, exact commands, health endpoint and bridge URL; these remain UNVERIFIED until the 90-minute preflight succeeds. No native/Docker toggle is assumed. If neither passes, stop binding demo. |
| S1 identity | 20 min | Open/unclaimed helper allowed, unclaimed owner-scoped PI refused, claimed owner allowed (EDGE-04). |
| S2 MCP and settings | 60 min | Separately test MCP discovery and effective permission enforcement. If only MCP launch fails and enforcement passes, try a separate gate-only CLI settings profile without blanket Bash deny and rerun the entire approval suite. If settings enforcement fails, CLI is not a remedy; select steward or disable commits. [Permission precedence](https://code.claude.com/docs/en/permissions) checks deny first. |
| S3a-c approval | 60 min | Use a nonbinding synthetic gated stub: wrong person refused, two same-session calls each gated, agent yes ignored; inject hook missing/crash/bad JSON/timeout/bypass and unknown mode. Record card and stub state separately. Repeat on actual commit tool during the Friday E2E gate; either failure disables binding. |
| S3d boundary | 75 min | Inventory effective offered tools and policies; reproduce then block same-owner policy widening, unexpected native and MCP tools, forbidden read/shell/attachment; 0 unauthorized changes or commits. Include real runtime mode test. |
| S4 templates and fixture | 30 min | After S0 and before S1, lint and import the booking-only core template, create two distinct local synthetic PI and Maya test users, enroll them in the private room and prove both can post. Use one real organizer identity; local test users are not event registrations. If fixture fails, stop dependent tests and binding. Defer other templates. |
| S5 Codex | 0 min | Deferred: use one verified provider; optional only after all gates and deliverables. |
| S6 capacity | 20 min | Measure actual session and MCP process count, peak RAM and latency with active rooms and after three takes; stop old sessions, serialize tests, require >=20% RAM headroom. Two rooms may create 3 + 5R placements, not merely five. |
| S7 literature | 0 min | Deferred; no citation beat in funded baseline. |
| S8 submission | 10 min | Inspect the authenticated Submit form, record fields and limits, and test whether it accepts an accessible complete Insights screenshot through an actual form-supported route. If acceptance cannot be established within 10 minutes, seek organizer clarification and mark Wispr entry uncertain; submit core on time. A README link alone is not proven accepted; the [event page](https://www.wemakedevs.org/hackathons/switch) requests a Wispr scorecard but does not establish the authenticated form route. |

S3 is preliminary; native binding is permitted only after the full Friday installed-runtime gates pass, including I-14, I-23, I-29 and E2E-01-06 and 10-13. Truncated or oversized decisions fail closed. A steward needs 3-5 additional hours and its identity, replay, revision, expiry, gap and outbox tests; it is not funded in this forecast. Otherwise disable binding mutations and explicitly present a proposal-only demo. A same-OS-user direct invocation is outside the native boundary; record the probe and do not claim ledger-authenticated approval.

## 8.2 Hour by hour

Reforecast at Thu 00:20: 40 h 10 min including 1 h 40 min defect slack, 15 min Insights retry, a separate 2 h certification and 30 min submission. Rebase on the actual clock; elapsed time cannot be recovered. The funded baseline is booking only. Literature, assay, inventory holds, release and bench parsing are deferred; 22 mL is background, not evidence of a hold. Stale detection may be shown only if separately built and tested; no release claim without separately funded certification.

| IST | Work and checkable exit | Time |
| --- | --- | ---: |
| Thu 00:20-01:00 | S8 10 min, Wispr baseline 10 min, start S0 20 min | 40 min |
| Thu 01:00-07:30 | Sleep | 0 |
| Thu 07:30-09:30 | Finish S0 70 min; S4 fixture 30 min; S1 20 min | 120 min |
| Thu 09:30-11:30 | S2 60 min and S3a-c 60 min | 120 min |
| Thu 11:30-12:45 | S3d effective boundary | 75 min |
| Thu 12:45-13:30 | Lunch | 0 |
| Thu 13:30-15:00 | Build two-person harness, isolated ledger and behavioral red before commit implementation | 90 min |
| Thu 15:00-16:30 | Booking policy and conflict tests: 60-minute request within 14:00-17:00, alternative 15:45-16:45 | 90 min |
| Thu 16:30-18:30 | Transactional store, race and audit | 120 min |
| Thu 18:30-19:30 | Break | 0 |
| Thu 19:30-22:00 | MCP profiles, decision schema and negative tests | 150 min |
| Thu 22:00-Fri 07:00 | Sleep | 0 |
| Fri 07:00-09:00 | Expiry, both clock orders and lazy read, test first | 120 min |
| Fri 09:00-10:30 | Revision, stale rejection and fresh card, test first | 90 min |
| Fri 10:30-12:00 | Hook failures and real process/card integration | 90 min |
| Fri 12:00-12:45 | Lunch | 0 |
| Fri 12:45-14:45 | E2E-01-06 and 10-13, separate seeded states and resets; record each elapsed time | 120 min |
| Fri 14:45-16:15 | 15 required EV trials, resets and latency/error log | 90 min |
| Fri 16:15-18:15 | Separate installed-runtime certification: execute and log I-14, I-23, I-29, mode/bypass, restart and full-card checks; see procedure below | 120 min |
| Fri 18:15-19:45 | S6 20 min; blocker fixes and affected gate rerun 70 min | 90 min |
| Fri 19:45-20:15 | Break | 0 |
| Fri 20:15-22:15 | Booking-only or proposal-only baseline rehearsal and recording with valid future slot | 120 min |
| Fri 22:15-Sat 00:15 | README, test evidence, Wispr clips and submission draft; freeze | 120 min |
| Sat 00:15-07:00 | Sleep | 0 |
| Sat 07:00-08:30 | Rerun changed gate and log evidence | 90 min |
| Sat 08:30-09:00 | Break | 0 |
| Sat 09:00-10:30 | Clean-room README setup | 90 min |
| Sat 10:30-12:30 | Final takes or baseline; per-shot timing and 720p review | 120 min |
| Sat 12:30-13:15 | Lunch | 0 |
| Sat 13:15-15:15 | Edit, caption, upload and verify logged out | 120 min |
| Sat 15:15-16:30 | README 45 min and link audit 30 min; optional blog dropped | 75 min |
| Sat 16:30-18:25 | Defect and overrun slack 100 min plus a bounded 17:45-18:00 Insights refresh/retry 15 min; retain a timestamped prior complete screenshot if refresh fails | 115 min |
| Sat 18:25-18:30 | Package and check Insights attachment | 5 min |
| Sat 18:30-19:00 | Submit on website and save confirmation | 30 min |
| Sat 19:00-23:59 | Submission contingency only | 0 |

Bottom-up: setup/spikes 5 h 55 min; harness/red 1 h 30 min; booking/store/MCP 6 h; expiry/revision/hook 5 h; E2E/evals 3 h 30 min; separate certification 2 h; capacity/fixes 1 h 30 min; baseline 2 h; documentation and package 3 h 20 min; Saturday gate and clean room 3 h; final takes/edit 4 h; defect slack 1 h 40 min; Insights retry 15 min; submit 30 min. Total 40 h 10 min. Each estimate is unmeasured. E2E time includes resets, 2 x 2 min expiry holds and 3 x 30 s observations plus calls; EV includes 15 trials and resets. On overrun use slack; if the gate does not pass, disable binding and use a proposal-only demo, preserving submission time. Final Insights succeeds only when a complete accessible screenshot is submitted by a form-supported route; if unconfirmed, preserve the prior screenshot and label the Wispr entry uncertain.

**Separate certification procedure (120 min maximum):** after the behavioral-red harness and implementation, use the installed Console, provider, effective settings and the two local personas. Allocate 25 min to I-14 hook failure and mode injections, 35 min to I-23 effective-tool and bypass probes, 25 min to I-29 full-card/hash and truncation checks, 20 min to restart and persisted-mode checks, and 15 min to evidence and decision. Record versions, effective settings hashes, room/session/call IDs, inputs, card and durable ledger state. Pass only if every required injection blocks, no unauthorized action or commit occurs, the complete decision matches the transaction, and restart preserves the certified configuration. E2E-01-06 and 10-13 remain in their separate 120-minute block; they are not counted as certification time. Any failure, unexecuted step or timeout disables binding; film and package the proposal-only path. A changed tuple requires recertification.

Critical path: S0 -> S4 fixture -> S1/S2/S3 -> harness red -> booking/store/MCP -> expiry/revision/hook -> real runtime gate -> baseline -> clean room/edit -> Submit. The 100 min defect slack can pay for a 90 min server preflight, leaving 10 min; the 180-300 min steward is unfunded. Post-target contingency is 4 h 59 min. No optional work consumes slack without a new arithmetic reforecast.

## 8.3 Escalation rules

| Trigger | Decision |
| --- | --- |
| S0 fails after 90 min | Spend at most 90 min preflighting path B using defect slack, leaving 10 min; if not proven, stop binding. |
| Approval boundary unproven | No binding mutation; use a fully tested steward only if its 3-5 h fits, otherwise proposal-only. Never simulate a human authorization. |
| Critical loop late | Those features are deferred; if the gate cannot pass, disable binding and preserve evidence, baseline and submission. |
| Authorization or integrity red | Fix or remove affected capability; record failure. |
| Saturday recording late | Use Friday baseline; preserve final screenshot and Submit window. |

## 8.4 Core Contribution PR

Skipped by default: solo time is consumed by the critical path. Only consider after submission; the impact and remaining hours are otherwise unverified.

