# P0 environment spike evidence

Date: 2026-11-05 (IST)
Scope: S0 server and smoke setup, S4 fixture, and S1 identity, following `docs/plan/08-build-schedule.md` section 8.1.
Decision: S0 FAIL. S1 and S4-fixture UNVERIFIED because the required Mattermost service did not start and the stop condition was reached.

## Environment and addresses

| Item | Observed value | Status |
| --- | --- | --- |
| Switch Console | v0.40.1, visible in the Console sidebar and CDP user agent | Running at `http://127.0.0.1:9333` |
| Local Switch server | v0.31.0. Console Home showed Running at 13:35, but by 13:50 no core process or API listener was present and the health probe was refused | FAIL at final check |
| Docker Desktop | v4.98.0, as verified by the orchestrator before this run | Reported |
| Docker Compose | v5.6.1 from `docker compose version` | PASS |
| Gateway URL | `http://localhost:52562`, derived from `local-switch-server/ports.json` gateway port | Not separately probed |
| Switch API URL | `http://localhost:52563`, derived from `ports.json` and pinned `nativeApiUrl` source | Not separately probed |
| Switch health URL | `http://localhost:52563/health`; `GET /health` is the documented public health route | FAIL: the 13:50 local probe was actively refused |
| Mattermost URL | UNVERIFIED. `ports.json` reserved port 52564, but no Mattermost container started | FAIL |
| Mattermost image | Console attempted `mattermost/mattermost-team-edition:11.9.0`; local image list was empty | Digest UNVERIFIED |
| Anonymous usage data | UNVERIFIED. First screenshot from this run was already on the local server startup page, so the preference control was not observed | No change made |
| Claude Code provider | CLI installation and authentication were reported as already present; Console provider settings were not checked | UNVERIFIED; no provider login changed |

The native URL mapping is derived from `%APPDATA%\switchdash\local-switch-server\ports.json`, pinned Console source `native/core-settings.ts:12-27`, and `constants.ts:98`. The health route is listed in pinned Switch docs at `docs/official/internals/identity-and-access.md:25`.

## Acceptance results

| Spike | What was done | Versions and URLs | Timestamp (IST) | Result | Screenshot/evidence |
| --- | --- | --- | --- | --- | --- |
| S0 - local server | Started the native local Switch server. Console Home later showed `Running`; version was 0.31.0. | Console v0.40.1; Switch server v0.31.0; Gateway `http://localhost:52562`; API health `http://localhost:52563/health` (probe refused at 13:50) | 2026-11-05 13:29:11 to 13:50:05 | FAIL at final check; transiently Running at 13:35 | `docs/build/evidence/p0/01-local-server-starting.png`; `docs/build/evidence/p0/02-home-no-mattermost.png`; `docs/build/evidence/p0/03-console-server-unreachable.png` |
| S0 - built-in Mattermost | Console attempted the bundled Mattermost image pull and startup. The Console log records `docker-credential-desktop` missing from `%PATH%`. Docker listed no containers and no images. Home showed 0 messaging apps. | Image tag `mattermost/mattermost-team-edition:11.9.0`; Mattermost port 52564 allocated; no live Mattermost URL or image digest | 2026-11-05 13:30:45 and 13:32:18 | FAIL | `docs/build/evidence/p0/02-home-no-mattermost.png`; redacted diagnostic log in the task temp directory |
| S0 - Claude Code smoke test | No Mattermost room was available. No throwaway room or agent was created and no agent reply was received. | Provider login was left unchanged; no room, agent, or message IDs | 2026-11-05 13:42 | FAIL | No smoke-test screenshot |
| S4-fixture | No synthetic accounts or private test room were created. `personas.json` and persona storage states were not created. | N/A | 2026-11-05 13:42 | UNVERIFIED, blocked by S0 failure and stop condition | No fixture screenshot |
| S1 identity | Unclaimed Maya and PI probes, claims, re-enrollment, and posting checks were not run because Mattermost did not start. | N/A | 2026-11-05 13:42 | UNVERIFIED, blocked by S0 failure and stop condition | No identity screenshot |

S0 overall is FAIL because the built-in Mattermost service and real agent reply are required for acceptance. The Console log shows the `Also run Mattermost` startup path was attempted, but the service never became available. The local server status alone does not make S0 pass.

## Failure diagnosis and stop record

The Console log at `%APPDATA%\switchdash\logs\switch-console.log` records these failures:

