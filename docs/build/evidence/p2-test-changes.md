| path | reason |
| --- | --- |
| tests/contract/test_p2_contract.py | Added tool-level checks for U-B11 offset-required datetime errors, U-B02 conflict owner and nearest-slot details, and C-09 agent MCP config resolution after the P2 red commit. The C-13 schema assertion follows the MCP SDK's generated Pydantic `$defs` references. |
| tests/contract/test_p2_contract.py | Updated the U-B02 conflict request to use the seeded INS-01 booking day and assert the named owner plus the same-length 15:45-16:45 local slot, accommodating the P1 next-open-day seed and fixed-width UTC timestamps. |
| tests/contract/__snapshots__/test_p2_contract.ambr | Added the C-01 Syrupy golden for each profile's live stdio tool names, descriptions, and generated JSON input schemas. |
| tests/contract/p2_probe_args.json | Added the gate's argument template after the P2 red commit, using the implemented request fields and JSON Pointer result paths. |
| tests/unit/test_p2_cli.py | Corrected test isolation for `shutil.which`, parsed JSON error output so Windows path escaping is asserted as a user-facing path, and covered `lq request show` against a seeded ledger. |
| tests/contract/test_p2_contract.py | Updated C-13 to require the flat human-readable commit card and updated I-12 to compare replayed calls with recorded stdio outputs and their fixed-seed provenance. |
| tests/contract/__snapshots__/test_p2_contract.ambr | Regenerated only the C-01 tool-description and input-schema snapshot for flat commit arguments, bounded untrusted text, the required trust notice, and the commit revision bound. |
