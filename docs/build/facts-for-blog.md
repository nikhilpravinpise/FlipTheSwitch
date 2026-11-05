# Verified local facts for the blog

Inspection date: 2026-11-05. Cloned product baseline: `86f71c3`.
This run adds documentation only. These are local Windows results, not a live Switch demonstration or clean-machine installation result.

## Commands actually executed

| Command | Result |
| --- | --- |
| `uv sync --locked` | PASS: installed the lockfile's 51 packages with Python 3.12.12. Initial restricted attempt could not read the uv cache; the approved retry succeeded. |
| `uv run ruff check .` | PASS: all checks passed. |
| `uv run ruff format --check .` | PASS: 125 files already formatted. |
| `uv run pyright` | PASS: 0 errors, 0 warnings, 0 informations. |
| `uv run pytest -q` | PASS: 101 passed in 93.32 seconds; 1 snapshot passed. Duration describes this run only, not a benchmark. |
| `uv run lq --help` | PASS: displayed `init`, `seed`, `doctor`, `request`, `audit`. |
| `uv run lq init --db ../artifacts/qa-ledger.sqlite` | Expected refusal: `INVALID_ARGUMENT`, ledger path under OneDrive. |
| `uv run lq seed --demo --anchor-date 2026-11-06 --db ../artifacts/qa-ledger.sqlite` | Expected refusal: `INVALID_ARGUMENT`, ledger path under OneDrive. |
| `uv run lq audit verify --db ../artifacts/qa-ledger.sqlite` | Expected refusal: `INVALID_ARGUMENT`, ledger path under OneDrive. |

Restricted direct-executable test and type-check attempts encountered dependency read-permission errors. The successful `uv run` checks above ran with approved access; those earlier errors are environment failures, not passing checks or product regressions.

The successful CLI sequence was:

```powershell
$qaLedger = Join-Path $env:TEMP 'labquorum-darshan-qa-20261105.sqlite'
uv run lq init --db $qaLedger
uv run lq seed --demo --anchor-date 2026-11-06 --db $qaLedger
uv run lq audit verify --db $qaLedger
uv run lq doctor --db $qaLedger
```

All four exited successfully. Observed output:

- Initialization: schema version 2, SQLite 3.50.4, journal mode `delete`.
- Seed: `seeded: true`, 4 instruments, 5 people and 2 bookings, anchor date 2026-11-06. These are synthetic fixture counts, not real users or adoption.
- Audit: `valid: true`, `first_bad_seq: null`, scope `internal chain consistency`. Truncation and recomputed chains remain undetectable without an external checkpoint.
- Diagnostics: `ok: true`, Python 3.12.12, uv 0.10.7. Warnings: Docker engine not responding and optional OpenAlex key absent; no agents directory was found. Diagnostic success is not live-deployment readiness.

The README now explains prerequisites, private-room joining, the local CLI workflow, expected outputs and the OneDrive path constraint. That documentation change does not establish a new user's unassisted success.

## What remains unverified

- Real Switch/Mattermost room availability and invitation; upstream issue 1 and 4 comments were empty when read.
- Human identity, student self-approval refusal, native card rendering and fresh one-use consent on the deployed runtime.
- Keyboard-only and screen-reader behavior of actual chat messages.
- Genuine dictation by Darshan; running Wispr processes are not usage evidence. Final export is scheduled for 2026-11-07 about 18:00 IST.
- Published article, real demo recordings, edited video, unlisted YouTube URL and logged-out playback.
- Chrome account state: computer-use inventory and a direct Chrome attempt both failed with `The browser access host is unavailable`, including after resetting the browser session.

Keep account identifiers, credentials, private invitations and Tailscale auth keys out of publication and source control. No article, comment, video, key or usage card was published or uploaded in this session.
