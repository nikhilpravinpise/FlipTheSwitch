# Demo recorder

`scripts/demo/record_demo.py` records one real LabQuorum room run with separate student and PI Mattermost accounts. It does not start Switch or Mattermost, seed or reset the ledger, or invent chat replies. The student sends through the Mattermost composer with a 45 ms per-character delay by default. The harness REST client observes the student post, agent reply, approval card, settled card, and durable ledger state.

## Install and run

Install the optional recorder dependency and its Chromium browser:

```powershell
uv sync --extra demo
uv run playwright install chromium
```

Use proposal-only mode unless the installed P4 binding tuple has completed certification:

```powershell
uv run python scripts/demo/record_demo.py --proposal-only
```

The default student is `maya`. To use Darshan's Mattermost account, add his credentials under a separate persona entry in `%LOCALAPPDATA%\LabQuorum\personas.json`, then select its username:

```powershell
uv run python scripts/demo/record_demo.py --proposal-only --student darved2305
```

LabOps records the Switch sender's handle as the requester, so the recorder expects the ledger request to belong to the selected student's Mattermost username (for example `darved2305`), not `maya`. That username must exist as a ledger person with valid INS-01 training; the demo seed includes `darved2305` with an INS-01 training record. The student types a first-person request: `@labops, can I book INS-01 (plate reader) for 60 minutes on <date> between 14:00 and 17:00 Asia/Kolkata?`. The Darshan take is covered by offline tests only; a live take with `--student darved2305` is still UNVERIFIED.

Before recording, confirm the ledger has a future committed Lena INS-01 booking from 14:00 to 15:30 local time. The demo seed anchors that booking to the seed's anchor date, so a ledger seeded for Friday 6 November has no conflict on later days. Pass `--request-date` only for a date that actually has that conflict.

The current persona file may use `server` and `private_room.id`; the P4 fields `mattermost_url` and `channel_id` are also accepted. Extra persona entries are loaded in memory for the selected student. Password values are never printed or written to timing evidence. An optional `--student-state` and `--pi-state` can load Playwright storage-state JSON files instead of adding an API login cookie to each browser context. The REST clients still log in with the persona file so the recorder can observe actual events.

Binding mode is an explicit opt-in and requires prior approval-path certification for the installed Console, provider, MCP server, and template tuple. Do not use this flag as a substitute for that certification:

```powershell
uv run python scripts/demo/record_demo.py --binding-certified
```

The PI account must be allowed to read deleted Mattermost posts for the harness to confirm that Switch settled the native card. The recorder clicks a single visible `Allow once`, `Approve once`, or equivalent action on the PI page. It fails closed if the action is absent or ambiguous, then checks the settled card and committed booking through the API and read-only ledger inspector.

## Inputs and output

The default persona path is `%LOCALAPPDATA%\LabQuorum\personas.json`. The channel is resolved from its configured ID using Mattermost's channel and team APIs. The path is opened in two headed Chromium windows placed at x positions 0 and 1280. Each browser context records a 1280x720 video. Browser API login uses Mattermost's documented session token cookie, `MMAUTHTOKEN`; no token is written to output. Playwright storage-state files are supported when already available. See the official [Mattermost session authentication reference](https://docs.mattermost.com/api/reference/mattermost-api) and [channel deep-link format](https://docs.mattermost.com/end-user-guide/collaborate/share-links).

Unless `--request-date YYYY-MM-DD` is supplied, the recorder reads the ledger in read-only mode and uses the next future committed Lena INS-01 booking from 14:00 to 15:30 in Asia/Kolkata as the request date. It asks for 60 minutes between 14:00 and 17:00 on that explicit date. It does not reset the ledger. The request and response must satisfy the P4 conflict and 15:45-16:45 smoke assertion before the recorder captions those values.

Output defaults to `%LOCALAPPDATA%\LabQuorum\demo\<UTC timestamp>\`:

- `student-video\` and `pi-video\` contain Playwright's raw WebM recordings. Playwright finalizes them when each browser context closes, as described in its [video recording guide](https://playwright.dev/python/docs/videos).
- `timing.json` records mode, request identity, shot boundaries, UTC step starts, measured event wait durations, status, and whether the recorded sequence stayed below 180 seconds.
- `shots.md` lists sequence-relative in/out timestamps and measured waits for Darshan's edit. Raw videos include page-load pre-roll before the first caption.

Use `--output-dir` for a different local destination. `--timeout` sets each API or UI event timeout. Polling defaults to 0.5 seconds and cannot exceed 2 seconds. `--end-card-hold` is capped at 2 seconds. The timing log covers the recorded workflow sequence; inspect the actual WebM duration and captions before exporting a cut. The target is 2:15 and the submission cap is strictly under 3:00.

The recorder displays the audit tail by running `lq audit tail --db <temporary copy> -n 5` after the status check. It makes that consistent copy through a read-only SQLite connection, runs the CLI on the copy, and deletes the temporary directory afterwards. Sensitive-looking audit keys and token strings are redacted before the text is injected into the page.

## Proposal-only behavior

`--proposal-only` still records the real request and student refusal attempt, but it does not wait for or click an approval card and never waits for or claims a commit. It checks again after the refusal that the request remains pending, has no commit event, and has no approval card in its thread. It displays `Proposal only - not booked` and shows the request-linked audit tail. If an actual approval card appears, the run fails and the take must not be used as an approval-free proposal cut. The active Switch profile must also be configured for the proposal-only fallback before recording.

The recorder never posts to Mattermost from a test. Pinned Switch v0.40.1 parses typed card answers in `core/switch_core/bridges/collaboration/session/text.py:141-156`. Its Mattermost callback handles the signed action context and visible labels in `core/switch_core/bridges/collaboration/mattermost/callback.py:183-227`, and the session bridge checks identity before applying the answer in `core/switch_core/session_activity/bridge_answers.py:177-205`. The recorder uses the PI's real visible Mattermost action button; its API wait then confirms settlement through the same event path the P4 harness documents in `docs/build/p4-harness.md`.

## Offline checks

The unit tests under `tests/demo/` use fake API clients, pages, and ledger snapshots. They do not run this script's live recording command. This build did not open the live Console, log in to Mattermost, or post a message.
