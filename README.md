# FlipTheSwitch

LabQuorum is a booking prototype for shared laboratory instruments. A requester asks
`@labops` for a slot in a Switch room; `@pi-desk` handles review. The Python ledger
checks booking rules, conflicts and the exact decision fields before commitment.
Demo people and instruments are synthetic. Live human identity and native approval
cards require separate certification; a pending proposal is not a reservation.

## Join the team's live room

Requesters need Chrome, Tailscale and a Mattermost invitation from the host. The
Switch server runs on the host's laptop; cloning this repository does not start
that server or create a room.

1. Install Tailscale from its [official Windows page](https://tailscale.com/download/windows)
   and sign in with your own account.
2. Complete the private connection setup with the host, then obtain the actual
   Mattermost URL and invitation. Keep credentials and connection keys out of the repo.
3. Join with your own student account. Ask `@labops, which instruments can I book?`
   Then request a slot using the host's agreed demo date and an explicit time zone.
4. Read the returned instrument, date, interval and request state. Only an eligible
   reviewer can approve; report an inaccessible or unclear approval flow to the host.

See the [onboarding checklist](docs/build/darshan/issue-1-onboarding.md) and
[QA procedure](docs/build/darshan/issue-4-qa-video.md) for evidence still required.

## Explore the local ledger

Prerequisites: Git, [uv](https://docs.astral.sh/uv/getting-started/installation/)
and Python 3.12. From PowerShell, clone and install the locked dependencies:

```powershell
git clone https://github.com/darved2305/FlipTheSwitch.git
cd FlipTheSwitch
uv sync --locked
```

The following uses a separate synthetic demo ledger in Windows TEMP. Choose an
anchor date deliberately: it determines the seeded schedule. Do not reseed a
shared live ledger as part of a local setup test.

```powershell
$demoLedger = Join-Path $env:TEMP 'labquorum-demo.sqlite'
uv run lq init --db $demoLedger
uv run lq seed --demo --anchor-date 2026-11-06 --db $demoLedger
uv run lq audit verify --db $demoLedger
uv run lq doctor --db $demoLedger
```

Successful initialization reports a schema version; seeding reports `seeded: true`;
audit verification reports `valid: true`. The audit checks internal chain consistency
and cannot detect truncation or a recomputed chain without an external checkpoint.
`doctor` reports local diagnostics; its success does not certify live Switch approval.
TEMP is for disposable exploration. For persistent use, omit `--db` to use
`%LOCALAPPDATA%\LabQuorum\ledger.sqlite` on Windows or
`$XDG_DATA_HOME/labquorum/ledger.sqlite` (default `~/.local/share`) on Linux.
Ledger paths under OneDrive are rejected, including a database beside a synced checkout.

## Development checks

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q
```

The current CLI provides `init`, `seed`, `doctor`, `request show`, `audit verify`
and `audit tail`. Run `uv run lq --help` for command details. The MCP server is
an stdio protocol process for an MCP client. Developer integration notes are in
[P2 MCP documentation](docs/build/p2-mcp.md); live deployment requirements and
remaining acceptance gates are in [build phases](docs/build/PHASES.md).

## Error codes

<!-- error-codes:start -->
| Code | Meaning |
| --- | --- |
| CONFLICT | The requested interval conflicts with a committed booking. |
| INSTRUMENT_DOWN | The instrument is unavailable for the requested interval. |
| TRAINING_REQUIRED | Required training is missing or expired at booking start. |
| TOO_LONG | The requested booking exceeds the instrument block limit. |
| OUTSIDE_WINDOW | The requested booking is beyond the booking window. |
| OUTSIDE_HOURS | The requested interval is outside instrument opening hours. |
| IN_PAST | The requested interval starts before the current time. |
| NEEDS_ISO_DATETIME | The input must be an explicit ISO 8601 datetime. |
| AMBIGUOUS_LOCAL_TIME | The local time occurs twice; provide a UTC offset. |
| NONEXISTENT_LOCAL_TIME | The local time does not exist because of a clock change. |
| EXPIRED | The approval request has expired. |
| STALE_REQUEST | The request revision or content hash is stale. |
| DECISION_MISMATCH | The submitted decision differs from the canonical decision. |
| UNCOMMITTABLE_REQUEST | The pending request predates or exceeds the current commit-card contract. |
| ALREADY_DECIDED | The request already has a terminal decision. |
| DECLINED | The request was declined and cannot be committed. |
| NOT_FOUND | The requested ledger record does not exist. |
| RATE_LIMITED | The profile exceeded its tool call rate limit. |
| INVALID_ARGUMENT | An argument is invalid or outside the supported format. |
| SCHEMA_VERSION_MISMATCH | The ledger schema version is not supported. |
| UNIT_MISMATCH | Quantities use incompatible units. |
| UNKNOWN_HAZARD | The hazard is unknown and must be reviewed. |
| ETHICS_REVIEW_REQUIRED | The request requires an ethics review. |
| TAMPERED | Stored content failed its integrity check. |
| BUDGET_EXCEEDED | The request exceeded its configured call budget. |
| UNRESOLVED | The requested source could not be resolved. |
| MISMATCH | The source metadata does not match the supplied metadata. |
| RETRACTED | The source has a recorded retraction. |
| UNREACHABLE | The remote source could not be reached. |
| BINDING_COMMIT_LIMIT | This MCP process already committed a different booking. |
| BINDING_CERTIFICATION_REQUIRED | Binding requires a test ledger or matching certification evidence. |
| BINDING_CERTIFICATION_MISMATCH | Certification evidence does not match the installed runtime tuple. |
<!-- error-codes:end -->
