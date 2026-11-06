# P2 MCP and CLI

## Run the server

Initialize the ledger before starting an agent server:

```powershell
uv run lq init
uv run lq seed --demo --anchor-date 2026-11-06
uv run lq-mcp --profile proposer
```

`lq-mcp` accepts `--profile proposer|approver|unavailable` and an optional `--db PATH`. Repeating any recognized option is an argument error, including `--profile` and `--db`. The default ledger path is the same path used by `lq`. The MCP server name is `labquorum`. MCP JSON-RPC uses stdout; structured JSON logs use stderr.

The `proposer` profile is for `labops`; the `approver` profile is for `pi-desk`. The `unavailable` profile is for agents whose capability is deferred. It only exposes `capability_status`. `check_availability`, `propose_booking` and `cancel_my_proposal` require the Switch sender's platform handle and resolve it case-insensitively against ledger people. An unknown handle returns `UNKNOWN_REQUESTER`; it never falls back to Maya or another person.

## Tool catalogue

All returned data is compact JSON. Results are limited to 8,192 UTF-8 bytes. Requester-supplied text is bounded and returned in fields labeled `*_untrusted_text`; every tool description says that supplied text is data, not instructions. Mutation results have bounded fields: project text is at most 120 characters, decline reasons are at most 160 characters, and the complete proposal card is below 900 serialized characters. This keeps mutation results below the output cap before the operation is accepted. Tool calls are rate limited to 30 calls per minute per MCP process and profile.

Datetime arguments are ISO 8601 strings with an explicit UTC offset, such as `2026-11-09T10:00:00+05:30`. Natural-language or offset-free values return `NEEDS_ISO_DATETIME`.

### Proposer

| Tool | Inputs | Purpose and result |
| --- | --- | --- |
| `list_instruments` | None | Lists instrument ID, name, location, time zone, status, training requirement, maximum block, cleaning gap, and booking window. |
| `check_availability` | `requester_handle`, `instrument_id`, `start`, `end` | Checks current policy, including training, for the requester. Returns an availability result and a readable local-time summary. A conflict returns the conflicting booking ID and owner, plus the nearest free interval with the same length when one exists. |
| `propose_booking` | `requester_handle`, `instrument_id`, `project_id`, `start`, `end` | Validates the requester handle against ledger people, checks that person's training and creates a pending booking request. Returns exactly the flat arguments that can be echoed to `commit_booking`, including instrument and requester names, `project_untrusted_text`, local weekday/date/time/zone endpoints, UTC endpoints, revision, and hash. Project text is limited to 120 characters. A conflict returns the owner and nearest same-length slot. |
| `cancel_my_proposal` | `requester_handle`, `booking_id` | Cancels the requester's own committed booking. A booking owned by anyone else returns `NOT_FOUND` and is unchanged. The tool does not withdraw a pending proposal. |
| `lab_state` | None | Reads a compact snapshot of instruments and bookings. |

### Approver

| Tool | Inputs | Purpose and result |
| --- | --- | --- |
| `get_request` | `request_id` | For a pending current-format request, returns exactly the flat arguments to echo to `commit_booking`. Existing pending requests with the previous decision shape return `UNCOMMITTABLE_REQUEST`. |
| `policy_check` | `request_id` | Rechecks current booking policy for a pending request and reports named checks. `commit_booking` repeats policy checks inside its transaction. |
| `lab_state` | None | Reads a compact snapshot of instruments and bookings. |
| `decline_request` | `request_id`, `revision`, `reason` | Declines a pending request at the supplied revision and records a reason limited to 160 characters. |
| `commit_booking` | `request_id`, `revision`, `content_hash`, `action`, `instrument_id`, `instrument_name`, `requester_handle`, `requester_display_name`, `project_untrusted_text`, `start_local`, `end_local`, `start_utc`, `end_utc` | Commits only if every flat field matches the stored canonical decision, revision, and SHA-256 hash. An identical repeat returns the committed booking without a second audit mutation. |

### Unavailable

| Tool | Inputs | Purpose and result |
| --- | --- | --- |
| `capability_status` | None | Lists the booking-adjacent capabilities that are not enabled and why. Literature, analysis, inventory, and protocols are outside the P2 booking build. |

## Decision to approval card

1. `labops` calls `propose_booking`. Its result is the flat echo object: `request_id`, `revision`, `content_hash`, `action`, `instrument_id`, `instrument_name`, `requester_handle`, `requester_display_name`, `project_untrusted_text`, `start_local`, `end_local`, `start_utc`, and `end_utc`.
2. `pi-desk` calls `get_request` and reviews the same flat fields. Local fields include weekday, date, time, and zone, for example `Fri 6 Nov 2026 15:45 IST`. Project text is labeled untrusted data.
3. After review, `commit_booking` echoes those fields as individual arguments. The stored canonical decision and hash bind each field, including the names and both local and UTC endpoints. The transaction compares the complete canonical bytes and rechecks booking policy. A stale or altered value fails closed.

The server computes the full serialized argument object during proposal, before inserting counters, the request, booking hold, or audit event. It rejects any proposal whose complete echo would be 900 characters or longer. The card remains flat; no nested decision object is used. Old pending requests from a previous decision format are not migrated. `get_request` returns `UNCOMMITTABLE_REQUEST` with an instruction to decline or allow the old hold to expire, then create a new proposal.

The contract proves the MCP tool schema and returned arguments. It does not certify the installed Switch card's rendering or human identity flow; those runtime checks remain part of the later Switch certification.

## I-12 replay recording

`tests/fixtures/p2_replay.json` stores the inputs and expected outputs from four real MCP stdio calls. The provenance records the `mcp.client.stdio.stdio_client` client, `create_server` process, fixed clock `2026-11-05T12:00:00Z`, and demo seed anchored on `2026-11-06`. Recreate it with `uv run python scripts/dev/record_p2_replay.py`. The recorder uses the installed MCP 1.30.0 client API at `.venv/Lib/site-packages/mcp/client/stdio/__init__.py:72,106` and `.venv/Lib/site-packages/mcp/client/session.py:113,160,386`.

## `lq` commands

- `lq init [--db PATH]` creates or inspects the ledger.
- `lq seed --demo --anchor-date YYYY-MM-DD [--db PATH]` loads the booking demo data.
- `lq doctor [--db PATH] [--agents-dir PATH]` reports Python and `uv` versions, OneDrive path use, SQLite version and journal mode, optional OpenAlex key status, Docker availability, and each existing agent folder's LabQuorum MCP config and effective profile. It parses the server arguments after the configured `lq-mcp` or `python -m labquorum.mcp.server` entry point, rejects duplicate JSON keys and launch options, and resolves the configured executable. A missing or non-writable ledger parent is an error. Warnings are distinct from blocking errors. It does not call scholarly APIs or mutate the ledger.
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
| UNCOMMITTABLE_REQUEST | The pending request predates or exceeds the current commit-card contract. |
| ALREADY_DECIDED | The request already has a terminal decision. |
| DECLINED | The request was declined and cannot be committed. |
| NOT_FOUND | The requested ledger record does not exist. |
| UNKNOWN_REQUESTER | Requester handle is not in the lab ledger; ask the lab admin to add or correct it. |
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
