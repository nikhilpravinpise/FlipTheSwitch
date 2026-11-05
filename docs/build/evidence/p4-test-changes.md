# P4 harness test changes

## Changes after red commit d54ed77

- `tests/e2e/test_p4_harness.py`: commit the synthetic setup rows before opening the database with the read-only inspector. SQLite correctly hid the test's uncommitted fixture rows from the separate read-only connection; the original fixture therefore tested visibility of uncommitted writes instead of harness behavior. The test also now attempts an update through the inspector's `mode=ro` URI and requires SQLite to reject it. Added regression coverage for historical commits during a no-effect refusal, repeat error matching and pending state, `%LOCALAPPDATA%` expansion, explicit provider-session confirmation, leaving a distinct same-session card pending after the first commit, and verifying that the settled card names Decline. These changes strengthen the acceptance checks and do not weaken any scenario assertion.
