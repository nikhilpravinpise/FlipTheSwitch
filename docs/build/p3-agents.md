# P3 Codex agent runtime

## Layout and setup

Run `uv run lq setup` to use the platform data root: `%LOCALAPPDATA%\LabQuorum` on Windows and `$XDG_DATA_HOME/labquorum` on Linux. Set `XDG_DATA_HOME` to your preferred data directory if it is unset. A custom root is supported with `uv run lq setup --runtime-root PATH`. Setup refuses paths inside `.claude/worktrees` and OneDrive.

The runtime contains:

| Path | Purpose |
| --- | --- |
| `agents/labops/AGENTS.md` | Booking proposal and handoff instructions. |
| `agents/pi-desk/AGENTS.md` | Request review instructions for the lab owner. |
| `agents/{labops,pi-desk}/.codex/config.toml` | Direct Codex launch config, with an explicit proposer or approver profile and absolute paths. |
| `switch/labquorum.template.yaml` | V1 two-agent, private-room Switch template, defaulted to `rao` for the room and agent display names. The stable agent slots remain `labops` and `pi-desk`, which also back the room aliases. |
| `codex/source-home-config.toml` | Generic source-home MCP registration fragment for Switch managed sessions. |
| `ledger.sqlite` | Runtime booking ledger, initialized by setup. |
| `runtime.json` | Root, template hash, version, source-home registration and binding mode record. |

`uv run lq template lint PATH` checks the V1 template keys and booking-only Codex settings. `uv run lq doctor --runtime-root PATH` checks the root, manifest, ledger, agent instructions, effective MCP arguments, template, and binding state. Doctor reports `RUNTIME_BINDING_OFF` when the runtime is proposal-only.

## Switch MCP registration

`lq setup` writes the source-home fragment and, for a stable non-temporary runtime root, installs the LabQuorum server entry in `$CODEX_HOME/config.toml` or `~/.codex/config.toml`. It merges a marked LabQuorum block while retaining unrelated Codex settings. A conflicting existing `mcp_servers.labquorum` entry is an error. The installed source-home entry has an absolute `lq-mcp` executable, absolute `--runtime-root` and `--db` arguments, no fixed `cwd`, no explicit profile, and `commit_booking` approval mode `prompt`.

The V1 Switch template uses stable agent slots named `labops` and `pi-desk`, with `display_name` values `{lab}-labops` and `{lab}-pi-desk`. Its room name is `{lab}-labquorum` and its aliases stay `labops` and `pi-desk`. This preserves the runtime folder and mention names while the default `lab=rao` prefixes the visible agent names and room. Switch interpolates the display name separately from the slot name and creates the agent from the slot name, as verified in the pinned source at `C:/Users/Nikhil/.claude/jobs/85ca08fa/tmp/ref/switch-v0.40.1/core/switch_core/agent_templates.py:100-110,814-826`.

At server start, the generic registration selects proposer only when its working directory is under `agents/labops`, or approver only under `agents/pi-desk`. Other working directories expose zero tools. Per-agent config files also set an explicit profile, but Switch approval-required sessions ignore project `.codex/config.toml`; the source-home entry is therefore the Switch registration path. This decision is based on the pinned Switch source in [ADR 001](adr/001-codex-mcp-registration.md): its managed Codex home merges source-home and agent config, host-injected MCP servers receive `default_tools_approval_mode="approve"`, and its app-server receives the agent working directory. The live run confirmed that the stdio child process inherited the agent directory and selected the expected profile (`console/packages/agent-providers/src/codex/home.ts:23-46`; `console/packages/agent-providers/src/codex/codex-adapter.ts:349-360`).

Generated Codex config requests `sandbox_mode = "read-only"`, `web_search = "disabled"`, and `features.shell_tool = false`. The live managed session home had web search disabled and the shell tool disabled, but the active thread recorded `sandbox_mode = "workspace-write"` and a managed policy that allows writes under the LabOps agent directory. The source-home read-only setting therefore did not take effect in this Switch session. The pinned Switch source adds a managed sandbox to the agent config before merging it over the source-home config: `console/packages/agent-providers/src/codex/home.ts:10-20,35-46`; the adapter reads the merged session-home sandbox when creating the thread: `console/packages/agent-providers/src/codex/codex-adapter.ts:185-203`. Do not treat the source-home value as proof of read-only enforcement. The generic LabQuorum registration uses no profile so a developer or builder working directory gets no LabQuorum tools.

## Binding modes

`lq-mcp` defaults to `--binding off`. In off mode, an approver has review tools but no `commit_booking` tool. Setup always writes off mode.

`--binding certify` is for isolated tests only. It requires an approver profile and one of these test-ledger markers: a row `labquorum_test_marker(marker='p3-certify-only')`; a database under a directory named `certify`; or the P3 acceptance gate's `p3-test-ledger.sqlite` directly under the operating system temporary directory. The mode allows one successful distinct commit per process. An identical complete-argument retry reaches the ledger's idempotent path; a different request or changed retry returns `BINDING_COMMIT_LIMIT`.

`--binding on` requires the approver profile, the runtime root's `ledger.sqlite`, a working directory under `agents/pi-desk`, and an existing certification evidence file. The evidence JSON must have a `certified_tuple` object with exactly these installed values:

```json
{
  "certified_tuple": {
    "codex_cli_version": "0.166.0",
    "switch_console_version": "0.40.1",
    "labquorum_version": "0.1.0",
    "template_sha256": "<64-character SHA-256 hex digest>"
  }
}
```

The server reads the Codex CLI version, `LABQUORUM_SWITCH_CONSOLE_VERSION`, installed LabQuorum package version, and SHA-256 of the runtime's V1 template. Missing or mismatched data refuses startup with a binding certification error. The `0.166.0` Codex CLI and `0.1.0` LabQuorum values are the versions observed in this build environment; `0.40.1` identifies the pinned Switch source. Replace all values with the installed and certified target tuple, and replace the template hash placeholder with the actual digest. Do not enable on mode until P4 has certified the live card, effective prompt mode, complete decision display, and owner identity path.

## Run commands

```powershell
uv run lq setup
uv run lq template lint "$env:LOCALAPPDATA\LabQuorum\switch\labquorum.template.yaml"
uv run lq doctor --runtime-root "$env:LOCALAPPDATA\LabQuorum"
```

For an isolated binding probe, create a test ledger under a `certify` directory, initialize and seed it, then launch `uv run lq-mcp --profile approver --db ABSOLUTE_LEDGER_PATH --binding certify`. Do not point certify mode at the real runtime ledger. A production binding launch additionally supplies `--runtime-root ABSOLUTE_RUNTIME_ROOT --certification-evidence ABSOLUTE_EVIDENCE_PATH` and the certified Switch version environment value. New MCP server processes are required after one distinct request has committed.

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
