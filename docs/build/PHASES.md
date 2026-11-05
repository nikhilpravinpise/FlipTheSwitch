# Build charter: phases and gates

Source of truth for what "done" means in each phase. The plan is `docs/plan/`; test IDs come from `docs/plan/06-testing.md`. A phase is done only when its gate script exits 0 **when run by the orchestrator**, and an independent audit run reports zero high-severity findings. A builder's self-report is never evidence.

## Roles

- Orchestrator: writes briefs, runs gates, decides. Does not write product code.
- Builder (Codex `gpt-6-luna`, reasoning `max`, headless): writes tests and code for one phase.
- Gate author (separate Codex run): writes `scripts/gates/` from the spec below. Builders may not edit gates.
- Auditor (fresh Codex run, read-mostly): reviews a finished phase against plan, gate and code; writes `docs/build/audits/pN-audit.md` with severity-ranked findings that cite `file:line`.

## Universal gate checks (every phase, `scripts/gates/common.py`)

1. `uv sync --locked` succeeds (lockfile in sync).
2. `ruff check .` and `ruff format --check .` clean.
3. `pyright` clean (strict for `src/`).
4. Full `pytest` suite green, no skips or xfails except those listed with reasons in `docs/build/evidence/allowed-skips.md`.
5. No U+2014 character in any tracked file outside `docs/plan`, `docs/review`, `docs/inputs`.
6. `scripts/gates/**` unchanged since the gate commit recorded in `docs/build/evidence/gate-baseline.txt` (unless the orchestrator re-baselines).
7. No tracked secrets (`.env` absent from git; simple key-pattern scan).
8. Red-before-green: `docs/build/evidence/pN.json` records `red_commit` and the test node IDs introduced there. The gate checks out `red_commit` in a temporary git worktree, runs those tests, and requires every listed test to fail with a non-collection failure (pytest exit code 1, no errors at collection). Test files changed after `red_commit` must be listed with a reason in `docs/build/evidence/pN-test-changes.md`.
9. Every plan test ID claimed for the phase (list in the phase section below) exists as at least one test whose name starts with `test_<ID with - replaced by _>`.

## P0 - Environment and Switch spikes (human + orchestrator, parallel with P1/P2)

Docker Desktop, Switch Console v0.40.1, local server, Mattermost, two claimed personas (PI and Maya), Submit-form inspection (S8), Wispr Insights baseline. Evidence in `docs/build/adr/000-spikes.md`. Gate: orchestrator-verified screenshots/logs; S0 and S1 pass.

## P1 - Ledger core (booking-only)

Domain + store: instruments, training, bookings, approval requests with revision and canonical hash, audit hash chain, injected clock, time display, closed error enum, demo seed.

Claimed IDs: U-B01..U-B11, U-B12 (slot release only; stock holds deferred), U-A01..U-A10, U-L01..U-L04, U-G01, U-G06, P-01, P-02, P-05, P-08, I-01, I-10, I-19, I-20, I-25 (WAL/version reporting and five writers), I-34 (time-zone part).

Phase gate (`scripts/gates/p1.py`) adds: line coverage >= 90% for `src/labquorum/domain` and `src/labquorum/store`; I-01 race run with 50 repetitions passes; seed loads twice idempotently and `audit verify` passes on the seeded DB.

## P2 - MCP server and `lq` CLI

FastMCP stdio server with profiles `proposer` (labops), `approver` (pi-desk), `unavailable` (reserved for agents whose tools are not built; per `resource-plan.md` the baseline room runs only labops and pi-desk), decision schema under 900 serialized characters, `NEEDS_ISO_DATETIME`, compact results, rate guard; CLI `lq init | seed | doctor | audit verify | audit tail | request show`.

Claimed IDs: C-01, C-02, C-03, C-09, C-10, C-13, C-14, I-02, I-03, I-11, I-32 (CLI part), U-G01 (wired), I-12 (replay of recorded call sequence on a fresh seed).

Phase gate adds: a real subprocess `lq-mcp --profile <p>` started by the official `mcp` client over stdio lists exactly the expected tools per profile (golden), and a propose -> get_request -> commit round trip works through stdio against a temp ledger.

## P3 - Agent folders, Claude Code settings, gate hook (local, real `claude` CLI)

`agents/<name>/` with `CLAUDE.md`, `.mcp.json`, `.claude/settings.json`; gate hook; template in `switch/` that lints and matches the pinned Switch template schema.

Token budget rule (Nikhil, 5 Nov 14:43): every agent in every template and agent folder runs `model: claude-haiku-5-5` with `advanced_config: {effort: medium}` and the folder `.claude/settings.json` also pins `"model": "claude-haiku-5-5"`; C-07 template lint fails on any other model or effort, and P4 verifies the model from real session transcripts.

Claimed IDs: C-04, C-05, C-06, C-07, C-08, C-11, C-12, I-13, plus local headless proofs: the installed `claude` CLI started in each agent folder sees only its profile's lab tools, denied tools are denied, and the gated commit tool is never auto-allowed.

## P4 - Live Switch E2E (needs P0)

Template import, Playwright two-persona harness against real Mattermost, read/propose smoke gate (expect the 14:00-15:30 conflict and the 15:45-16:45 proposal, no commit), then native-card certification (S2, S3a-d, I-14, I-23, I-29, I-36..I-41, E2E-01..06, 10..13). Any failure: binding commits disabled, proposal-only path filmed.

## P5 - Expansion (only after P4 floor is safe)

Ordered by demo value: stale-detection/dataset provenance, literature verify_citation with cassettes, inventory holds. Each expansion is its own sub-phase with the same gate rules.

## P6 - Ship

README (how Switch is used, agents, chat setup, how to run, honest limits), `docs/test-evidence.md`, demo video, Wispr scorecard, public repo, submission.
