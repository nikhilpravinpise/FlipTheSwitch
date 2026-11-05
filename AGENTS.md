# AGENTS.md - rules for every coding agent in this repo

LabQuorum: a lab-operations workflow where people and AI agents book shared instruments together inside a Switch team chat. The plan lives in `docs/plan/` (read `docs/plan/README.md` first). The build charter, phases and gates live in `docs/build/PHASES.md`.

## Hard rules

1. Never write the em dash character (U+2014) anywhere: code, docs, commit messages. Use a plain hyphen "-".
2. Never add `Co-Authored-By` or any agent/tool name as co-author or signature in commits.
3. Never edit `docs/plan/**`, `docs/review/**`, `docs/inputs/**`, `CHANGELOG.md`, or any file marked auto-generated. Build docs go in `docs/build/`.
4. Never edit `scripts/gates/**` unless your brief explicitly says you are the gate author. Gates are the acceptance contract; a builder that edits a gate fails the phase.
5. Test first. For each behavior: write the test named after its plan ID (`test_U_B02_conflict_names_booking`), commit it as `test(pN): ...`, see a behavioral red (assertion failure or a stub raising `NotImplementedError`, never an import/collection error), then implement in a separate `feat(pN): ...` commit. Never weaken, skip, xfail or delete a test to make it pass. If a planned test is wrong, record why in `docs/build/evidence/<phase>-test-changes.md`.
6. Do not hallucinate APIs. For Switch, read the pinned source at the path given in your brief (tag `switch-console-v0.40.1`) and cite `file:line`. For MCP, Claude Code, SQLite, Python libraries: read official docs (web search allowed) or installed package source and cite the URL or path. If you cannot verify a fact, say UNVERIFIED instead of guessing.
7. Zero tolerance: `ruff check`, `ruff format --check`, `pyright` (strict for `src/`), and the full test suite must be clean before you finish. Fix any failure you see, even if you did not cause it.
8. No live network in tests. No secrets in the repo (`.env` is gitignored; `.env.example` documents keys).
9. Windows first (this machine), Ubuntu in CI. Use `pathlib`, argument arrays, UTF-8, aware datetimes (`zoneinfo` + `tzdata`). Never build shell strings or JSON by concatenation.
10. Commit your work in small conventional commits before you finish. Do not push, merge, rebase or force anything. Do not touch other worktrees.

## Stack (decided in docs/plan/03-architecture.md; do not change without an ADR in docs/build/adr/)

- Python 3.12, `uv` with committed `uv.lock`, `src/` layout, package `labquorum`, console scripts `lq` and `lq-mcp`.
- SQLite via stdlib `sqlite3`, `BEGIN IMMEDIATE`, 5 s busy timeout, injected clock, all times stored UTC.
- MCP: official `mcp` Python SDK, pinned `mcp>=1,<2`, FastMCP over stdio; stdout is JSON-RPC only, logs to stderr.
- Tests: pytest, hypothesis, pytest-timeout, syrupy, pytest-cov. Lint/types: ruff, pyright strict.
- Scope for the first build: booking-only (instruments, training, bookings, approval requests, audit). Literature, analysis, inventory, protocols are later phases.

## Final message

End every run with: what you changed (files), commits (sha + subject), exact commands you ran with their pass/fail result, anything UNVERIFIED, and open issues. Never claim a command passed unless you ran it in this session and saw it pass.
