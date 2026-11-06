| Test file | Reason |
| --- | --- |
| tests/conftest.py | Added generator and callable return annotations so pyright can check the test fixtures; runtime behavior is unchanged. |
| tests/unit/test_p1_error_paths.py | Added post-red boundary tests for error branches that were not reached by the required P1 behaviors, to meet the phase coverage gate. |
| tests/unit/test_p1_domain.py | Strengthened U-B01, U-B02, U-B03, U-B04, U-B05, U-B06, U-A04, U-G06, P-02 and P-08 with real proposals, exact boundary values, independent expectations and README table verification. |
| tests/integration/test_p1_ledger.py | Replaced sample lifecycle checks with a generated repository state machine, verified injected timestamps and audit mutations, strengthened I-10/I-19 and added audit CLI wording coverage. |
| tests/integration/test_p1_ledger.py | Add an I-10 regression proving a same-anchor seed run restores a newly added synthetic person and training grant without changing existing seed data. |
| tests/integration/test_p1_races.py | Replaced the shared production conflict predicate in P-01 with an independent arithmetic oracle over persisted UTC endpoints. |
| tests/integration/test_p1_races.py | `test_I_01_two_processes_race_fifty_times_and_unsafe_variant_is_detected` now has `@pytest.mark.timeout(300)`. At v1.0.2 `b1a5b14` on a Windows 11 host under load from other local services it passed in 63.3 s with `--timeout 600` but failed the suite-wide 60 s limit in three runs. The race, the fifty rounds, the unsafe-variant check and the per-worker joins are unchanged. |
