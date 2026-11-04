# Adversarial review loop

The plan in [`../plan/`](../plan/README.md) was grilled and revised by headless Codex agents (round 1 reviewers on `gpt-6.1-sol`, high effort; every later reviewer, editor, integrator and fixer on `gpt-6.1-terra`, high effort, all with full permissions), orchestrated from Claude Code. Every finding had to carry evidence, an exact fix and a reasoning metric. Pass bar: **9/10 in every scope with no open blocker or high finding**, scoring the plan as a plan (build-time items count only if their certification procedure, pass/fail criteria, time box and fallback are written down).

## Scores by round

| Scope | Round 1 (five reviewers) | Round 2 | Round 3 | Round 4 | Round 5 | Round 6 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Technical (Switch truth, architecture, tests, schedule) | Switch 5.0, engineering 4.0 | 6.0 | 7.5 | 8.1 | 8.8 | **9.1 pass** |
| Novelty, evidence, decisions | Research 6.0, market 5.0 | 7.0 | 7.5 | 8.3 | 9.1 | **9.0 pass** |
| Presentation (demo, Wispr, submission, judging) | Judging 6.1 | 6.9 | 7.0 | 7.5 | 8.8 | **9.2 pass** |

## What changed most (high level)

- **Approval boundary:** a blocker was found and closed (a same-owner helper agent could widen `@pi-desk` addressing); the native-card path now ships only after a bounded certification with attack tests, revision-and-hash-bound decision payloads, a fail-closed bypass guard, and a proposal-only fallback.
- **Scope and schedule:** a bottom-up estimate (71-109 h for the original scope against about 41 active hours) forced a cut to a four-agent, booking-first vertical slice; the schedule is now 2,470 minutes with explicit slack and cut lines.
- **Honesty:** the assay is framed descriptively (one synthetic plate, technical replicates); novelty claims are bounded against cited prior work (Agent Laboratory, AI co-scientist, Virtual Lab and others); unproven numbers are marked UNVERIFIED.
- **Evidence:** a dedicated citation pass checked all 145 cited URL occurrences; [`10-decision-record.md`](../plan/10-decision-record.md) scores 39 decisions with per-decision criteria, weights, arithmetic, margins and revisit triggers.

## Files

| Folder | Contents |
| --- | --- |
| [`round1/`](round1/) | Five reviews (switch, research, market, engineering, judging), four editor change logs, integration log |
| [`round2/`](round2/) | Three verifier reviews, URL check, editor logs, integration log |
| [`round3/`](round3/) | Three verifier reviews, citation verification, editor logs, integration log |
| [`round4/`](round4/), [`round5/`](round5/) | Verifier reviews and the fixer's change log |
| [`round6/`](round6/) | Final verifier reviews: all scopes pass |

## Lesson recorded from the run

Round 1 ran five agents in parallel, each re-reading about 300 KB of context with open-ended search, and hit the account's usage limit after about 1.5M tokens; one review was lost because it wrote only at the end. Later rounds required incremental writes, scoped reading, search budgets and at most three parallel agents, and used about 60-180k tokens per agent.
