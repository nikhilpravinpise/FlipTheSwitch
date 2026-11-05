# P3 Codex agent runtime

## Layout and setup

Run `uv run lq setup` to use the platform data root: `%LOCALAPPDATA%\LabQuorum` on Windows and `$XDG_DATA_HOME/labquorum` on Linux. Set `XDG_DATA_HOME` to your preferred data directory if it is unset. A custom root is supported with `uv run lq setup --runtime-root PATH`. Setup refuses paths inside `.claude/worktrees` and OneDrive. It installs a locked, non-editable runtime environment under `runtime-root/venv`, so the registered `lq-mcp` command stays outside the builder worktree. Installation uses the local uv cache and does not access the network.

The runtime contains:

| Path | Purpose |
| --- | --- |
| `agents/labops/AGENTS.md` | Booking proposal and handoff instructions. |
| `agents/pi-desk/AGENTS.md` | Request review instructions for the lab owner. |
| `agents/{labops,pi-desk}/.codex/config.toml` | Direct Codex launch config, with an explicit proposer or approver profile and absolute paths. |
| `venv/` | Locked LabQuorum installation; its `lq-mcp` executable is referenced by all agent registrations. |
| `codex-home/config.toml` | Managed Codex config used by Switch agents. |
| `codex-home/auth.json` | Copy of the source Codex login, created only when the runtime copy is missing. |
| `switch/labquorum.template.yaml` | V1 two-agent, private-room Switch template, defaulted to `rao` for the room and agent display names. The stable agent slots remain `labops` and `pi-desk`, which also back the room aliases. |
| `codex/source-home-config.toml` | Copy of the generic source-home MCP registration fragment for review. |
| `ledger.sqlite` | Runtime booking ledger, initialized by setup. |
| `runtime.json` | Root, template hash, version, runtime Codex home, source-home registration and binding mode record. |

`uv run lq template lint PATH` checks the V1 template keys and booking-only Codex settings. `uv run lq doctor --runtime-root PATH` checks the root, manifest, ledger, agent instructions, stable MCP executable, effective MCP arguments, runtime Codex home, template, and binding state. Doctor reports `RUNTIME_BINDING_OFF` when the runtime is proposal-only and fails if the user Codex config contains a LabQuorum managed block.

## Switch MCP registration

