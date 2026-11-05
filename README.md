# FlipTheSwitch

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
<!-- error-codes:end -->