- 2026-11-05 13:30:45 IST: the pre-pull failed because Docker could not execute `docker-credential-desktop`.
- 2026-11-05 13:32:18 IST: Mattermost startup failed for the same missing helper. The error was `exec: "docker-credential-desktop": executable file not found in %PATH%`.
- `docker ps -a --no-trunc` returned no containers. `docker images --digests` returned no images. There was no container ID to pass to `docker inspect` or `docker logs`, so Docker container inspection/log retrieval was unavailable.
- By 2026-11-05 13:50 IST, no `switch_core.main` process or listener on API port 52563 was present. A single `GET http://localhost:52563/health` probe was actively refused, and the Console showed `Rooms may be out of date - couldn't reach Default`. The reason the local server stopped is UNVERIFIED; it was not restarted.
- Two Playwright attempts to open the Console Admin page timed out. After the second attempt, UI work stopped as required. An earlier Home capture showed 0 messaging apps; the final Console capture showed `Your Agents` with a reachability warning.

The pinned `docs/official/resources/troubleshooting.md` does not give a Console log path. The pinned Console source defines the filename as `switch-console.log` at `console/apps/switch-console-desktop/src/main/lib/file-logger.ts:17` and sets the log directory under the app user-data path at lines 107-110. Filtered diagnostic copies were saved outside the repo at `C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\p0\diagnostics\console-relevant-redacted.log` and `C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\p0\diagnostics\console-final-relevant-redacted.log`.

The Mattermost toggle is exposed as `Run Mattermost` in the managed server page in pinned source `console/apps/switch-console-desktop/src/renderer/features/switch-servers/managed-server-view.tsx:333-356`. The official add-server doc says Mattermost is on by default when Docker is available and can be switched later from the server page at `docs/official/getting-started/add-a-server.md:39`.

## Stop and resume instructions

1. Have a human repair Docker Desktop's credential-helper availability for the Docker CLI used by Switch Console. In the same Windows account, `Get-Command docker-credential-desktop.exe -ErrorAction SilentlyContinue` should resolve to a path. If it does not, repair the Docker Desktop installation or PATH so its credential helper is resolvable. Do not change provider logins.
2. In Switch Console, open the local managed server page and enable `Run Mattermost`. Wait for the service to finish starting, then confirm the Home page lists a messaging app and record its sign-in URL, image ID, and digest.
3. Resume the remaining S0 provider and smoke flow, then S4 fixture, then S1 identity, in the schedule's order. Keep generated persona credentials only in `%LOCALAPPDATA%\LabQuorum\personas.json` and persona browser states only in the specified LocalAppData folder.

The Console was left running with CDP on port 9333; a final request to `http://127.0.0.1:9333/json/version` returned HTTP 200. No product code, provider login, Mattermost account, persona credential, or browser storage state was changed or created.

## Command outcomes

| Command | Result |
| --- | --- |
| `Invoke-WebRequest -Uri 'http://127.0.0.1:9333/json/version' -UseBasicParsing` | PASS. CDP responded and reported Switchdash/0.40.1. |
| `uv run --no-project --with playwright python -I 'C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\scripts\cdp_shot.py' 'C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\p0\shots\00-welcome.png'` | FAIL after the screenshot was written. `print` raised `UnicodeEncodeError` for a console glyph under cp1252. |
| `$env:PYTHONIOENCODING = 'utf-8'; uv run --no-project --with playwright python -I 'C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\scripts\cdp_shot.py' 'C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\p0\shots\01-server-starting.png'` | FAIL for the same encoding error because Python isolated mode ignored that environment setting. Later UTF-8-safe helper scripts succeeded. |
| `uv run --no-project --with playwright python -I 'C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\p0\console_action.py' 'C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\p0\shots\08-admin-nav.png' click-role button Admin` | FAIL. No screenshot was produced within 30 seconds; a later screenshot showed the Home page unchanged. |
| `uv run --no-project --with playwright python -I 'C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\p0\console_action_safe.py' 'C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\p0\shots\10-admin.png' click-role button Admin` | FAIL. Playwright `Locator.click` timed out after 5000 ms. This was the second Admin-page attempt, so UI work stopped. |
| `& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' ps -a --no-trunc` | PASS. No containers listed. |
| `& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' images --digests` | PASS. No images listed. |
| `& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' compose version` | PASS. Docker Compose v5.6.1. |
| `uv run --no-project --with playwright python -I 'C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\p0\console_state.py' 'C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\p0\shots\11-final-home.png'` | PASS. Captured the final `Your Agents` page with the server reachability warning. |
| `Invoke-WebRequest -Uri 'http://localhost:52563/health' -UseBasicParsing -TimeoutSec 5` | FAIL. Connection actively refused at 2026-11-05 13:50 IST. |
| `Invoke-WebRequest -Uri 'http://127.0.0.1:9333/json/version' -UseBasicParsing -TimeoutSec 5` | PASS. CDP returned HTTP 200; Console remained running. |
| Docker `inspect` and `logs` | Not run because no container ID existed. |
| Repository tests, lint, and type checks | Not run. No product code was changed and the environment stop condition applied. |