`lq setup` writes the managed LabQuorum block only to `<runtime-root>/codex-home/config.toml`; it never reads or modifies `~/.codex/config.toml`. It copies `auth.json` from the current Codex home only when the runtime copy is missing, and never prints its contents. Re-running setup replaces only the managed block and retains unrelated runtime Codex settings. A conflicting existing `mcp_servers.labquorum` entry is an error. The registration has an absolute runtime `lq-mcp` executable, absolute `--runtime-root` and `--db` arguments, no fixed `cwd`, no explicit profile, server default `default_tools_approval_mode = "approve"`, and `commit_booking` override `approval_mode = "prompt"`. These keys are documented in the official [Codex MCP configuration](https://developers.openai.com/codex/mcp/) and [configuration reference](https://developers.openai.com/codex/config-reference/).

The `launch_console.ps1` helper closes Switch Console through its main window, rebuilds `PATH` from machine and user settings, sets `CODEX_HOME` to `<runtime-root>/codex-home`, starts `Switch Console.exe --remote-debugging-port=9333`, and waits for the CDP version endpoint. It applies and probes a Windows ACL that denies writes to both agent working directories before launching Console. Setup applies the same OS write restriction for non-temporary runtime roots. Temporary roots are reserved for tests and skip that policy.

The V1 Switch template uses stable agent slots named `labops` and `pi-desk`, with `display_name` values `{lab}-labops` and `{lab}-pi-desk`. Its room name is `{lab}-labquorum` and its aliases stay `labops` and `pi-desk`. This preserves the runtime folder and mention names while the default `lab=rao` prefixes the visible agent names and room. Switch interpolates the display name separately from the slot name and creates the agent from the slot name, as verified in the pinned source at `C:/Users/Nikhil/.claude/jobs/85ca08fa/tmp/ref/switch-v0.40.1/core/switch_core/agent_templates.py:100-110,814-826`.

At server start, the generic registration selects proposer only when its working directory is under `agents/labops`, or approver only under `agents/pi-desk`. Other working directories expose zero tools. Per-agent config files also set an explicit profile, but Switch approval-required sessions ignore project `.codex/config.toml`; the source-home entry is therefore the Switch registration path. This decision is based on the pinned Switch source in [ADR 001](adr/001-codex-mcp-registration.md): its managed Codex home merges source-home and agent config, host-injected MCP servers receive `default_tools_approval_mode="approve"`, and its app-server receives the agent working directory. The live run confirmed that the stdio child process inherited the agent directory and selected the expected profile (`console/packages/agent-providers/src/codex/home.ts:23-46`; `console/packages/agent-providers/src/codex/codex-adapter.ts:349-360`).

Codex config requests `sandbox_mode = "read-only"`, `web_search = "disabled"`, `features.shell_tool = false`, and `sandbox_workspace_write.network_access = false`. Switch v0.40.1 adds `workspace-write` when the generated agent profile omits a sandbox (`console/packages/agent-providers/src/codex/home.ts:10-20,35-46`), and passes the merged session home to Codex (`codex-adapter.ts:185-203`). Therefore the filesystem boundary relies on the OS ACL on the agent folders, not the source-home `sandbox_mode` value. `can_manage_agents` is false, auto mode and auto approve are false, and the template has no service connections. The Switch host-injected `switch` MCP server is separate from the LabQuorum source-home server; its complete tool inventory and a host-controlled allowlist have not been verified. Keep its control-plane mutators unavailable until that inventory is checked. The generic LabQuorum registration uses no profile so a developer or builder working directory gets no LabQuorum tools.

## Binding modes

`lq-mcp` defaults to `--binding off`. In off mode, an approver has review tools but no `commit_booking` tool. Setup always writes off mode.

`--binding certify` is for the P3 acceptance probe only. It accepts the exact `p3-test-ledger.sqlite` inside a `labquorum-p3-*` temporary root whose runtime manifest records binding off and a separate `ledger.sqlite`. A directory name or caller-writable marker is not enough. The mode allows one distinct commit per process; an identical retry reaches the ledger's idempotent path.

`--binding on` is unconditionally refused until a trusted P4 certificate verifier and a complete P4 record exist. A caller-supplied tuple is not certification. The production runtime remains proposal-only.

The one-commit limiter has a persistent SQLite reservation under the active Codex home for every `certify` or future certified `on` server, so a server restart or concurrent server cannot reserve a different request. A reservation is written before calling the ledger and remains after a crash. P3 retains the limitation that it cannot prove this home maps to one human conversation; `on` stays disabled pending P4 lifecycle certification.

## Run commands

```powershell
uv run lq setup
uv run lq template lint "$env:LOCALAPPDATA\LabQuorum\switch\labquorum.template.yaml"
uv run lq doctor --runtime-root "$env:LOCALAPPDATA\LabQuorum"
.\scripts\ops\launch_console.ps1
```

The P3 gate creates the only ledger accepted by certify mode. Do not create a production binding launch; `on` remains disabled pending P4.

## Live smoke result

The P0 release marker was present before live work. Setup used `%LOCALAPPDATA%\LabQuorum`; the V1 template was run through Switch Gateway's template-document API, which accepts a template, inputs, filled slots, and template name and creates its agents and room (`core/switch_core/gateway/rooms.py:619-679`). No Console UI was used. The imported private room is `rao-labquorum`, with `labops` and `pi-desk` aliases, the `bench-manager` and `approver` roles, and the Lab handbook document. The agents are `rao-labops` and `rao-pi-desk`.

Mattermost REST evidence from channel `c83c9h1rtifgzp38wpw35iazqh`:

| Event | Post ID | Time (IST) | Evidence |
| --- | --- | --- | --- |
| Maya's request | `57gdroajjiyq98nm3c51fsdj3y` | 2026-11-05 19:54:57.166 | `@labops, propose a 60-minute INS-01 booking on the next open day between 14:00 and 17:00` |
| LabOps threaded reply | `8ccnr67ttpdrtbzc1pzb4n4k8c` | 2026-11-05 20:04:03.606 | Root post is Maya's request. It names Dr. Lena Okafor's committed 14:00-15:30 slot, proposes Friday 6 November 2026, 15:45-16:45 IST, and routes pending request `AR-0042` to `@rao-pi-desk`. |

The ledger records `AR-0042` for Maya and `INS-01`, 2026-11-06 10:15-11:15 UTC, status `pending`; its linked booking `BK-0042` is `proposed`. The audit log contains `propose_booking` for LabOps and no commit event. The live source-home MCP entry uses an absolute executable and ledger path, no fixed profile, and `commit_booking` approval mode `prompt`. The LabOps MCP process ran from the LabOps directory with profile `proposer`; the PI-desk process ran with profile `approver` and binding `off`. Switch's source-home/agent config merge and app-server working-directory behavior are documented at `console/packages/agent-providers/src/codex/home.ts:23-46` and `console/packages/agent-providers/src/codex/codex-adapter.ts:349-360`. The approval answer API used for single-call MCP prompts is `core/switch_core/gateway/agent_sessions.py:169-188`.

The active LabOps Codex thread database reports thread `01a1ac19-479b-7792-b44b-1d13eeaa07a3`, model `gpt-6-luna`, reasoning effort `high`, and CLI `0.166.0`. Its referenced rollout file was absent when checked, so a rollout `turn_context` could not be verified. The Switch live check passed for both agents and confirmed Buddy was absent or stopped. The first `uv run python scripts/gates/p3.py --live` invocation exited 1 because check 6 found that `scripts/gates` differed from baseline `ad39706e9ac173b1f3e701056f5be9e66b766338`. The orchestrator then refreshed the baseline to `2ac7b2e070a7a799cd26d65c42d0c67b13f51cb4` in commit `63c5789`. The P3 builder did not edit gate files. The gate README assigns baseline creation or update to the orchestrator and explicitly excludes builders (`scripts/gates/README.md:74-75`). After the refresh, the exact acceptance command exited 0 with all checks passing.

## Live limitations

Binding remains off. No `commit_booking` call was made, so the actual commit approval card and its complete display remain unverified. The actual LabOps Codex rollout file was unavailable; model and effort are supported by the active thread database record, not rollout evidence. The source-home config requests read-only, but the active Switch thread allowed writes under the LabOps directory as described above. No non-MCP approval prompt occurred during the smoke run. `lq doctor` also reported the existing `OPENALEX_KEY_MISSING` and `DOCKER_UNAVAILABLE` warnings; neither is needed for the booking-only P3 smoke.
