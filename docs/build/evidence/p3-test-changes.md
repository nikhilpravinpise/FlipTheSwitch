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
