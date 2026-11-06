# Contributing

## Local setup

Use Python 3.12 and uv. From the repository root, run:

```powershell
uv sync --locked
```

Run the CLI in the project environment with `uv run lq ...`. Keep generated environments, ledgers, credentials, and local runtime data out of commits. Copy `.env.example` to `.env` only when you need an optional key; `.env` is ignored by git.

## Test-first changes

Follow the plan ID in `docs/plan/06-testing.md` for each behavior. Add tests named `test_<plan_id>` and commit them with `test(pN): ...`. Run the tests and confirm a behavioral failure, such as a failed assertion or an intentional `NotImplementedError`. Import and collection errors do not count as a red result. Implement the behavior in a separate `feat(pN): ...` commit. Record the test node IDs and red commit in `docs/build/evidence/pN.json`.

Do not weaken, skip, xfail, or remove a test to obtain a pass. If a planned test needs correction, document the reason in `docs/build/evidence/pN-test-changes.md`.

## Checks and gates

Before opening a pull request, run the applicable checks from the repository root:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

Run the phase gate scripts for the work you changed, for example `uv run python scripts/gates/p1.py` and `uv run python scripts/gates/p2.py`. Gates are acceptance contracts. Do not edit `scripts/gates/**` unless you are assigned as the gate author.

## Branch and pull request flow

Create a focused branch or isolated worktree from the current integration branch. Keep commits small and use conventional commit subjects such as `test(p2): ...` and `feat(p2): ...`. Do not work in another contributor's worktree. Open a pull request with a concise summary, the plan IDs covered, exact commands and results, and any remaining limits. Wait for required gates and review before merge.

Do not use the em dash character (U+2014) in code, documentation, or commit messages. Do not add co-author or agent signatures to commits.
