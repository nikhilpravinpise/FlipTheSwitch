# Gate evidence formats

Each phase's red evidence is recorded in `pN.json`:

```json
{
  "red_commit": "full-git-commit-sha",
  "red_tests": [
    "tests/unit/test_booking.py::test_U_B02_conflict_names_booking"
  ]
}
```

`red_commit` is the commit where the listed tests were added and observed failing
for a behavioral reason. The gate checks out that commit in a temporary worktree,
runs every listed node ID, and requires a failure for each with no collection or
test errors and no skips.

If a test file changed after the red commit, list it in `pN-test-changes.md` with
one table row per file and a concrete reason:

```markdown
| Test file | Reason |
| --- | --- |
| tests/unit/test_booking.py | Added the boundary case required by the same plan ID. |
```

Only record an allowed skip or xfail in `allowed-skips.md` when there is a
specific reason and the exact pytest node ID. An empty table means no skips or
xfails are allowed.

`gate-baseline.txt` is written by the orchestrator after reviewing the gate
scripts. It contains the commit SHA whose `scripts/gates/` tree is accepted.
