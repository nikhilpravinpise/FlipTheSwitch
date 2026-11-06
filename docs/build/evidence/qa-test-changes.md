# QA follow-up test changes (Darshan, post-v1.0.2)

Changes to pre-existing test files made by the student-side QA pull requests. No assertion was weakened, skipped or removed.

- `tests/demo/test_record_demo.py`: the `_make_recorder`, `FakeLedger`, `_proposal_snapshot` and `_committed_snapshot` helpers now take an optional student username, defaulting to `maya`, so every existing test keeps its original fixture. Two new tests drive the recorder as `darved2305`. Reason: the recorder smoke assertion hard-coded Maya as the ledger requester although requester identity now comes from the Switch sender, so the documented `--student darved2305` take could never pass.
