# Orchestrator handoff: full session context (as of Fri 6 Nov 2026, 10:58 IST)

Written by the orchestrator (Claude) so the session can be resumed after context compaction. Deadline: **Sat 7 Nov 2026, 23:59 IST** (form: `docs/submission-fields.md`, video UNDER 3:00, human clicks Submit).

## 1. People, goal, standing rules

- **Nikhil Pravin Pise** (owner, PI persona, approves) and **Darshan Ved** (teammate, GitHub `darved2305`, Mattermost `darved2305`, Switch user "Darshan Ved (student)"; remote; owns blog #3, a11y/QA + video edit #4, Wispr card #2).
- Product: **LabQuorum**, Track 1 (Best Business Workflow) + Code with Wispr. Lab instrument booking in a Switch team chat: `@labops` (anyone) proposes conflict-free slots; `@pi-desk` (owner-only) commits only after the PI answers a native Switch approval card.
- Rules from Nikhil (all in memory too):
  - Claude only orchestrates (writes briefs, decides, glances at outputs). ALL grunt work goes to Codex: **Luna Max** (`gpt-6-luna`, effort `max`) for building/fixing/ops; **Terra 6.1 High** (`gpt-6.1-terra`, effort `high`) for every per-phase audit and research. One audit per phase, no re-audit.
  - Switch room agents: **Codex provider, model `gpt-6-luna`, effort `high`** (no Claude/Haiku agents).
  - Get everything onto GitHub `main` at the end (every work branch merged, CI green, tag `v1.0.0`). Merge to main per phase when complete; merging is pre-authorized.
  - Repo stays PRIVATE until everything is complete; make public last.
  - Export both Wispr cards at the very end; Nikhil pastes the submission text himself.
  - Ignore the RAM limit (Nikhil, 06:28 Fri); parallelize when it helps.
  - No em dashes anywhere; no Co-Authored-By lines in commits; never hand-edit CHANGELOG.

## 2. How Codex runs are launched

```powershell
Get-Content <brief.md> -Raw | codex --search exec -m gpt-6-luna -c model_reasoning_effort="max" --dangerously-bypass-approvals-and-sandbox -C <worktree> --add-dir <extra dirs> -o <out-last.md> - *> <log>
```
(`--search` goes BEFORE `exec`; Terra: `-m gpt-6.1-terra -c model_reasoning_effort="high"`.)
- Scratch root: `C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\` with `briefs\`, `out\` (each run's final report `*-last.md`), `logs\`, `scripts\`, `ref\switch-v0.40.1\` (pinned Switch source clone).
- Helper scripts: `scripts\after_then.ps1` (wait for a file, then launch a run), `split_codex_home.py` (strip LabQuorum agent settings from the user's global Codex config), `guard_codex.ps1` (re-run that every 10 s), `wait_issue_comment.ps1`, `watchdog.ps1`, `cdp_shot.py` / `cdp_eval.py`.
- Claude Code reaps background runs when system memory is low (happened 03:15 and 07:15 Fri). Fix: launch Claude Code with env `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1`. After a reap, restart only when Nikhil says so.
- Quota check: newest `~/.codex/sessions/**/rollout-*.jsonl` has `rate_limits` (5 h and weekly windows).

## 3. Repo, branches and worktrees

- GitHub: `nikhilpravinpise/FlipTheSwitch` (private). `main` has P1+P2 (PR #5, merge `86f71c3`) and Darshan's PRs #6 (docs, blog draft, a11y plan, 135-second script, README quickstart, `docs/build/facts-for-blog.md`) and #7 (CI `setup-uv` pinned to `68559e99cc807c1eb7e9238fd43a15bba460eec2`, v10.3.3; `@v10` does not resolve).
- Worktrees under `C:\Dev\FlipTheSwitch\.claude\worktrees\`:
  - `build-labquorum` (branch `worktree-build-labquorum`): main build branch; P3 + P4 work; last commit before the current run `fb09cd1`. P4 run is live here.
  - `release-prep`: everything pre-merged (origin/main, integrate, readme, demo-rec, ship-docs, p3-fix2, p6-prod, p5-stale, p5-lit, p4-harness); ALL offline gates exit 0 (259 tests, P1 92.54% coverage + race, P2, P3).
  - `integrate`, `readme` (final README `17a2ffd`), `demo-rec` (scripted recorder `a7b8996`), `ship-docs` (submission text `6efcf14`: `docs/build/submission-final.md`), `p3-fix2`, `p6-prod` (CI 7/7 green on GitHub), `p5-stale`, `p5-lit`, `p4-harness`, `gatecheck` (detached, for clean gate runs), `p1-fix`, `p2-fix`.
- Key docs on the build branch: `AGENTS.md` (Codex rules), `docs/build/PHASES.md` (charter and gates), `switch-facts.md`, `codex-boundary.md` (Codex approval design + spike result), `spikes/codex-elicitation.md`, `adr/000-spikes.md` (P0 runs 1-8, S6), `adr/001-codex-mcp-registration.md`, `access-control.md`, `team-impact.md`, `resource-plan.md`, `remote-host.md`, `modal-hosting.md`, `p1-ledger.md`, `p2-mcp.md`, `p3-agents.md`, `audits/p1-audit.md`, `p2-audit.md`, `p3-audit.md`.

## 4. Gates (orchestrator runs them; builders may not edit `scripts/gates/**`)

- `scripts/gates/common.py` universal checks: uv sync --locked, ruff + format, pyright, full pytest, no U+2014, gate baseline (`docs/build/evidence/gate-baseline.txt`), secret scan, red-before-green replay (`docs/build/evidence/pN.json`), claimed test IDs (`scripts/gates/phase_ids.json`). Test-change reasons: rows in any `docs/build/evidence/*-test-changes.md` for modified pre-existing tests.
- `p1.py` (coverage >= 90%, I-01 race x50, lq init/seed/audit verify), `p2.py` (real stdio MCP probe: tool lists per profile, propose, commit in `--binding certify`, idempotent repeat, tamper -> DECISION_MISMATCH), `p3.py [--live]` (lq setup/lint/doctor, fail-closed binding, one commit per process, live agent config via Console RPC).
- Re-baseline after any gate edit: commit, write HEAD sha to `gate-baseline.txt`, commit. Run gates in a clean worktree for independence.

## 5. Phase status

| Phase | Status |
|---|---|
| P0 environment | DONE. Docker 4.98, Switch Console v0.40.1, local server switch-core 0.31.0, Mattermost 11.9.0 on 127.0.0.1:52564; S0 (Codex PONG reply), S1 (unclaimed refused), S4, S6 (27% RAM headroom), personas `prof-rao` (claimed to Nikhil admin), `maya` (own Switch user), Darshan onboarded |
| P1 ledger core | DONE, on main |
| P2 MCP server + CLI | DONE, on main |
| P3 agents/Codex/template/binding | Built; orchestrator ran `p3.py --live` green at `183ee14`; Terra audit FAIL -> fixes merged (ACLs, hard-link certify ledger, launcher, stable MCP path, requester from sender, Darshan seeded, only commit_booking prompts, seed backfill, post_message instructions) |
| P4 live certification | IN PROGRESS (run `p4live4.log`, output `out\p4live-last.md`) |
| P5 stale + literature | Built, integrated (in release-prep) |
| P6 production | CI hardening, backup/restore, LICENSE/SECURITY/CONTRIBUTING, final README, demo recorder, submission text: done; release pending |

Overall estimate ~80%. Remaining after P4: release (Terra, armed: merge release-prep + P4 evidence, clean-worktree gates incl. `--live`, PR, CI green, merge, tag v1.0.0, notify Darshan), then human items (section 9).

## 6. Live environment facts

- Switch Console must be launched with `scripts/ops/launch_console.ps1` (refreshed machine+user PATH so `docker-credential-desktop` resolves; `CODEX_HOME=%LOCALAPPDATA%\LabQuorum\codex-home`; `--remote-debugging-port=9333`). Switch builds each agent session home from `CODEX_HOME || ~/.codex` (`shared-config.ts:160-166`), so agent lock-down lives ONLY in the LabQuorum codex home; the user's `~/.codex/config.toml` must stay clean (backup of the bad version: `config.toml.bak.labquorum-p3-1822`; user default model `gpt-6.1-terra`/`high`).
- Automation is API-only: Console RPC over CDP (`window.electronAPI.invoke`, wrapper `scripts/ops/switch_rpc.py`), Console control API (`%APPDATA%\switchdash\control-api.json`, header `x-switch-control-token`), Switch server REST (`http://localhost:52563`, gateway 52562; users `POST /gateway/users`, identity claim via collaborations route, template-document API `core/switch_core/gateway/rooms.py:619-679`, approval answer route `agent_sessions.py:169-188`), Mattermost REST v4. Persona credentials only in `%LOCALAPPDATA%\LabQuorum\personas.json`.
- Room: private `rao-labquorum` (Mattermost slug `rao-labquorum-cb95ddef`), agents `rao-labops` (anyone, proposer profile) and `rao-pi-desk` (owner-agents, approver profile), aliases `labops`, `pi-desk`. Members: prof-rao, maya, darved2305.
- Runtime root `%LOCALAPPDATA%\LabQuorum` (ledger `ledger.sqlite`, agents folders, codex-home). Ledger schema now v3 (P5); upgrade path from commit 853a7ac.
- Switch session journals: `%USERPROFILE%\.local\state\switch\sdk-sessions\<hash>\events.jsonl` (ground truth for `request.opened` approval events).
- Network: laptop on Darshan's tailnet as `labquorum-host` (100.127.12.9); Mattermost shared tailnet-only at `http://labquorum-host.tail7b113e.ts.net:8065` (`tailscale serve --bg --http=8065 http://127.0.0.1:52564`; use the hostname, IP gives 404). Tailscale adapter set Public, accept-routes off, SSH/exit node/drive off. Open signup accepted while tailnet-only (`docs/build/access-control.md`). If tailscaled hangs at "starting", launch `tailscale-ipn.exe`.
- `.wslconfig` caps WSL at 5 GB / 4 CPUs (applies at next WSL restart); sleep on AC disabled.

## 7. Key technical findings (do not rediscover)

1. Codex 0.166.0 does NOT forward server-initiated MCP elicitation to app-server (spike); the binding design is: native Codex tool-call card for `commit_booking` (`approval_mode = "prompt"`), all other labquorum tools auto-approved, one binding commit per server process (`BINDING_COMMIT_LIMIT`), fail-closed binding modes (`off` default, `certify` only on an isolated test ledger, `on` only with certification evidence matching the installed tuple), flat human-readable card fields bound by the canonical content hash, serialized args < 900 chars.
2. The commit card WORKS: journal shows `request.opened` "labquorum wants to run commit_booking" within 5 ms. Detect approvals via gateway `kind == "approval"` (not `mcp_tool_approval`), take the baseline before posting, answer with returned option ids, never reset a session while an approval is pending.
3. Switch hosted agents must reply with the `post_message` tool; final assistant text is not shown in chat (`hosted.ts:91-98`). Fixed in agent instructions; visible replies confirmed (35 s).
4. After a Console relaunch, agents may start but not re-attach to the controller stream (no "Agent attached to the controller stream" log); fix by reloading agents via Console RPC / clean relaunch. Running agent hosts can cache old MCP config: reload after `lq setup` changes.
5. Console template runs abort after 30 s; use the server template-run API. Template agent names must not collide with room aliases.
6. `@pi-desk` refusal to non-owners is Switch's own message ("You're not permitted to direct messages to me in this room..."): good demo beat.
7. P3 `lq setup` once wrote agent settings into the global `~/.codex/config.toml` (blinded every Codex run); fixed, guarded.
8. A Codex `exec` process can hang after writing its `-o` file; downstream triggers should key on the output file, not process exit.

## 8. Darshan / GitHub issues

- #1 Tailscale + Mattermost onboarding (done). #2 Wispr (export at the very end). #3 blog (facts sheet on `ship-docs`, his `docs/build/facts-for-blog.md` is canonical). #4 QA, accessibility, video edit (demo recorder `docs/build/demo-recording.md`). #8 his live run: found 3 bugs (read-only tool cards answerable by the student, requester hard-wired to Maya, card answers misread as training), all fixed; he slept before retesting; a Maya retest proved AR-0044 created correctly; he should retest Friday.

## 9. Remaining work

1. P4 finishes: Maya visible-reply smoke (conflict Lena 14:00-15:30, proposal 15:45-16:45, request id, < 2 min, zero cards); certification scenarios (student cannot answer, prof-rao Approve once -> exactly one matching commit, decline, second commit blocked, injection cannot commit, model proof); `certification.json` (binding on) or proposal-only; `docs/test-evidence.md`; commits after each scenario.
2. Release (Terra): brief `tmp\briefs\release.md` (merge `release-prep` + P4 evidence, completeness ancestor checks, clean-worktree gates incl. `--live`, PR to main, CI green, merge, `v1.0.0` + GitHub release, notify Darshan on #4/#8, report final origin/main sha).
3. Human: record demo with `scripts/demo/record_demo.py` (two windows; `--proposal-only` fallback), Darshan edits to < 3:00 and uploads unlisted; Darshan retests #8 and publishes blog; export both Wispr cards last; make repo public; Nikhil pastes `docs/build/submission-final.md` into the form.
