| Test file | Reason |
| --- | --- |
| tests/conftest.py | Added generator and callable return annotations so pyright can check the test fixtures; runtime behavior is unchanged. |
| tests/unit/test_p1_error_paths.py | Added post-red boundary tests for error branches that were not reached by the required P1 behaviors, to meet the phase coverage gate. |