## Run 2 - 2026-11-05

Scope: resume S0, S1, and S4-fixture after the orchestrator refreshed the PATH inherited by Switch Console. Run 1 remains above unchanged.

### Environment and verified endpoints

| Item | Run 2 observation | Result |
| --- | --- | --- |
| Switch Console | v0.40.1; remained running with CDP on `http://127.0.0.1:9333` | PASS |
| Switch core | v0.31.0 from the installed bundle metadata | PASS |
| Docker Desktop | v4.98.0, as verified by the orchestrator; not re-probed in this run | Reported |
| Docker Compose | v5.6.1 | PASS |
| Switch Gateway | `http://localhost:52562` from the local server ports metadata | Address verified; Gateway UI was not opened |
| Switch API | `http://localhost:52563` | PASS, `GET /health` returned HTTP 200 and `{"status":"ok"}` at 2026-11-05 14:30:58 IST |
| Mattermost | `http://localhost:52564` | PASS, `GET /api/v4/system/ping` returned HTTP 200 at 2026-11-05 14:30:58 IST |
| Mattermost container | `switchdash-local-mattermost-mattermost-1`, healthy, loopback publish `127.0.0.1:52564->8065/tcp` | PASS |
| Mattermost image | `mattermost/mattermost-team-edition:11.9.0`; repo digest `sha256:1c538cf33c2144ba2c825571cd414aaaebf8d8c231d4b18081b811cd0ca0ef2a` | PASS |
| Claude Code provider | `claude --version` reported 2.1.318; Console showed Installed and Signed in | PASS; login unchanged |
| Anonymous usage data | Settings screenshot showed the sharing switch off | PASS; no change made |

The Console process was restarted by the orchestrator at 14:12 IST before this run's UI work. CDP stayed available, so it was not relaunched by this operator.

### Acceptance results

| Spike | What was done | Timestamp (IST) | Result | Evidence |
| --- | --- | --- | --- | --- |
| S0 - server and Mattermost | Probed Switch health and Mattermost system ping; inspected the running container, port mapping, image tag, and digest | 2026-11-05 14:30:58 | PASS for server and Mattermost availability | `docs/build/evidence/p0/06-run2-home-mattermost.png` |
| S0 - provider | Checked the Claude Code CLI version and Console provider status; made no provider login changes | 2026-11-05, during the 14:12-14:30 UI session | PASS for installed and signed-in provider | `docs/build/evidence/p0/05-run2-claude-provider.png` |
| S0 - real-agent smoke | The Admin navigation stop condition occurred before a throwaway room or agent was created. No Claude Code agent reply was received in Mattermost. | 2026-11-05, during the 14:12-14:30 UI session | FAIL, smoke requirement not met | `docs/build/evidence/p0/07-run2-admin-stop.png` |
| S4-fixture | No `prof-rao` or `maya` Mattermost account, private room, persona credentials file, or browser storage state was created. | 2026-11-05, during the 14:12-14:30 UI session | UNVERIFIED, stopped at Admin navigation | No fixture screenshot |
| S1 identity and claims | No unclaimed probes or claims were run. The Console still showed `@user` linked to Switch user `admin`; `@prof-rao` was not linked. | 2026-11-05, during the 14:12-14:30 UI session | UNVERIFIED, stopped at Admin navigation | `docs/build/evidence/p0/06-run2-home-mattermost.png` and `07-run2-admin-stop.png` |

S0 overall remains FAIL because a real agent reply is part of the smoke acceptance, even though the local Switch server and Mattermost were healthy. The four new screenshots bring the P0 evidence set to seven PNGs, below the 12-image limit. No passwords or secret values appear in the committed screenshots.

### Stop condition and diagnostics

