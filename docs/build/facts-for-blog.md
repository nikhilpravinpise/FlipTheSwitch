# Facts for Darshan's blog

Status: working evidence sheet, not a release announcement. Claims about future gates, two-person filming and deployment remain pending. Check the latest evidence before publication.

## Problem and approach

- Shared instruments need booking rules, conflict checks and accountable decisions; LabQuorum proposes a lab-specific workflow in team chat. Its novelty and superiority are hypotheses, not established results. Source: `docs/plan/01-problem-market-usp.md`, `docs/plan/README.md`.
- The funded baseline is booking only: instruments, training, bookings, approval requests and audit. Literature, analysis, inventory and protocols are deferred. Source: `docs/plan/02-product.md`, `docs/build/PHASES.md`.
- In the intended Switch room, `@labops` checks rules and proposes an alternative; `@pi-desk` is restricted to its PI owner and handles decisions. Nikhil is the intended PI and Darshan the student, using distinct accounts. Two people do not create a quorum requirement. Source: `docs/build/team-impact.md`, `docs/build/PHASES.md`.
- The required template provider is Codex with `gpt-6-luna` and high effort. A smoke agent's managed settings showed these values, but rollout proof of model and effort was not recovered. Source: `docs/build/PHASES.md`, `docs/build/adr/000-spikes.md`.

## Approval and security

- The revised design calls for a native tool-call card, the full canonical decision with request ID, revision and hash, and at most one distinct binding commit per MCP server process, allowing identical retries. A new session should require a fresh card. This addresses possible session-wide grants; instructing a person to click Allow once alone is not enforcement. Source: `docs/build/codex-boundary.md`.
- The actual identity, effective tool inventory, repeated consent and full-card display must all pass certification on the installed tuple. Truncation, oversized cards, errors or missing evidence fail closed. Until certified, binding must be disabled and the demo is proposal-only. These are design requirements, not completed certification. Source: `docs/plan/README.md`, `docs/build/PHASES.md`, `docs/build/codex-boundary.md`.
- A ledger hash is not an authenticated human receipt; a same-OS-user malicious process is outside the stated boundary. An audit chain without an external checkpoint cannot prove a suffix was not removed or the chain recomputed. Source: `docs/plan/README.md`, `docs/build/audits/p1-audit.md`.

## Evidence and results

- Phase completion requires an orchestrator-run gate and an independent audit with zero high findings. P1 specifies at least 90% domain/store line coverage and 50 race repetitions; P2 specifies a real stdio client inventory and booking round trip. These are gate requirements, not proof of a pass. Source: `docs/build/PHASES.md`.
- The P1 audit verdict was FAIL, including high findings on seed dates and test coverage. It recorded 56 tests passing before adding regressions, then 3 failing and 56 passing; its reported gate pass was not independently rerun. Source: `docs/build/audits/p1-audit.md`.
- The P2 audit verdict was FAIL, including a high finding on duplicate profile options. It recorded 82 tests passing before two new regression tests failed. These are historical snapshots, not current totals. Source: `docs/build/audits/p2-audit.md`.
- The seed scenario names a 14:00-15:30 booking and a 15-minute gap; the expected alternative is 15:45-16:45. The P1 audit identified incorrect recording-anchor handling, so the actual fixture must be verified before filming. Source: `docs/build/audits/p1-audit.md`, `docs/build/PHASES.md`.

## Switch lessons

- A server-initiated Codex elicitation spike did not reach the app-server client; the tool received cancel, despite advertised elicitation support. Codex's own tool-call approval arrived instead. The design was revised; the replacement still requires live certification. Source: `docs/build/codex-boundary.md`.
- Console automation used its RPC through CDP and `window.electronAPI.invoke`; this enabled room, agent and identity operations in the recorded spike. The pinned Console paths and lines are documented in the ADR. Source: `docs/build/adr/000-spikes.md` (Run 4; `console/apps/switch-console-desktop/src/renderer/lib/ipc.ts:5`, `src/main/rpc.ts:34-66`).
- On Windows, Console initially could not find `docker-credential-desktop` on its inherited PATH, preventing Mattermost startup. After the orchestrator refreshed PATH and restarted Console, the server and Mattermost health checks passed; the full initial smoke still failed at that stage. A later run recorded a real Codex smoke reply. Source: `docs/build/adr/000-spikes.md`.
- A separate student identity and full approval behavior require actual end-to-end verification. Voice through Wispr is dictated text reviewed before sending, not an audio SDK integration. Actual usage evidence is pending. Source: `docs/build/team-impact.md`, `docs/plan/05-wispr-flow.md`.
