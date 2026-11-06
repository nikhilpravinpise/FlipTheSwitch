# Teammate access control (Darshan over Tailscale)

Decided and applied Thu 5 Nov 2026, 18:20 IST. Goal: Darshan (remote teammate, student role) can reach exactly one thing on Nikhil's laptop, the LabQuorum Mattermost web app, and nothing else.

## Network layer

| Control | State | How it was verified |
| --- | --- | --- |
| Laptop joins Darshan's tailnet as `labquorum-host` (`100.127.12.9`) with a single-use auth key he generated | Done | `tailscale status`; Nikhil's own tailnet is kept as a separate profile (`tailscale switch --list`) |
| Only Mattermost is shared, tailnet-only, through `tailscale serve --bg --http=8065 http://127.0.0.1:52564` | Done | `tailscale serve status` shows one proxy, "(tailnet only)"; `GET http://labquorum-host.tail7b113e.ts.net:8065/api/v4/system/ping` returns `"status":"OK"` |
| No public exposure (`tailscale funnel` not used) | Done | `tailscale serve status` lists no funnel |
| Every LabQuorum and Switch service binds loopback only (Switch API and gateway, PostgreSQL, Mattermost container port, Console CDP 9333, Console control API) | Verified | Unsandboxed `netstat -an` shows no listening socket on any non-loopback address |
| Windows Firewall profile of the Tailscale adapter set to **Public** (strictest default: unsolicited inbound blocked unless an app rule allows it) | Done (elevated, UAC approved) | `Get-NetConnectionProfile -InterfaceAlias Tailscale` -> Public; Mattermost still reachable through `serve` afterwards |
| Laptop does not accept subnet routes from Darshan's tailnet | Done | `tailscale set --accept-routes=false`; prefs `RouteAll: false` |
| Tailscale SSH, exit node, Taildrive file sharing | Off | prefs `RunSSH: false`, `ExitNodeID: ""`, `DriveShares: null` |

## Application layer

- Mattermost: Darshan gets a normal (non-admin) account `darshan` through the team invite link (open signup is currently on; see the 19:12 decision below).
- Switch: his identity is claimed to a separate Switch user with role `user` (not admin, not owner of any agent). Addressing makes `@pi-desk` owner-only, so he cannot instruct it or answer its approval cards; he can address `@labops` (anyone).
- GitHub: write access as a collaborator on the private repository (team member), working through branches and PRs.

## Revoking

`tailscale serve --http=8065 off` stops sharing immediately; `tailscale switch <nikhil profile>` or `tailscale logout` leaves Darshan's tailnet; deactivating his Mattermost account and Switch user removes chat access.

## Decision: open signup while Mattermost is tailnet-only (5 Nov 2026, 19:12 IST)

Mattermost's `EnableOpenServer` is on in the Switch-provisioned instance, and the only operator session available to automation is `@user` (team member, not system admin), so it cannot be switched off from our side. Because Mattermost is reachable only through `tailscale serve` inside Darshan's tailnet (his own devices plus `labquorum-host`; never public), open signup does not expose the server to anyone outside the team. We accept it for the build window, share the team invite link with Darshan, and record the risk. If a Mattermost system-admin path is found, or before any wider exposure, open signup must be disabled.