Two attempts to open the same Switch Console Admin section failed. The first Playwright attempt used `page.get_by_role("button", name="Admin", exact=True).click(timeout=10000)` and failed because the sidebar button had no accessible name in the page snapshot. The second attempt targeted the Admin sidebar button through the registered `switch-console` browser tool and timed out after 5000 ms while waiting for the element to become visible, enabled, and stable. The stop rule was then applied. CDP remained HTTP 200, so the Console was left running and was not restarted.

Console and Mattermost diagnostic copies were saved outside the repository under `C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\p0\diagnostics\`. The full Console log copy predates the UI attempts, so it does not contain a new navigation error. The Mattermost container tail was collected after the service was healthy. Neither diagnostic copy is committed.

### Identity model and onboarding procedure

The seeded local Mattermost account `@user` is linked to the Switch Gateway admin by the local server setup path (`deploy/shared_resources/setup.py:357-400` in pinned Switch source v0.40.1). On this machine that Switch account is `admin`, owned by Nikhil. For the requested owner persona, create the Mattermost account `prof-rao`, then sign in to Switch Console as Nikhil's existing `admin` user, open the local server Home page, choose **Link** under **Messaging apps**, search for `prof-rao` by handle, name, or email, then choose **This is me**. This links the platform identity to Nikhil's existing Switch user; it does not create a second Switch user. The procedure is identified from the pinned add-server documentation and Console identity search UI, but was not executed because of the stop condition. See `docs/official/getting-started/add-a-server.md:72-104`, `console/apps/switch-console-desktop/src/renderer/features/switch-servers/link-account-prompts.tsx:35-50`, and `bridge-identity-search.tsx:285-320` in pinned Switch source v0.40.1.

A second, independent Switch user for Maya is supported. The Gateway Users page has **Add User** with Name, Email, Password, and Role fields; choose role `user`. The API endpoint is `POST /users` and requires an admin. After creating that account, sign in as Maya and use the same Home page > Messaging apps > Link > search `maya` > **This is me** flow to claim her Mattermost identity to her own Switch user. This was not executed. Source: `gateway/src/pages/users/UsersPage.tsx:41-52`, `CreateUserDialog.tsx:58-92`, `gateway/src/data/api.ts:1331-1347`, and `core/switch_core/gateway/auth_routes.py:501-507` in pinned Switch source v0.40.1.

An unclaimed Mattermost account matches no Switch user, so it cannot match an `owner`, named user, or `owner_agents` rule. Source: `docs/official/internals/identity-and-access.md:124-134`. Source-based inference, not runtime-tested: an unclaimed human can address an agent whose effective policy is open with no rules, because `AddressingPolicy.allows` permits every non-platform sender in that case (`core/switch_core/addressing.py:153-190`). Newly registered agents default to owner-only, so Maya cannot address those as the owner until her platform account is claimed. No unclaimed behavior was probed in this run.

Create the personas' Mattermost credentials only at `%LOCALAPPDATA%\LabQuorum\personas.json` and their browser states only at `%LOCALAPPDATA%\LabQuorum\state-prof-rao.json` and `%LOCALAPPDATA%\LabQuorum\state-maya.json`. None of these files exists as a result of this run.

### Admin credential location and team invitations

The Mattermost admin password is generated in the local server secret bundle and held by Console's encrypted app-secrets store. The credential location is `%APPDATA%\switchdash\switchdash.db` (the Console database; the stored app secret is encrypted with Electron `safeStorage`). The local host uses the secret key `local-switch-server:secrets`. No password value was read or recorded. Source: `secret-values.ts:3-5, 30, 38-50`, `host/local-host.ts:58-62`, `encrypted-app-secrets-store.ts:40-58,84-99`, and `db/default-path.ts:4,13-34,45-47` in pinned Switch source v0.40.1.

To create a Mattermost team invite link later: select the team name at the top of the sidebar, choose **Invite People**, then **Copy invite link**. To invalidate or replace it, open **Team Settings > Access > Invite Code > Regenerate**. Sources: [Mattermost invite people](https://docs.mattermost.com/end-user-guide/collaborate/invite-people) and [Mattermost team settings](https://docs.mattermost.com/help/settings/team-settings).

### Run 2 command outcomes

| Command or action | Result |
| --- | --- |
| `Invoke-WebRequest -Uri 'http://localhost:52563/health' -UseBasicParsing -TimeoutSec 5` | PASS, HTTP 200 with `{"status":"ok"}` at 14:30:58 IST |
| `Invoke-WebRequest -Uri 'http://localhost:52564/api/v4/system/ping' -UseBasicParsing -TimeoutSec 5` | PASS, HTTP 200 at 14:30:58 IST |
| `docker compose version` | PASS, Docker Compose v5.6.1 |
| `docker ps` and container/image inspection | PASS, healthy Mattermost container, expected loopback port, image tag and digest recorded |
| `claude --version` | PASS, Claude Code 2.1.318 |
| Playwright capture of settings and provider pages | PASS, sharing off and Claude Code signed in were visible |
| First Admin navigation via accessible role locator | FAIL, the button had no accessible name in the snapshot |
| Second Admin navigation via `switch-console` browser tool | FAIL, 5000 ms wait for visible, enabled, stable element timed out; stop condition applied |
| Console and Mattermost diagnostic collection | PASS, copies saved outside the repository; no secrets copied into evidence |
| Repository tests, lint, and type checks | Not run; no product code changed and this environment run stopped at the required UI stop condition |

### Resume work

1. Leave Switch Console running with CDP on port 9333. Resume only after the Admin section can be opened reliably; do not use a different route to bypass the two-failure stop condition in this run.
2. Create a throwaway room and agent, then obtain one real Claude Code reply in Mattermost to complete S0.
3. Create `prof-rao` and `maya` Mattermost accounts, store credentials only in `%LOCALAPPDATA%\LabQuorum\personas.json`, and save their Playwright storage states only in the two LocalAppData state paths above. Confirm both can post in a private room.
4. Keep `prof-rao` linked to Nikhil's existing Switch `admin` user. Create Maya's separate Switch `user` account, sign in as Maya, and claim the `maya` Mattermost identity. Record the required unclaimed and claimed S1 probes.
5. Onboard Darshan later by creating his Mattermost student account and sending him a team invite link using the Mattermost procedure above; create and claim a separate Switch user if LabQuorum's S1 design requires Switch-level identity for student addressing.

## Run 4 - 2026-11-05

Scope: API-only P0 environment run using Switch Console v0.40.1 RPC over CDP and Mattermost REST API v4. No Console UI clicks, typing, or keyboard navigation were used.

### API procedures and evidence

| Area | RPC procedures or API calls | Result |
| --- | --- | --- |
| Console RPC wrapper | `switch_rpc.py list-procedures`; `switchServers.listServers`; `switchServers.getBundledChatSignIn`; `managedAgents.list`; `managedAgents.advancedConfigSchema`; `managedAgents.update`; `managedAgents.setDesiredState`; `workspaces.list`; `workspaces.listBridges`; `workspaces.listRooms`; `workspaces.createRoom`; `workspaces.searchBridgeDirectory`; `workspaces.claimBridgeIdentity`; `workspaces.listMyIdentities`; `switchServers.getAuthConfig`; `switchServers.openGatewayPage` | Wrapper uses `window.electronAPI.invoke` over CDP. Source: pinned `console/apps/switch-console-desktop/src/renderer/lib/ipc.ts:5`, `src/preload/index.ts:5-6`, `src/shared/lib/ipc/rpc.ts:44-63,109-129`, and `src/main/rpc.ts:34-66`. The wrapper is `scripts/ops/switch_rpc.py`. |
| Switch agents | `managedAgents.update` attempted `switch-buddy-admin` provider `codex`, model `gpt-6-luna`, effort `high`; the Console rejected it because the registered agent is Claude Code. `managedAgents.setDesiredState` stopped that built-in agent. `managedAgents.list` verified it stopped and the smoke agent running with provider `codex`, model `gpt-6-luna`, effort `high`, `autoMode=false`, `autoApprove=false`. | PASS for smoke agent settings. Built-in agent remains Claude and stopped. Exact update error: `This agent is registered as 'claude-code', which does not run provider 'codex'.` |
| S0 room and Mattermost post | `workspaces.createRoom` created public bridged room `lq-p0-run4-smoke` with the Codex smoke agent. Mattermost calls: `POST /api/v4/users/login`, `GET /api/v4/teams/name/switch/channels/name/lq-p0-run4-smoke`, `POST /api/v4/posts`, `GET /api/v4/channels/{channel_id}/posts`, and `GET /api/v4/users/{user_id}`. Credentials came from `switchServers.getBundledChatSignIn`; passwords and bearer tokens stayed in process memory. | FAIL for final S0 reply within 180 seconds. `@user` post returned 201. The agent posted a session-start acknowledgment, then requested approval to read `run3-local-sentinel.txt`. `@user` approved request A1 through Mattermost, but a new A2 approval prompt appeared and the exact sentinel reply was not captured. |
| Personas in private room | Mattermost calls: `POST /api/v4/users/login`, `GET /api/v4/channels/{channel_id}/members`, and `POST /api/v4/posts` as `prof-rao` and `maya` in `lq-p0-run3-private`. | PASS; both post requests returned 201. Credentials remain only in `%LOCALAPPDATA%/LabQuorum/personas.json`. |
| Identity linking and S1 | `workspaces.searchBridgeDirectory` found `prof-rao` and `maya`; `workspaces.claimBridgeIdentity` claimed `prof-rao` to the signed-in Switch admin. Mattermost `POST /api/v4/channels/{channel_id}/members` added Maya to the public smoke room, followed by `POST /api/v4/posts` as `maya` mentioning the owner-scoped agent. | PASS for `prof-rao` claim and unclaimed Maya refusal. The Codex agent replied that Maya's account was not linked and it only accepts instructions from its owner. `maya` remained unclaimed. |
| Maya Switch user | `switchServers.getAuthConfig` returned `signupEnabled=false` and `passwordLoginEnabled=true`. Pinned Gateway source exposes admin-only `POST /gateway/users` (`core/switch_core/gateway/auth_routes.py:482-517`), but no Console RPC for creating a Gateway user or issuing an authenticated arbitrary Gateway request was found. Public signup was disabled, so a separate Maya Switch user and claim could not be created through a supported path in this run. | BLOCKED. No credential store was read or decrypted. |
| Codex rollout | Read `CODEX_HOME` from the Codex process environment and searched that per-session home under `sessions/` as required by `docs/build/codex-boundary.md`. The active rollout path disappeared during enumeration and no `turn_context` record with model and effort was recovered. | UNVERIFIED from rollout records. Managed agent settings show the requested model and effort, but do not substitute for the required rollout evidence. |

Mattermost API endpoint shapes follow the official [login](https://docs.mattermost.com/api/reference/mattermost-api), [create post](https://docs.mattermost.com/api/reference/create-post), [channel membership](https://docs.mattermost.com/api/reference/channels), and [users](https://docs.mattermost.com/api/reference/users) references. The Console RPC implementation details above are from pinned Switch source tag `switch-console-v0.40.1`.

### Run 4 command outcomes

| Command or action | Result |
| --- | --- |
| `uv run --no-project --with playwright python scripts/ops/switch_rpc.py list-procedures` | PASS |
| `uv run --no-project --with playwright python scripts/ops/switch_rpc.py call managedAgents.list '["ccf022f8-5ecb-4004-8c1e-d60e65bcce1e"]'` | PASS; output verified Codex settings and stopped built-in agent |
| Mattermost API `POST /api/v4/posts` from `@user` to `lq-p0-run4-smoke` | PASS for API post; FAIL for final S0 reply within 180 seconds |
| Mattermost API persona logins and posts to `lq-p0-run3-private` | PASS for `prof-rao` and `maya` |
| `workspaces.claimBridgeIdentity` for `prof-rao` | PASS |
| Mattermost API unclaimed Maya mention to the smoke agent | PASS; explicit owner-only refusal received |
| Codex per-session rollout parse | UNVERIFIED; active file disappeared during enumeration |
| `uv run ruff check .` | PASS, all checks passed |
| `uv run ruff format --check .` | PASS, 117 files already formatted |
| `uv run pyright` | PASS, 0 errors, 0 warnings, 0 informations after making the optional Playwright import dynamic in the RPC helper |
| `uv run pytest` | FAIL, 82 passed and 2 failed: `test_audit_proposal_can_be_echoed_to_commit` rejects the 81-character project value on `BookingDecisionInput.project`; `test_audit_doctor_rejects_duplicate_profile` does not reject repeated `--profile` options. These existing source behaviors are outside the explicit run 4 staging paths. |

## Run 5 - 2026-11-05

Scope: close the S0 final reply, verify the Codex model from its rollout, create Maya's Switch user and claim, then repeat the two addressing probes. API only; no Console UI clicks, typing, or keyboard navigation.

### Results

| Gap | Result | Evidence |
| --- | --- | --- |
| S0 final reply | PASS | In Mattermost channel `lq-p0-run4-smoke` (`m43uifmkdbns7gww81par4sndy`), `@user` declined the old A2 shell-read approval with post `c4estouihibgunw5dbzufwy5gr`, then posted `@codex.p0-smoke.run3 reply with exactly: PONG 2026-11-05. No shell or file access is needed.` as post `rrxhxx3w13demyariwh9yjiw1r`. The actual agent user `codex.p0-smoke.run3` replied exactly `PONG 2026-11-05`, post `pmh8y9hi63ng9dp8rucy7p9rqw`, at 2026-11-05 11:22:28.901 UTC / 16:52:28.901 IST. |
| Codex rollout model proof | FAIL | The live process had cwd `C:\Users\Nikhil\AppData\Local\LabQuorum\smoke-agent` and per-session `CODEX_HOME` under `C:\Users\Nikhil\.local\state\switch\sdk-sessions\8bdfe369e3cb637b0a2ec15f5e1fae3ee27d6ea164d27adfcc8f7fc7aa8a6256\provider-home\8bdfe369e3cb637b0a2ec15f5e1fae3ee27d6ea164d27adfcc8f7fc7aa8a6256`. A rollout path appeared during enumeration but disappeared before it could be read; no matched `turn_context` lines were recovered, so model and effort for every turn remain UNVERIFIED. Console's managed-agent definition still reports Codex `gpt-6-luna`, effort `high`, but that is not rollout proof. |
| Maya user and S1 probes | FAIL overall | `POST /gateway/users` created Switch user `6b2ee708-1159-4490-afc6-551e4cc4f686`, name `Maya Iyer (synthetic student)`, email `maya@labquorum.invalid`, role `user` (HTTP 200). The first script expected 201 and exited after the successful 200 response; a follow-up GET verified the account. The admin then claimed Mattermost user `tys9b94u7fgrpxtdsdioz8ynmh` (`maya`) to the Switch user through the supported identity route (HTTP 200). With the agent temporarily open, Maya's post `3y4pdu8qwidt5d7knz4mzyin1y` at 17:09:18.766 IST got no agent-authored reply within 75 seconds. After restoring the original owner-scoped policy (HTTP 200), Maya's post `q9pqixe4j7rruyqxewftc93bza` at 17:10:40.038 IST got no agent-authored refusal within 75 seconds. Both probes FAIL. The original policy was restored. |

### API and RPC procedure

The Console RPC helper `scripts/ops/switch_rpc.py` was reused through CDP. RPC calls: `switchServers.getBundledChatSignIn`, `switchServers.openGatewayPage`, and `workspaces.listAgents`. The authenticated Gateway cookie came from the Console-managed session; the pinned client sends it as `Cookie: switch_auth=...` (`console/apps/switch-console-desktop/src/main/core/switch-servers/gateway-client.ts:333-363`). No credential value was written to evidence.

Mattermost REST calls used `POST /api/v4/users/login`, `POST /api/v4/posts`, and `GET /api/v4/channels/{channel_id}/posts?per_page=100`. S0 declined A2 by posting `A2 3` before the tool-free mention. The two Maya probes used the existing Mattermost account and channel.

Gateway calls used `GET /gateway/users`, `POST /gateway/users` with Maya's name, synthetic email, generated password, and role `user`, `POST /gateway/collaborations/6e3161e2-11b7-4b03-9cbe-6788f475bb28/identities` with `external_user_id`, `username`, and `user_id`, and `PUT /gateway/agents/1435e7f9-2947-453a-9272-820bd874ac04/addressing-policy` with `{"policy":null}` for the open probe and the original policy for restoration. Source: `core/switch_core/gateway/auth_routes.py:501-531`, `core/switch_core/gateway/collaborations.py:815-862`, and `core/switch_core/gateway/agents.py:685-724` in pinned Switch v0.40.1.

The session-home derivation is `sha256(sessionId)` under `root/provider-home`, and managed host config supplies that home to Codex (`console/packages/agent-providers/src/codex/home.ts:23-53`, `console/packages/agent-providers/src/host/shared-config.ts:150-165`). The live process environment exposed the home path, but its `sessions` directory yielded no readable rollout. No `turn_context` line can be cited for the required ground-truth model check.

### Run 5 command outcomes

| Command or action | Result |
| --- | --- |
| `uv run --no-project --with playwright python scripts/ops/switch_rpc.py list-procedures` | PASS in Run 4; reused RPC procedures are listed above |
| `uv run --no-project --with playwright python -I <temp>\run5_smoke.py` | PASS; real agent reply captured in under 180 seconds |
| `uv run --no-project --with playwright python -I <temp>\run5_maya_switch_user.py` | API creation succeeded with HTTP 200, but command exited 1 because the script incorrectly expected HTTP 201 |
| `uv run --no-project --with playwright python -I <temp>\run5_claim_maya.py` | PASS; Mattermost login, Gateway user lookup, and identity claim returned HTTP 200 |
| `uv run --no-project --with playwright python -I <temp>\run5_maya_probes.py` | FAIL; neither probe produced an agent-authored response within 75 seconds; owner policy restoration returned HTTP 200 |
| Search in the live per-session `CODEX_HOME\sessions` for a recent rollout with the smoke-agent cwd | FAIL; no stable readable rollout or matched `turn_context` lines |
| `uv run ruff check .` | PASS, all checks passed |
| `uv run ruff format --check .` | PASS, 122 files already formatted |
| `uv run pyright` | PASS, 0 errors, 0 warnings, 0 informations |
| `uv run pytest` | PASS, 101 passed in 53.92 seconds |
| `git diff --check` | PASS, exit code 0; Git warned that the ADR working copy uses CRLF and will be normalized to LF |
| U+2014 scan of Run 5 files | PASS, zero occurrences in `000-spikes.md` and `run5-api.json` |
## Run 7 - 2026-11-05

Scope: API-only onboarding of Darshan Ved following the accepted 19:12 access-control decision. Mattermost remained tailnet-only. The Switch Console RPC opened its authenticated Gateway origin, and all account, identity, and membership changes used HTTP APIs. No UI clicks or typing were used.

### Account discovery and Switch identity

| Area | API calls and result |
| --- | --- |
| Mattermost session | `switchServers.getBundledChatSignIn` supplied the local `@user` login to `POST /api/v4/users/login`. Password and bearer token stayed in process memory and were not recorded. `GET /api/v4/users/me` verified the session as `@user`. |
| Darshan lookup | `GET /api/v4/users?sort=create_at&per_page=50` returned HTTP 400. `POST /api/v4/users/search` for `darshan`, `darved`, `Darshan Ved`, and `darshanmved` returned HTTP 200 and matched Mattermost user `darved2305`, email `darshanmved@gmail.com`, id `uis47eufo3njdjobcuigp8ky1o`. |
| Switch user | `GET /gateway/users` confirmed the email was not already present. Admin-authenticated `POST /gateway/users` created `Darshan Ved (student)` with role `user`; it returned HTTP 200 and the follow-up `GET /gateway/users` verified the same record. A high-entropy initial password was generated in memory and not recorded. The admin-only route and request fields are in pinned Switch source `core/switch_core/gateway/auth_routes.py:501-531`. |
| Identity claim | `POST /gateway/collaborations/{bridge_id}/identities` with Mattermost's user id, username `darved2305`, and the new Switch user id returned HTTP 200. The response listed `Darshan Ved (student)` as the claimant. The claim request's optional target `user_id` is in `core/switch_core/gateway/schemas.py:740-752`; the route and admin check are in `core/switch_core/gateway/collaborations.py:815-862`. |

The Console API session path is pinned at `console/apps/switch-console-desktop/src/main/core/switch-servers/controller.ts:622-637` and `auth.ts:31-33, 76-83, 128-142`. The Mattermost API shapes follow the official [users](https://docs.mattermost.com/api/reference/users) and [channels](https://docs.mattermost.com/api/reference/channels) references.

### Room membership and issue follow-up

The Switch workspace room list contained `rao-labquorum`; its Mattermost private channel slug is `rao-labquorum-cb95ddef`. Direct Mattermost channel lookup also found the private persona test room `lq-p0-run3-private` (display name `LabQuorum P0 Run 3`). As `@user`, `POST /api/v4/channels/{channel_id}/members` added Darshan to both rooms and returned HTTP 201 for each. `GET /api/v4/channels/{channel_id}/members/{user_id}` returned HTTP 200 for both, listing Darshan as `channel_user`.

Issue #1 was updated with both room names and the requested first message: `@labops, can I book INS-01 for 60 minutes on the next open day between 14:00 and 17:00?`. The invite link was not reposted.

No password or token was written to this file. The Switch account's generated initial password was not retained, so direct password sign-in to Switch would need a secure reset or setup path if Darshan needs one.
