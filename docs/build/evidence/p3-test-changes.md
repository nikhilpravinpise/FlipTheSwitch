| path | reason |
| --- | --- |
| tests/contract/test_p2_contract.py | Mark seeded contract-test ledgers as test-only and launch approver stdio servers with explicit `--binding certify`, because P3 makes commit exposure off by default. |
| tests/contract/p2_probe_args.json | Add the flat get_request card and commit arguments used by the P3 certify probe; keep the P2 probe's complete flat card pointer. |
| tests/unit/test_p3_setup.py | Keep imports compliant with Ruff and assert the commit limiter raises the stable domain error so FastMCP returns a failed tool call to the P3 gate. |
