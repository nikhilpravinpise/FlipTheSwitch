| path | reason |
| --- | --- |
| tests/contract/test_p2_contract.py | Mark seeded contract-test ledgers as test-only and launch approver stdio servers with explicit `--binding certify`, because P3 makes commit exposure off by default. |
| tests/contract/test_p2_contract.py | Place certify-mode contract-test databases under an isolated temporary P3 runtime with a manifest, matching the stricter runtime guard rather than relying on a caller-writable marker. |
| tests/contract/p2_probe_args.json | Add the flat get_request card and commit arguments used by the P3 certify probe; keep the P2 probe's complete flat card pointer. |
| tests/unit/test_p3_setup.py | Keep imports compliant with Ruff and assert the commit limiter raises the stable domain error so FastMCP returns a failed tool call to the P3 gate. |
| tests/unit/test_p3_setup.py | Require the source-home MCP server default approval mode to be `approve`, with the existing per-tool `commit_booking` override left at `prompt`, matching the live approval contract. |
| tests/unit/test_p3_auditfix.py | Encode replacement executable paths as TOML strings so the doctor regression exercises a real `.claude/worktrees` command path on Windows. |
| tests/unit/test_p3_auditfix.py | Track `Path.open` calls against a temporary user Codex config during setup so the test fails on any read or write of the global config, then stop tracking before assertions. |
| tests/unit/test_p3_auditfix.py | Verify a certify server creates its persistent commit limiter under the active Codex home, covering restarts and concurrent server instances. |
| tests/unit/test_p3_auditfix.py | Check the Windows ACL deny mask uses specific write and delete rights without denying Synchronize, so agents retain read access to their instructions. |
| tests/unit/test_p3_auditfix.py | Require doctor to prove agent directory protection with a `Path.open` file-create attempt because `os.access(W_OK)` reports a false positive for the specific Windows deny mask. |
| tests/unit/test_p3_auditfix.py | Assert the launcher uses a PowerShell-compatible path API for its process working directory after the live run exposed an unsupported `Split-Path` parameter set. |
| tests/unit/test_p3_auditfix.py | Preserve the orchestrator's P2 certify probe using only its disposable `labquorum-p2-*\g.sqlite` ledger, while rejecting other temporary ledger paths. |
| tests/unit/test_p3_auditfix.py | Keep the P3 one-commit limiter out of the P2-only disposable ledger so its tampered-decision check reaches booking validation. |
| tests/unit/test_p3_fix2.py | Added requester-handle, synthetic Darshan seed, labops instructions, and generated Codex approval-mode regressions. |
| tests/contract/test_p2_contract.py | Added explicit `requester_handle` arguments to existing MCP proposal contract and conflict tests. |
| tests/contract/test_p2_audit_fix.py | Added explicit Maya requester handles to existing proposal-bound, untrusted-text, and bounded-result tests. |
| tests/contract/__snapshots__/test_p2_contract.ambr | Updated only the `propose_booking` C-01 description, requester_handle property, and required fields. |
| tests/contract/p2_probe_args.json | Added `requester_handle` to the existing P3 gate proposal probe input. |
| tests/unit/test_p3_auditfix.py | Fixed the Windows TOML path replacement to quote the executable path, so the existing worktree rejection test changes its input as intended. |
| tests/unit/test_p3_auditfix.py | Added coverage that only the P2 gate's isolated temporary ledger path is accepted for certify mode while arbitrary `certify` directories remain rejected. |
| tests/unit/test_p3_setup.py | Updated the existing commit limiter test so a changed retry for the same request reaches ledger validation, while a distinct request remains blocked. |
| tests/fixtures/p2_replay.json | Added the requester's handle to the recorded proposal input and updated the seed people count for synthetic Darshan. |
