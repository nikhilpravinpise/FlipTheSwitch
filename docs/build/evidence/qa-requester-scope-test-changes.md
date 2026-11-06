# Requester-scoped proposer tools: test changes

Changes to pre-existing tests made with `fix(mcp): scope proposer tools to the requester`. No assertion was weakened, skipped or removed.

- `tests/contract/test_p2_contract.py`: `test_I_02_stdio_lists_profiles_and_calls_each_read_tool_on_seed` and `test_U_B11_tool_rejects_natural_language_time_with_needs_iso_datetime` now pass `requester_handle: "maya"` to `check_availability`, which now requires it. U-B11 still exercises ISO parsing, which runs before requester lookup.
- `tests/contract/__snapshots__/test_p2_contract.ambr`: regenerated for C-01. The only differences are the new required `requester_handle` argument on `check_availability` and `cancel_my_proposal`, and their descriptions, which no longer say the tools act for Maya.
