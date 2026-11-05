| path | reason |
| --- | --- |
| tests/contract/test_p2_contract.py | Mark seeded contract-test ledgers as test-only and launch approver stdio servers with explicit `--binding certify`, because P3 makes commit exposure off by default. |
| tests/contract/p2_probe_args.json | Add the flat get_request card and commit arguments used by the P3 certify probe; keep the P2 probe's complete flat card pointer. |
| tests/unit/test_p3_setup.py | Keep imports compliant with Ruff and assert the commit limiter raises the stable domain error so FastMCP returns a failed tool call to the P3 gate. |
| tests/unit/test_p3_setup.py | Require the source-home MCP server default approval mode to be `approve`, with the existing per-tool `commit_booking` override left at `prompt`, matching the live approval contract. |
| tests/unit/test_p3_fix2.py | Added requester-handle, synthetic Darshan seed, labops instructions, and generated Codex approval-mode regressions. |
| tests/contract/test_p2_contract.py | Added explicit `requester_handle` arguments to existing MCP proposal contract and conflict tests. |
| tests/contract/test_p2_audit_fix.py | Added explicit Maya requester handles to existing proposal-bound, untrusted-text, and bounded-result tests. |
| tests/contract/__snapshots__/test_p2_contract.ambr | Updated only the `propose_booking` C-01 description, requester_handle property, and required fields. |
| tests/contract/p2_probe_args.json | Added `requester_handle` to the existing P3 gate proposal probe input. |
| tests/unit/test_p3_auditfix.py | Fixed the Windows TOML path replacement to quote the executable path, so the existing worktree rejection test changes its input as intended. |
| tests/unit/test_p3_auditfix.py | Added coverage that only the P2 gate's isolated temporary ledger path is accepted for certify mode while arbitrary `certify` directories remain rejected. |
| tests/unit/test_p3_setup.py | Updated the existing commit limiter test so a changed retry for the same request reaches ledger validation, while a distinct request remains blocked. |
| tests/fixtures/p2_replay.json | Added the requester's handle to the recorded proposal input and updated the seed people count for synthetic Darshan. |
| seed/demo.yaml | Added synthetic person `darved2305` and one synthetic valid INS-01 training grant; Maya and existing fixtures remain. |
