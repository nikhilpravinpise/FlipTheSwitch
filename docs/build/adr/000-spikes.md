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
