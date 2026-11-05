| path | reason |
| --- | --- |
| tests/contract/test_p2_contract.py | Added tool-level checks for U-B11 offset-required datetime errors, U-B02 conflict owner and nearest-slot details, and C-09 agent MCP config resolution after the P2 red commit. The C-13 schema assertion follows the MCP SDK's generated Pydantic `$defs` references. |
| tests/contract/__snapshots__/test_p2_contract.ambr | Added the C-01 Syrupy golden for each profile's live stdio tool names, descriptions, and generated JSON input schemas. |
| tests/contract/p2_probe_args.json | Added the gate's argument template after the P2 red commit, using the implemented request fields and JSON Pointer result paths. |
| tests/unit/test_p2_cli.py | Corrected test isolation for `shutil.which`, parsed JSON error output so Windows path escaping is asserted as a user-facing path, and covered `lq request show` against a seeded ledger. |
