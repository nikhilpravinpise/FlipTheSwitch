# ADR 001: Codex MCP registration for Switch agents

Date: 2026-11-05

## Decision

Register LabQuorum in the Codex source-home `config.toml` as one stdio server. Do not register it through Switch Connectors, agent template `connections`, the Switch host MCP map, or a project `.codex/config.toml`.

The source-home server entry has an absolute `lq-mcp` executable path, absolute runtime-root and ledger arguments, no fixed `cwd`, no explicit profile, and no binding option. It sets the per-tool `commit_booking` approval mode to `prompt`. `lq-mcp` derives `proposer` or `approver` only when its working directory is under the matching runtime-root agent folder. Every other working directory gets an MCP server with zero tools. Binding defaults to off.

`lq setup` also writes a per-agent `.codex/config.toml` containing an explicit profile and absolute paths. This is a portable registration manifest for direct Codex use and for `lq doctor`; Switch approval-required sessions must use the source-home entry because Switch marks the project untrusted and Codex skips project `.codex` configuration. The source-home registration intentionally omits `--profile`, so a LabQuorum server in a builder Codex working directory receives no profile and exposes no tools.

## Evidence and alternatives

Switch source citations below are relative to the pinned checkout at `C:/Users/Nikhil/.claude/jobs/85ca08fa/tmp/ref/switch-v0.40.1/`.

| Candidate | Pinned source behavior | Decision |
| --- | --- | --- |
| Switch Connectors | `core/switch_core/gateway/connectors.py:33-74` registers a server-side connector type with connection configuration and a user identity. It does not accept a local stdio command and argument list. | Not a local LabQuorum launcher. |
| Agent template `connections` | `core/switch_core/agent_templates.py:844-880` converts names or `{service, access, repos}` values into service `ConnectionPlan` entries. | Grants a Switch service; it does not register arbitrary stdio MCP servers. |
| Switch-hosted connector MCP | `console/packages/agent-providers/src/host/shared-config.ts:115-123,206-219` describes and injects granted vendor MCP servers as host input and identifies them in `connectorMcpServers`. `console/packages/agent-providers/src/codex/config-args.ts:21-32,34-80` gives these connectors distinct approval handling and sets `default_tools_approval_mode="approve"` for other host-registered servers. | Not used for LabQuorum. The host path is not the path for a user-home stdio registration and has the approval override this design must avoid. |
| Project `.codex/config.toml` | `console/packages/agent-providers/src/codex/codex-adapter.ts:143-169` marks the working directory untrusted for approval-required sessions and documents that an untrusted project does not load its own `.codex` config. The command line sets the same untrusted project mark. | Not effective for this Switch mode. |
| Switch per-agent Codex profile | `console/packages/plugins/src/agents/impl/codex/profile.ts:94-106,125-136,148-172` writes a bounded set of model, effort, verbosity, web search, and instruction settings. It explicitly does not register MCP servers. `console/packages/plugins/src/agents/session-launch.ts:163-200` selects and passes that profile per agent. | No arbitrary MCP registration point in the pinned per-agent profile. |
| Source-home config merged into session home | `console/packages/agent-providers/src/codex/home.ts:23-46` hashes a session ID for its home, merges the source-home config with the agent config, removes `mcp_servers.switch`, and writes the merged Codex config. `console/packages/agent-providers/src/host/shared-config.ts:150-165` passes the agent working directory and prepares that home. | Selected. A source-home `mcp_servers.labquorum` entry survives the merge without entering Switch's host-registered MCP map. |

Switch starts `codex app-server` with `cwd=input.cwd` and adds host MCP overrides to that process at `console/packages/agent-providers/src/codex/codex-adapter.ts:349-360`. The LabQuorum entry omits Codex's optional MCP `cwd` field, so the child server is expected to inherit the app-server working directory. Codex documents `cwd` as optional for stdio servers and documents the `command`, `args`, `tools.<tool>.approval_mode`, and `default_tools_approval_mode` fields at [Codex MCP configuration](https://developers.openai.com/codex/mcp/) and [Codex configuration reference](https://developers.openai.com/codex/config-reference/). Inheritance of the actual child process working directory on Codex CLI 0.166.0 remains UNVERIFIED until a live Switch session proves that the runtime folder selects the intended profile. The server fails closed if it receives another directory.

The template uses stable agent slot names `labops` and `pi-desk`; the `{lab}` parameter prefixes their display names and the room name, while room aliases remain `labops` and `pi-desk`. In the pinned checkout, `_written_name` prefers `name`, `_resolved_name` interpolates `display_name` when needed, and the creation plan separately interpolates the `display_name` field: `C:/Users/Nikhil/.claude/jobs/85ca08fa/tmp/ref/switch-v0.40.1/core/switch_core/agent_templates.py:100-110,804-826`. This keeps mention aliases and local agent folders stable while the default display prefix is `rao`.

## Binding rules

- `off` is the only mode written by `lq setup`; `commit_booking` is absent from the server tool list.
- `certify` may expose `commit_booking` only for a test ledger. A ledger qualifies if it has the marker row `labquorum_test_marker(marker='p3-certify-only')`, is under a directory named `certify`, or is the P3 gate's `p3-test-ledger.sqlite` file under the OS temporary directory.
- `on` requires an explicit certification evidence JSON file with a `certified_tuple` matching the installed tuple: Codex CLI version, Switch Console version, LabQuorum version, and SHA-256 of the installed V1 template. Switch Console version must be provided by the trusted local installation environment. If any tuple value is missing or differs, the server refuses to start with binding tools.
- A successful binding server process may commit one distinct request. An identical retry with the same complete arguments is passed to the ledger's idempotent commit path. A different request or changed retry receives `BINDING_COMMIT_LIMIT`.
- The real room stays proposal-only until the installed tuple and native card behavior pass P4. The Codex tool-call card, effective `prompt` mode, complete card rendering, and user identity are not certified by static configuration.

## Verification status

Verified from the pinned source: source-home merging, Switch host MCP override behavior, project config suppression, Codex working-directory passed to app-server, Connectors semantics, template `connections` semantics, and the limited settings in Switch's generated Codex profile. Verified from the official Codex docs: stdio config fields and per-tool approval-mode syntax. UNVERIFIED on the installed runtime until live checks: effective source-home configuration after Switch merges it, MCP child working directory, actual `prompt` card, full card display, tool inventory for each agent, and the `0.40.1` Console version supplied to certification checks.
