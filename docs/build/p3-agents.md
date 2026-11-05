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

At server start, the generic registration selects proposer only when its working directory is under `agents/labops`, or approver only under `agents/pi-desk`. Other working directories expose zero tools. Per-agent config files also set an explicit profile, but Switch approval-required sessions ignore project `.codex/config.toml`; the source-home entry is therefore the Switch registration path. This decision is based on the pinned Switch source in [ADR 001](adr/001-codex-mcp-registration.md): its managed Codex home merges source-home and agent config, host-injected MCP servers receive `default_tools_approval_mode="approve"`, and its app-server receives the agent working directory. The stdio child process inheriting that directory remains UNVERIFIED until the live run proves it.

Generated Codex config sets `sandbox_mode = "read-only"`, `web_search = "disabled"`, and `features.shell_tool = false`. The source-home config has these settings as well, because Switch approval-required mode does not load the project config. The generic LabQuorum registration uses no profile so a developer or builder working directory gets no LabQuorum tools.

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

The live setup, template import, per-agent tool inventory, model and effort rollout check, Mattermost post evidence, and P3 live gate are pending until the Console release marker `p0e-last.md` is present. No live Console behavior is claimed in this document.
