# 8. Build schedule

Back to the [master plan](README.md). All times IST; hard cutoff **Saturday 7 Nov 23:59**. The brief's starting assumption is Wed 4 Nov 22:45; the review checkpoint was Thu 5 Nov 00:20. Rebase each remaining block on the actual clock and record actual time; past slots are not available. Sleep and breaks are excluded from productive hours. The original blocks total 40.75 hours from 22:45, not 45; full scope is estimated at 71-109 hours ([engineering review](../review/round1/engineering.md)). Estimates below are assumptions, not measured velocity.

## 8.1 Day-1 spikes with go/no-go rules

Record installed versions, effective configuration hashes/revision, room/session/tool-call IDs, request revision/hash, displayed decision and ledger outcome in `docs/adr/000-spikes.md` and `docs/test-evidence.md`. Build the minimal two-person Playwright harness and observe a behavioral red before binding commit implementation (EN-03). Each box includes its result; stop on failure.

| Spike | Box | Pass / decision |
| --- | ---: | --- |
| S0 server | 90 min native + separately budgeted 60-90 min fallback if needed | Path A: fresh Windows Console native server and Docker Mattermost; run the installed Console smoke flow and verify one agent replies. Path B: follow the pinned [self-host guide](https://github.com/sandbox-quantum/switch/blob/main/docs/official/deploy/self-host.md) for a separate Linux/Docker Compose server and Mattermost, verify health, bridge URL and PI ownership, then Console **Connect to an existing server** and get one reply. Preflight B before relying on it; the precise installed commands/health URL are UNVERIFIED until recorded. No native/Docker toggle is assumed. If neither passes, stop binding demo. |
| S1 identity | 20 min | Open/unclaimed helper allowed, unclaimed owner-scoped PI refused, claimed owner allowed (EDGE-04). |
| S2 MCP and settings | 60 min | Separately test MCP discovery and effective permission enforcement. If only MCP launch fails and enforcement passes, try a separate gate-only CLI settings profile without blanket Bash deny and rerun the entire approval suite. If settings enforcement fails, CLI is not a remedy; select steward or disable commits. [Permission precedence](https://code.claude.com/docs/en/permissions) checks deny first. |
| S3a-c approval | 60 min | Wrong person refused, two same-session calls each gated, agent yes ignored; inject hook missing/crash/bad JSON/timeout/bypass and unknown mode. Record card and ledger separately. |
| S3d boundary | 75 min | Inventory effective offered tools and policies; reproduce then block same-owner policy widening, unexpected native and MCP tools, forbidden read/shell/attachment; 0 unauthorized changes or commits. Include real runtime mode test. |
| S4 templates | 30 min | Import the one-room MVP template, check members and manual fallback; defer the second template. |
| S5 Codex | 0 min | Deferred: use one verified provider; optional only after all gates and deliverables. |
| S6 capacity | 20 min | Measure actual session and MCP process count, peak RAM and latency with active rooms and after three takes; stop old sessions, serialize tests, require >=20% RAM headroom. Two rooms may create 3 + 5R placements, not merely five. |
| S7 literature | 20 min | Pin only the chosen real, retracted and intentionally fabricated fixtures, label each; otherwise omit citation beat. |
| S8 submission | 10 min | Inspect website Submit form, record actual fields, limits and screenshot route; unknown fields remain UNVERIFIED. |

Decision by end of S3: native card only if all installed-runtime gates pass. A trusted steward is an alternative only if its identity, replay, revision, expiry, gap and outbox tests pass; allocate 3-5 hours from optional work and rewrite every affected deliverable. Otherwise disable binding mutations and explicitly present a proposal-only demo. A same-OS-user direct invocation is outside the native boundary; record the probe and do not claim ledger-authenticated approval.

## 8.2 Hour by hour

Reforecast at Thu 00:20 checkpoint: 38 h 40 min scheduled work including 1 h 55 min defect slack and 30 min submission; 4 h 59 min later calendar contingency remains after the target submission. The schedule is contingent on S0 path A; path B costs 60-90 min and consumes defect slack or displaces the citation beat. No unpaid overlap between tasks. Windows are illustrative and must be shifted if the actual start differs.

| IST | Work and checkable exit | Hours |
| --- | --- | ---: |
| Thu 00:20-01:00 | S8, baseline Wispr screenshot, begin S0 | 0.67 |
| Thu 01:00-08:00 | Sleep | 0 |
| Thu 08:00-09:30 | Finish S0 and S1; one responding agent and identity table | 1.5 |
| Thu 09:30-11:30 | S2 and S3a-c, build minimal browser harness and red test | 2 |
| Thu 11:30-12:45 | S3d permission boundary; ADR choice | 1.25 |
| Thu 12:45-13:30 | Lunch | 0 |
| Thu 13:30-16:30 | Minimal booking rules, transactional store and race test | 3 |
| Thu 16:30-18:30 | MCP profiles, real proposal, wrong-person and PI decision end to end | 2 |
| Thu 18:30-19:30 | Break | 0 |
| Thu 19:30-22:30 | S4, seed, basic UI and initial evidence; critical loop green | 3 |
| Thu 22:30-Fri 07:00 | Sleep | 0 |
| Fri 07:00-10:00 | Minimal citation verifier and pinned fixtures (S7); cut if core loop not green | 3 |
| Fri 10:00-12:00 | Synthetic descriptive assay, one corrected well and stale flag, reproducible output; no biological inference | 2 |
| Fri 12:00-12:45 | Lunch | 0 |
| Fri 12:45-15:45 | Selected end-to-end tests, recorded models, clean fixture reset; S6 | 3 |
| Fri 15:45-17:45 | README, setup and test evidence | 2 |
| Fri 17:45-18:45 | Break | 0 |
| Fri 18:45-20:45 | Baseline rehearsal and recording with future valid slot | 2 |
| Fri 20:45-22:45 | Blog, voice log, submission draft; feature freeze | 2 |
| Fri 22:45-Sat 07:00 | Sleep | 0 |
| Sat 07:00-09:00 | Run actual MVP gate, record timings and failures | 2 |
| Sat 09:00-10:00 | Clean-room setup against README | 1 |
| Sat 10:00-12:00 | Final takes or keep baseline | 2 |
| Sat 12:00-12:45 | Lunch | 0 |
| Sat 12:45-14:45 | Edit, caption, upload and verify logged out | 2 |
| Sat 14:45-16:00 | README, blog and links | 1.25 |
| Sat 16:00-17:55 | Defect and overrun slack, no features | 1.92 |
| Sat 17:55-18:30 | Final Wispr Insights screenshot, package and link audit | 0.58 |
| Sat 18:30-19:00 | Submit via website Submit form and save confirmation | 0.5 |
| Sat 19:00-23:59 | Submission contingency only | 0 |

Bottom-up forecast within the above blocks: setup, proof and harness 5.42 h; minimum domain/store/MCP loop 5 h; integration, seed and evidence 3 h; optional literature and descriptive assay 5 h; testing/capacity 5 h; docs/clean room 6.25 h; recording/edit 6 h; final package 0.58 h; defect slack 1.92 h; submission 0.5 h. These categories total 38.67 h, so they exceed the listed 38.67 h blocks by 0 h; actual durations and remaining available hours must be recalculated at each checkpoint. Critical path: S0 -> S1/S2/S3 -> red harness -> transactional booking -> real decision -> MVP gate -> baseline -> edit -> Submit. MVP target is one room and four agents: `labops`, `scout`, `pi-desk`, and `analyst` (also writes the fixed results paragraph), one booking kind, one citation fixture, one synthetic CSV, a descriptive figure and a stale check. Cut literature and assay only if the core path slips, and disclose the reduced demo. Protocol release, inventory orders, general bench parsing and external rooms are roadmap.

## 8.3 Escalation rules

| Trigger | Decision |
| --- | --- |
| S0 fails after 90 min | Spend 60-90 min on separately preflighted path B; cut optional work to pay for it. |
| Approval boundary unproven | No binding mutation; use a fully tested steward only if its 3-5 h fits, otherwise proposal-only. Never simulate a human authorization. |
| Critical loop late | Cut literature, analysis and extra agents first; preserve testing, evidence, baseline and submission. |
| Authorization or integrity red | Fix or remove affected capability; record failure. |
| Saturday recording late | Use Friday baseline; preserve final screenshot and Submit window. |

## 8.4 Core Contribution PR

Skipped by default: solo time is consumed by the critical path. Only consider after submission; the impact and remaining hours are otherwise unverified.
