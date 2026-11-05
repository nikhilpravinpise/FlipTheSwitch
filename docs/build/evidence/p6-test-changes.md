# P6 test changes after red commit

`tests/integration/test_p6_backup_restore.py` was reformatted with `uv run ruff format` and adjusted to use one combined connection context after red commit `9caf04fe4fb6c91bf763c0a8c7f55af9254f8e72`. These changes only affect formatting and resource cleanup; test names and assertions are unchanged.
