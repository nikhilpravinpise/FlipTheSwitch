# P1 booking ledger

## Module map

| Module | Responsibility |
| --- | --- |
| `domain/timeutil.py` | Injected clocks, strict ISO 8601 parsing, DST gap/fold detection, UTC normalization, and readable interval display. |
| `domain/errors.py` | Closed error-code enum, typed domain exception, and Markdown error-code table. |
| `domain/canonical.py` | Deterministic UTF-8 JSON and SHA-256 content hashes. |
| `domain/booking.py` | Pure booking checks, half-open conflict windows, and nearest-free-slot search. |
| `domain/approvals.py` | Approval decision serialization, revision rules, expiry, and lifecycle transitions. |
| `domain/policy.py` | Structured policy check results. |
| `domain/guards.py` | Per-profile rate limit with an injected clock. |
| `store/schema.sql` | Versioned SQLite schema, constraints, indexes, and append-only audit rows. |
| `store/db.py` | Connection setup, version-gated journal mode, schema compatibility, path checks, and immediate transactions. |
| `store/repos.py` | Transactional proposal, revision, commit, decline, cancellation, expiry, and read operations. |
| `store/audit.py` | Hash-chained audit append and verification. |
| `store/seed.py` and `seed/demo.yaml` | Anchor-date demo data and idempotent seed loading. |
| `cli/main.py` | `lq init`, demo seed, audit verify, and audit tail commands. |

## Invariants and coverage

| Invariant | Coverage |
| --- | --- |
| Booking intervals are half-open; the configured minimum gap is included in conflict checks. | `U-B01`, `U-B02`, `U-B03`, `P-01`, `P-02`, `I-01`, `I-25` |
| Booking policy checks local opening hours, booking window, past time, instrument downtime, training at start, and maximum block length. | `U-B04`, `U-B05`, `U-B06`, `U-B07`, `U-B08` |
| Time input requires ISO 8601 and rejects DST gaps and folds unless the input carries an explicit offset. Display includes weekday, date, time, and zone. | `U-B10`, `U-B11`, `U-L03`, `U-L04`, `I-34` |
| Approval requests use only pending, committed, declined, and expired states. Expiry is inclusive at `now >= expires_utc`; revision, decision bytes, and content hash must match. | `U-B09`, `U-A01`, `U-A05`, `U-A06`, `U-A07`, `U-A08`, `U-A10`, `P-05` |
| Commit rechecks booking policy within `BEGIN IMMEDIATE`, allows exactly one conflicting writer, and returns an identical repeat without a second audit effect. | `U-A02`, `U-A03`, `U-A09`, `I-01`, `I-25`, `P-01` |
| A cancellation releases its slot once; a declined or expired request cannot commit. | `U-B12`, `U-A01`, `U-A05`, `U-A06`, `P-01`, `P-05` |
| Canonical JSON is stable, compact, UTF-8, sorted, rejects floating point values, and normalizes aware times to UTC `Z`. | `P-08` |
| Audit records form a SHA-256 chain; a raw edit is reported at the first invalid sequence. | `U-L01`, `U-L02`, `I-20` |
| Demo seed is anchor-date-relative and idempotent. Schema version mismatch is rejected; journal mode is selected from the SQLite runtime version. | `I-10`, `I-19`, `I-20` |
| Error values are closed, policy checks are structured, and per-profile rate limits use the injected clock. | `U-G01`, `U-G06`, `U-A04` |

## Runtime measurement

Measured on the Windows build machine using the P1 race and journal-mode tests: SQLite `3.53.1`, journal mode `wal`. The configured selection is WAL for SQLite `>= 3.51.3` and DELETE otherwise.
