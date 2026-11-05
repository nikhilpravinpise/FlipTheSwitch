# P5 stale detection and dataset provenance

## Scope

This expansion adds immutable CSV dataset versions, descriptive analysis runs, hashed output artifacts, and stale propagation from a superseded dataset version through its runs and artifacts. It adds the `analyst` MCP profile with five tools. It does not add draft sections, results packets, arbitrary scripts, or inferential statistics.

## Module map

| Module | Responsibility |
| --- | --- |
| `store/schema.sql` | Schema v3 tables, constraints, immutability and monotonic status triggers. |
| `store/provenance.py` | Dataset validation, staging, registration, profiles, contained paths, and stale graph traversal. |
| `analysis/csvdata.py` | UTF-8 CSV parsing, column profiling, formula escaping, and conservative human-subject identifier screening. |
| `analysis/descriptive.py` | Fixed plate mapping validation, descriptive summary, and deterministic JSON/PNG outputs. |
| `analysis/worker.py` and `analysis/runner.py` | Fixed worker entry point, subprocess execution, timeout, and process-tree termination. |
| `analysis/service.py` | Run lifecycle, input/recipe/lock/output provenance, artifact rows, and run status. |
| `mcp/tools_analyst.py` | Profile-bound analyst tools. All staged paths are resolved internally. |
| `mcp/profiles.py` and `mcp/server.py` | Analyst profile tool list and isolated registration path. |
| `cli/main.py` | Separate `lq backup` command for preserving a ledger before upgrading. |
| `seed/make_plate.py` | Reproducibly generates the synthetic 96-well fixture from seed `20261107`. |

## Ledger and stale state

Schema version is 3. New ledgers receive the new schema. Existing schema versions are refused by `init_database` and `open_database`; no in-place upgrade is attempted. The error includes a concrete backup command:

```powershell
uv run lq backup --db <ledger> --output <backup>
```

The backup command uses SQLite's online backup API and requires a new output path. Dataset bytes live under `<ledger>.staging/datasets/<dataset-id>/v<version>/<sha256>.csv`. The ledger stores the relative path, byte count, SHA-256, schema description, sensitivity, registering actor, timestamp, and superseded version. Update and delete triggers make dataset versions immutable.

An identical latest content hash and sensitivity returns the current version idempotently. New bytes create a new version. A `dependency_edge` connects each input dataset version to its analysis run, and each run to its JSON and PNG artifacts. Registration traverses descendants breadth-first and changes current runs and artifacts to `STALE`. The first stale reason is retained. SQLite triggers reject a `STALE` run or artifact becoming `CURRENT`; a rerun has a new run ID and new artifact IDs.

The stale graph currently covers datasets, runs, and artifacts. Draft sections and packets are not present in this schema, so their planned stale checks are not implemented here. Recipe and parameter versions are recorded on each run; this build does not expose recipe editing.

`register_dataset` refuses an explicit `human_subjects` sensitivity and conservatively rejects likely direct identifiers found in headers, email addresses, phone-like values, or Aadhaar-shaped values. This detector is a screening heuristic, not a privacy certification. Dataset registration currently rejects CSV input over 50 MiB; the planned metadata-only local CLI import for larger files is not included.

## Descriptive recipe

Only `descriptive` version `1.0.0` is available, with an empty parameter object. It accepts the synthetic plate fixture's required columns and validates all 96 well identities, the 42 treatment wells, six technical wells per dose, seven planned concentrations, and the 54 medium-only wells. Unknown well mappings and duplicate wells fail for correction rather than being guessed.

For each concentration, JSON reports technical-well count, mean OD590, sample SD, concentration in ug/mL, and unit. It reports no p-values, inferential intervals, or significance claims. Synthetic A1 and H12 high-OD QC blanks are flagged and omitted only from the blank summary. Treatment wells remain included and are not blank-subtracted. The PNG uses a fixed Matplotlib style, a colorblind-safe palette, labeled axes with units, and a 150 dpi export.

The worker runs only the package's fixed recipe in a subprocess, with no shell and a 120 second wall-clock timeout. On Windows, timeout uses `taskkill /T /F`; on POSIX, it kills the new process group. The worker receives a reduced environment, verifies the staged input hash, and writes only under the staging root. Run records include the dataset input hash, recipe/version, parameters, `uv.lock` hash, output hashes, status, timestamps, and duration. JSON and PNG artifacts are stored in the staging run directory and their hashes are exposed by `run_status`.

The synthetic correction changes only C5's `od590` from `0.083` to `0.830` at 8 ug/mL, replicate 2. The independent golden checks 42 treatment wells and six wells per dose. Version 1's 8 ug/mL mean is 0.803333 OD590; the corrected mean increases by 0.1245 OD590. Repeated runs on the same environment produced identical JSON and PNG hashes in the integration test.

## Analyst MCP contract

The analyst profile exposes exactly:

| Tool | Purpose |
| --- | --- |
| `register_dataset` | Register UTF-8 CSV text as an immutable version, optionally stating sensitivity and correction reason. |
| `dataset_profile` | Read schema and quality findings by version ID without returning raw rows or paths. |
| `run_analysis` | Run the fixed descriptive recipe for a current dataset version. |
| `list_runs` | List recent runs, optionally scoped by dataset ID. |
| `run_status` | Read run and artifact hashes, status, and stale reason. |

No analyst tool accepts shell text or filesystem paths. Stored relative paths are checked against the ledger's staging root, including after path resolution, to reject traversal and symlink escapes. The MCP contract snapshot is in `tests/contract/p5_analyst_snapshot.json`.

## Tests and validation

The test-first commit is `d346d1a6a8ba24b6bdd861198c2869ad3457e5e3`. Its 18 P5 tests produced behavioral assertion failures against the absent schema/profile/implementation, with no collection errors. The finalized P5 test module covers CSV profiling, human-subject refusal, synthetic goldens, deterministic hashes, timeout process-tree termination, formula escaping, monotonic stale propagation against an independent graph oracle, schema refusal and backup guidance, MCP traversal rejection, and tool snapshots.

Validation was run on Windows with Python 3.12.13 and SQLite 3.53.1:

| Command | Result |
| --- | --- |
| `uv sync --locked` | Passed. |
| `uv run ruff check .` | Passed. |
| `uv run ruff format --check .` | Passed. |
| `uv run pytest tests/integration/test_p5_stale.py -q` | Passed: 18 tests. |
| `uv run pytest` | Failed: 119 passed, 9 P3 setup tests failed because `lq setup` and binding implementation are absent from this worktree. |
| `uv run pyright` | Failed only on `tests/unit/test_p3_setup.py` referencing the not-yet-implemented `ErrorCode.BINDING_CERTIFICATION_REQUIRED`. |
| `uv run python scripts/gates/p1.py` | Failed in its shared common checks for the same full-suite and P3 pyright failures. P1 race tests, 92.31% domain/store coverage, init, idempotent seed, and audit checks passed. |
| `uv run python scripts/gates/p2.py` | Failed in its shared common checks for the same full-suite and P3 pyright failures. P2 stdio probes passed. |

The P3 failures are outside this builder's assigned scope. The full acceptance gates remain blocked until the P3 implementation is present in this worktree and its shared checks pass. P5 does not yet have a phase ID entry in `scripts/gates/phase_ids.json`; the gate author owns that file.

## References

- Python SQLite backup API: [sqlite3.Connection.backup](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup).
- Python subprocess execution and timeout APIs: [subprocess](https://docs.python.org/3/library/subprocess.html).
- Matplotlib figure and axes APIs: [pyplot.subplots](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html) and [Figure.savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html).
