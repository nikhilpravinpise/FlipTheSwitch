# 8. Build schedule

Back to the [master plan](README.md). All times IST. Starts Wednesday 22:30, ends at the hard cutoff **Saturday 7 Nov 23:59**. About 45 focused hours; sleep is scheduled, not optional. Every build block is test-first: the listed tests are written and seen red before the code. Every decision goes into `docs/adr/` (dictated).

## 8.1 Day-1 spikes with go/no-go rules

Each spike is time-boxed, produces a screenshot and a one-paragraph result in `docs/adr/000-spikes.md`, and has a pre-decided fallback.

| Spike | Question | Pass | Fail -> decision | Box |
| --- | --- | --- | --- | --- |
| **S0** Server path | Does Console on Windows run a local server with bundled Mattermost and a Claude Code agent that answers in a room? | Official smoke test passes | Switch between the native and Docker-backed paths (issue [#1335](https://github.com/sandbox-quantum/switch/issues/1335)); after 90 min on one path, try the other; last resort WSL2 or a small Linux VM as the agent host | 90 min |
| **S1** Second person | Can a second Mattermost user address an `anyone` agent, with and without a Switch claim? | Claimed user is answered | Create a Switch user plus claim for every persona; document in README | 30 min |
| **S2** Folder MCP + ask | Do an agent folder's `.mcp.json` (toy `ping`, `commit_ping`) and `.claude/settings.json` `ask` rule apply under Console, raising a Switch card? Is `auto_mode: false` honored? | Card appears for `commit_ping` only | CLI variant with `Bash(uv run lq commit:*)` in `ask`; then the steward fallback ([03](03-architecture.md#decision-rules-after-the-spikes)) | 60 min |
| **S3a** Wrong clicker | What happens when a non-owner clicks the card? | Refused, card stays open (pin exact text) | Escalate to organizers; steward fallback; never claim a guarantee we lack | 15 min |
| **S3b** Session allow | After "Allow for this session" on one call, does the next `commit_ping` raise a fresh card? | Fresh card | Add the gate hook returning `ask`; retest; if still leaking, steward fallback for commits | 30 min |
| **S3c** Agent "yes" | Does an agent's bare "yes" in the card thread settle the card? | Card stays open | Strengthen rule 8, report upstream, steward fallback | 15 min |
| **S4** Templates | Do the lab and project templates import (group, aliases, roles, docs, kickoffs, agent-typed params, placeholders in `directory`)? | Both create what they declare | Set aliases, roles and docs by hand after creation; simplify the template; document | 45 min |
| **S5** Codex on Windows | Does a Codex `@analyst` run and call MCP tools? | Works | Claude Code for all five | 20 min |
| **S6** Capacity | RAM, CPU and token use of five concurrent sessions plus Docker Mattermost on this laptop | Fits with headroom | Cut line A (drop `@scribe`); cheaper model in development | 20 min |
| **S7** Scholarly access | OpenAlex key (starts new-account pacing), Crossref polite pool, pick and pin the retracted DOI and 6-8 real EGCG papers | Pinned in fixtures | Use cassettes recorded with whatever access works | 30 min |
| **S8** Submission form | Open the website's Submit form: which fields (repo, video, README, track, Wispr screenshot, blog, social)? limits? | Field list in `docs/adr/000-spikes.md` | Ask in WeMakeDevs Discord | 10 min |

## 8.2 Hour by hour

### Wednesday 4 Nov

| Time | Work | Done when |
| --- | --- | --- |
| 22:30-23:00 | Wispr baseline Insights screenshot; load dictionary and snippets ([05](05-wispr-flow.md)); S7 OpenAlex key; S8 inspect the Submit form; star the Switch repo | Dictating into VS Code and Mattermost |
| 23:00-00:15 | **S0**: Docker Desktop (4 GB), Switch Console v0.40.1, local server with Mattermost, `claude auth login`, smoke test | An agent answers in a room |
| 00:15-01:00 | **S1**, start **S2** with a toy MCP server | Results written |
| 01:00-08:00 | Sleep | |

### Thursday 5 Nov

| Time | Work (tests first) | Milestone |
| --- | --- | --- |
| 08:00-09:45 | Finish **S2**, **S3a-c**, **S4**, **S5**, **S6**; ADR-000 go/no-go; ADR-001 architecture; ADR-002 approval model | Approval path decided |
| 09:45-10:30 | Repo skeleton: `uv init`, ruff, pyright, pytest, pre-commit, gitleaks, em-dash check, CI workflow, `.gitattributes`, `.env.example`; first red test | CI green on the skeleton |
| 10:30-13:00 | Domain: U-B01..12, U-I01..06, U-A01..10, U-L03..04, P-01..06 | Domain green |
| 13:00-13:45 | Lunch; 15-minute researcher walkthrough if someone is reachable | |
| 13:45-15:30 | Store and audit (U-L01..02, I-01 x50 on Windows), MCP server and profiles (C-01..C-10, C-13, I-02, I-03), gate hook (C-12) | Contracts green |
| 15:30-18:00 | Agent folders and settings, `lq doctor` (C-11, I-11, I-13), lab and project templates; write E2E-02..04 first, then make the first live loop pass: `@labops` proposes, `@pi-desk` raises a card, Maya refused, PI commits | **M1 / cut line A** |
| 18:00-19:00 | Break, walk | |
| 19:00-21:45 | Scholarly: HTTP client (limiter, cache, retries, circuit), OpenAlex, Crossref, dedupe, verifier, golden set (U-C01..12, I-04..07, G-01..06) | Verifier thresholds met |
| 21:45-23:00 | `@scout` live: search, verify, retraction catch (E2E-07); #HowISwitch clip of the first approval card; voice-log entry | Scout segment works |
| 23:00-07:00 | Sleep | |

### Friday 6 Nov

| Time | Work (tests first) | Milestone |
| --- | --- | --- |
| 07:00-09:00 | Protocols, hazards, ethics (U-P01..07), bench notes with read-back (U-V01..06, I-21, I-22), `Lab state` document | |
| 09:00-11:30 | Data and analysis: CSV, profile, PII, recipe goldens, stale cascade (U-D01..10, U-S01..06, I-09, I-15, I-16); demo seed and `make_plate.py` | **M2: reproducible analysis + stale** |
| 11:30-12:15 | Lunch. **Cut line B:** `run_script` only if ahead, otherwise roadmap | |
| 12:15-14:00 | `@analyst` and `@scribe` live; draft refusal; stale cascade live (E2E-08, E2E-09, E2E-14) | Full story works once. **Cut line D at 13:30** |
| 14:00-17:00 | Playwright harness and remaining specs E2E-01..20, EDGE-01..06; evals EV-01..12 with the cheap model | E2E green once |
| 17:00-18:00 | Fix defects only; pixel pass on agent message formats | |
| 18:00-19:00 | Break | |
| 19:00-20:30 | Full rehearsal, then record the **baseline video**; Telegram `#bench` only if ahead (**cut line C at 20:00**) | Baseline footage saved |
| 20:30-22:45 | Dictate README, blog draft, video script, voice log | Drafts exist |
| 23:00 | **Feature freeze** | |
| 23:00-06:30 | Sleep | |

### Saturday 7 Nov

| Time | Work | Milestone |
| --- | --- | --- |
| 06:30-08:30 | E2E-01..14 three consecutive green runs; evals with the demo model; fix defects only | Gate passed |
| 08:30-09:00 | Breakfast, microphone check | |
| 09:00-10:30 | Clean-room reproduction (M-03): new Windows user, fresh clone, README only; fix every gap | README proven |
| 10:30-12:30 | Rehearsal checklist, then three full takes; segment retakes | Raw footage |
| 12:30-13:15 | Lunch | |
| 13:15-15:15 | Edit, captions, export 1080p, upload, verify the link logged out | Video link |
| 15:15-17:00 | README final (video, GIF, diagrams, test evidence); publish the blog; #HowISwitch post | Links live |
| 17:00-18:30 | Final Insights screenshot; package audit: gitleaks, em-dash check, licenses, all links in incognito | Package ready |
| 18:30-19:00 | **Submit through the website's Submit form**; screenshot the confirmation | **Submitted** |
| 19:00-23:59 | Buffer only: fix broken links or upload problems; no features | |

## 8.3 Escalation rules

| Trigger | Decision |
| --- | --- |
| S0 not green by Thu 08:00 | Everything else waits; try the other server path, then a Linux host |
| M1 not reached by Thu 18:00 | Cut line A; spend the evening on the approval loop, not the verifier |
| Verifier not at thresholds by Thu 23:00 | Ship VERIFIED / NOT_FOUND / RETRACTED only; notes become polish |
| No full story by Fri 13:30 | Feature freeze on new behavior (cut line D) |
| An authorization or data-integrity test is red | Stop; fix the root cause or remove the capability. Never demo around an unsafe path |
| Behind on Sat 12:30 | Use the Friday baseline video and spend the time on the package |

## 8.4 Core Contribution PR

Skipped by default: lowest expected value per hour for a solo builder, judged after the event with heavy competition. If a teammate joins, they own issue [#807 (agent controller guide)](https://github.com/sandbox-quantum/switch/issues/807) from Thursday morning; a maintainer comment on that issue says the guide goes in `docs/agent-controller-guide.md`. Any Windows Console bug we hit gets a normal upstream issue with a reproduction regardless.
