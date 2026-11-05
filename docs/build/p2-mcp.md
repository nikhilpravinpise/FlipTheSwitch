# P2 MCP and CLI

## Run the server

Initialize the ledger before starting an agent server:

```powershell
uv run lq init
uv run lq seed --demo --anchor-date 2026-11-06
uv run lq-mcp --profile proposer
```

`lq-mcp` accepts `--profile proposer|approver|unavailable` and an optional `--db PATH`. The default ledger path is the same path used by `lq`. The MCP server name is `labquorum`, so Claude Code sees tools under `mcp__labquorum__<tool>`. MCP JSON-RPC uses stdout; structured JSON logs use stderr.

The `proposer` profile is for `labops`; the `approver` profile is for `pi-desk`. The `unavailable` profile is for agents whose capability is deferred. It only exposes `capability_status`. The P2 booking workflow uses the seeded requester Maya. It does not infer a human identity from tool arguments.

## Tool catalogue

All returned data is compact JSON. Results are limited to 8,192 UTF-8 bytes. An oversized result returns `INVALID_ARGUMENT`. Tool calls are rate limited to 30 calls per minute per MCP process and profile.

Datetime arguments are ISO 8601 strings with an explicit UTC offset, such as `2026-11-09T10:00:00+05:30`. Natural-language or offset-free values return `NEEDS_ISO_DATETIME`.

### Proposer

| Tool | Inputs | Purpose and result |
| --- | --- | --- |
| `list_instruments` | None | Lists instrument ID, name, location, time zone, status, training requirement, maximum block, cleaning gap, and booking window. |
| `check_availability` | `instrument_id`, `start`, `end` | Checks current policy for Maya. Returns an availability result and a readable local-time summary. A conflict returns the conflicting booking ID and owner, plus the nearest free interval with the same length when one exists. |
| `propose_booking` | `instrument_id`, `project_id`, `start`, `end` | Creates a pending booking request. Returns `request_id`, `revision`, `content_hash`, the full canonical `decision`, and a weekday/date/time/time-zone summary. A conflict returns the owner and nearest same-length slot. |
| `cancel_my_proposal` | `booking_id` | Cancels a committed booking after checking that its recorded requester is Maya. |
| `lab_state` | None | Reads a compact snapshot of instruments and bookings. |

### Approver

| Tool | Inputs | Purpose and result |
| --- | --- | --- |
| `get_request` | `request_id` | Returns current request status, revision, content hash, and complete canonical decision. |
| `policy_check` | `request_id` | Rechecks current booking policy for a pending request and reports named checks. `commit_booking` repeats policy checks inside its transaction. |
| `lab_state` | None | Reads a compact snapshot of instruments and bookings. |
| `decline_request` | `request_id`, `revision`, `reason` | Declines a pending request at the supplied revision and records the reason. |
| `commit_booking` | `request_id`, `revision`, `content_hash`, `decision` | Commits only if the request, revision, SHA-256 hash, and every canonical decision field match. An identical repeat returns the committed booking without a second audit mutation. |

### Unavailable

| Tool | Inputs | Purpose and result |
| --- | --- | --- |
| `capability_status` | None | Lists the booking-adjacent capabilities that are not enabled and why. Literature, analysis, inventory, and protocols are outside the P2 booking build. |

## Decision to approval card

1. `labops` calls `propose_booking`. The returned summary helps explain the request, while `request_id`, `revision`, `content_hash`, and `decision` are the transaction-bound values.
2. `pi-desk` calls `get_request` and reviews those canonical values. The decision includes `action`, `requester`, `resource`, `interval.start_utc`, `interval.end_utc`, `project`, `request_id`, and `revision`.
3. After the human reviews the approval card, the `commit_booking` call must echo the complete object from `get_request`, along with its ID, revision, and hash. The commit transaction checks the exact canonical bytes and current booking policy. A stale or altered value fails closed.

The serialized `commit_booking` arguments are required to stay below 900 characters so the full input can fit within Switch's 1,000-character MCP card detail limit. The decision object is not reduced to a prose summary or hash. Static tool and ledger contracts do not certify the installed Switch card or its human identity flow; those runtime checks are part of the later Switch certification.

## `lq` commands

- `lq init [--db PATH]` creates or inspects the ledger.
- `lq seed --demo --anchor-date YYYY-MM-DD [--db PATH]` loads the booking demo data.
- `lq doctor [--db PATH] [--agents-dir PATH]` reports Python and `uv` versions, OneDrive path use, SQLite version and journal mode, optional OpenAlex key status, Docker availability, and each existing agent folder's LabQuorum MCP config and profile. Warnings are distinct from blocking errors. It does not call scholarly APIs or mutate the ledger.
- `lq request show <id> [--db PATH]` prints the request's current ledger record.
- `lq audit verify [--db PATH]` verifies the audit hash chain.
- `lq audit tail [-n COUNT] [--db PATH]` prints recent audit events.

Doctor reports missing `uv`, unusable ledger paths, unsafe OneDrive placement, invalid agent MCP config, and an incompatible SQLite journal mode as errors. Missing optional OpenAlex credentials or a stopped Docker engine are warnings for this booking-only build.

## Shared error codes

This table is generated from `ErrorCode` in `src/labquorum/domain/errors.py` by `error_codes_markdown()`.

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
