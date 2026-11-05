# Issue 1: join the live test chat

Source: [upstream issue 1](https://github.com/nikhilpravinpise/FlipTheSwitch/issues/1).
Inspection date: 2026-11-05. Status: preparation complete; live onboarding NOT COMPLETE.

## Observed on this Windows machine

| Read-only check | Result |
| --- | --- |
| `Get-Command tailscale -ErrorAction SilentlyContinue` | No command found on PATH |
| `Test-Path -LiteralPath 'C:/Program Files/Tailscale/tailscale.exe'` | False |
| `Get-Service -Name Tailscale -ErrorAction SilentlyContinue` | No service found |
| Tailscale account, tailnet and authenticated browser session | UNVERIFIED |
| Nikhil's reachable Mattermost address and invite | Not supplied in the issue body; issue 1 comments were checked and empty in this session |

These checks establish that no standard installation was visible to this session. They do not exclude a nonstandard installation or another Windows account. No installation, login, key creation, key disclosure or network change was performed.

## Onboarding sequence

1. Install Tailscale on Darshan's machine using the issue's Windows command:

   ```powershell
   winget install -e --id Tailscale.Tailscale
   ```

   Alternatively, use the [official Windows download](https://tailscale.com/download/windows). Open Tailscale and sign in with Darshan's own account. Official installation reference: [Tailscale for Windows](https://tailscale.com/docs/install/windows).

2. Open [Tailscale admin keys](https://login.tailscale.com/admin/settings/keys) in that account. Following the issue's requested configuration, generate a key with Reusable OFF, Ephemeral OFF, Pre-approved ON if shown, expiry 1 day, and no tags. For key behavior, see [official auth-key documentation](https://tailscale.com/docs/features/access-control/auth-keys). Account permissions and available controls remain UNVERIFIED until viewed in the signed-in console.

3. Coordinate the single-use key handoff with Nikhil. The issue asks for a temporary private issue comment followed by deletion after he consumes it. Before that specific handoff, verify the repository is still private and the recipient is correct. Keep the key out of source files, screenshots, terminal output and this document. No key has been created or sent by this run.

4. Wait for Nikhil to enroll his laptop and provide the actual Mattermost address and invite. Use only the supplied private `100.x.y.z` address and port; do not substitute a guessed address or `localhost` on Darshan's machine.

5. In Chrome, open the supplied invite while Tailscale is connected. Create Darshan's own Mattermost account, use display name `Darshan Ved`, join the named team and room, and retain the password privately.

6. Confirm that room history loads and updates without refreshing. Send the agreed synthetic student booking request beginning with `@labops`, and verify an actual agent reply. Record timestamp, room, request ID and the visible time zone with secrets redacted.

7. Test the student role only against the agreed seeded scenario: attempting to approve the student's own request must be refused. Joining Mattermost does not grant PI approval authority. Nikhil remains owner and PI approver; see [team role decisions](../team-impact.md), lines 86-91. A successful chat login alone is insufficient evidence of the refusal or approval boundary.

## Completion evidence still required

- Tailscale installation and Darshan's own account sign-in.
- Nikhil's laptop enrolled and private Mattermost URL reachable from this machine.
- Darshan's distinct Mattermost account and room membership.
- A real `@labops` reply to Darshan and a recorded student-refusal result.

The lightweight teammate setup is intentional: [resource plan](../resource-plan.md), line 20, requires a browser, Tailscale and Wispr Flow on Darshan's laptop, without duplicating Nikhil's server stack. [Build phases](../PHASES.md), line 62, identify Nikhil's laptop via Tailscale as the team's deployment.

Do not close issue 1 based on this runbook. Live connectivity and the identity checks above remain UNVERIFIED.
