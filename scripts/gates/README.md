# LabQuorum gates

Run commands from the repository root with `uv` available.

- `uv run python scripts/gates/common.py --ci` runs the universal checks used in
  CI. It skips the orchestrator-owned gate baseline and behavioral-red replay.
- `uv run python scripts/gates/common.py --phase p1` runs universal checks and
  then validates P1 red evidence and every claimed P1 test ID.
- `uv run python scripts/gates/p1.py` adds domain and store coverage, the I-01
  race test, idempotent demo seeding, and audit verification. P1 includes the
  minimal `lq init`, `lq seed --demo` and `lq audit verify` commands.
- `uv run python scripts/gates/p2.py` runs the P2 universal checks and the real
  MCP stdio probe. The probe requires `tests/contract/p2_probe_args.json` from
  the P2 builder. The structural example below uses placeholder JSON Pointers,
  not claims about the implemented tool schemas.
- `uv run python scripts/gates/p3.py` runs the P3 universal checks, creates an
  isolated runtime root with `lq setup`, lints the generated Switch template,
  verifies both agent instruction folders and their Codex `labquorum` profile
  registrations, rejects worktree and OneDrive roots, and requires five
  single-rule mutations to fail lint. It then
  runs `lq doctor` and probes `lq-mcp` over stdio against a temporary seeded
  ledger. Binding certification must expose `commit_booking`, allow one
  commit, reject a distinct second commit with `BINDING_COMMIT_LIMIT`, and
  allow an identical retry. The default approver profile and `--binding on`
  without evidence must expose no commit tool; refusal to start also passes
  for the latter.
- `uv run python scripts/gates/p3.py --live` additionally runs
  `scripts/gates/p3_live_check.py` against Switch Console CDP at
  `http://127.0.0.1:9333`. Pass `--runtime-root PATH` when setup used a
  non-default root. The live check reads managed agent definitions and their
  workspace addressing policies through Console RPC.

The stdio probe checks exact tool-name sets from `p2_expected_tools.json`, then
seeds a temporary ledger and performs propose, get, commit, idempotent repeat,
and tampered-decision calls. The template supplies each tool's argument object,
JSON Pointer paths into results, expected success values, and a pointer into the
decision object to mutate. Argument objects may contain `{"$ref": "..."}`
values: `proposal.request_id` or `request.request_id`, `request.revision`,
`request.content_hash`, and `request.decision`.

```json
{
  "propose_booking": {
    "tool": "propose_booking",
    "arguments": {},
    "request_id_path": "/replace/with/request/id/path"
  },
  "get_request": {
    "tool": "get_request",
    "arguments": {},
    "request_paths": {
      "request_id": "/replace/with/id/path",
      "revision": "/replace/with/revision/path",
      "content_hash": "/replace/with/hash/path",
      "decision": "/replace/with/decision/path"
    }
  },
  "commit_booking": {
    "tool": "commit_booking",
    "arguments": {},
    "result_paths": {"status": "/replace/with/status/path"},
    "committed_value": "replace-with-implemented-value",
    "idempotent_values": ["replace-with-implemented-value"],
    "tampered_decision_path": "/replace/with/decision/field",
    "error_codes": ["STALE_REQUEST", "DECISION_MISMATCH"]
  }
}
```

`phase_ids.json` is the expanded copy of the P1, P2 and P3 claimed test IDs from
`docs/build/PHASES.md`. Tests satisfy an ID when the collected function name
starts with `test_` followed by the ID with hyphens changed to underscores.

The orchestrator creates `docs/build/evidence/gate-baseline.txt` after reviewing
the gate implementation. Builders should not create or update that file.
