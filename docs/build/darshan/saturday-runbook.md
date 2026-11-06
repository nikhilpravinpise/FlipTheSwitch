# Saturday 7 November runbook (issue #14)

One ordered page for the human-only work in [issue #14](https://github.com/nikhilpravinpise/FlipTheSwitch/issues/14). Detailed procedures stay in the linked files. Keep private URLs, credentials and Tailscale details out of issues, PRs, screenshots, video and the repo. All lab records are synthetic.

## 0. Host pre-flight (Nikhil's laptop, before 09:00 IST)

The live room only exists while Nikhil's laptop is on and on the tailnet. Do these on the host, in order:

1. Pull `main` with every merged QA PR. The requester-scoped tool fix changes the `check_availability` and `cancel_my_proposal` arguments, so the runtime must be refreshed: `uv run lq setup`, then reload both agents. Running agent hosts keep an old MCP config until reloaded (see `docs/build/orchestrator-handoff.md`, finding 4).
2. `uv run lq doctor --runtime-root "$env:LOCALAPPDATA\LabQuorum"` must report `RUNTIME_BINDING_OFF`. The whole day is proposal-only.
3. Confirm a future committed Lena INS-01 booking from 14:00 to 15:30 IST exists on the day you will request. Read-only check:

   ```powershell
   uv run python -I -c "import pathlib,sqlite3,sys; c=sqlite3.connect(pathlib.Path(sys.argv[1]).as_uri()+'?mode=ro', uri=True); [print(r) for r in c.execute('SELECT id, start_utc, end_utc, status FROM booking WHERE person_id = ? AND instrument_id = ? ORDER BY start_utc', ('lena', 'INS-01'))]" "$env:LOCALAPPDATA\LabQuorum\ledger.sqlite"
   ```

   14:00-15:30 IST is 08:30-10:00 UTC. If the only conflict is in the past (for example Friday 6 November), the retest and the demo will show no conflict. Deciding whether to reseed or add a booking is Nikhil's call, because it changes the shared ledger; never do it while a take is running.
4. Saturday is an open day for INS-01 (08:00-20:00) and Sunday is closed, so "the next open day" on Saturday means Saturday itself.

## 1. Live student retest (09:00-11:00)

Read [issue-1-onboarding.md](issue-1-onboarding.md) and [access-control.md](../access-control.md). Use your own `darved2305` account.

1. Note the local time, then send exactly: `@labops, can I book INS-01 for 60 minutes on the next open day between 14:00 and 17:00?`
2. Record the exact reply text, the time it arrived and the elapsed seconds. If no reply arrives within 5 minutes, record that as a finding. It is the known P1 missing-reply bug, so do not resend in the same thread.
3. Expected: the reply names the actual conflict (owner and interval), proposes a free same-length slot, names you as requester, gives a request ID and says it is pending and not booked. No approval card appears that you can answer.
4. Within 10 minutes of the proposal, have Nikhil run `uv run lq request show <request ID> --db "$env:LOCALAPPDATA\LabQuorum\ledger.sqlite"` and paste the JSON (no paths) into the issue. Expected: `status` `pending`, `requester` `darved2305`. Proposals expire 10 minutes after creation, so a later read shows `expired`.
5. Send `@pi-desk, approve my request <ID>`. Expected: Switch refuses you as a non-owner and the request is unchanged.
6. File each deviation as its own new issue with the template in [issue-4-qa-video.md](issue-4-qa-video.md#one-finding-per-issue).

## 2. Accessibility review (11:00-13:00)

Follow steps 7-9 of the [live QA procedure](issue-4-qa-video.md#live-qa-procedure): keyboard only, screen reader, grayscale, 200% zoom, plus a first-time read of `README.md`. Record OS, browser and screen-reader name and version. Mark any check you could not perform UNVERIFIED. One issue per observed failure.

## 3. Blog and #HowISwitch (13:00-14:00)

Use [issue-3-blog.md](issue-3-blog.md), then fact-check every claim against the "Update (6 Nov evening)" section of [facts-for-blog.md](../facts-for-blog.md) and your own retest. Do not say P4 is certified or that the isolated approval proves the deployed workflow. Name the ledger whenever you cite a request ID, because IDs restart per ledger.

## 4. Record the demo (14:00-15:00)

Prerequisites and flags: [demo-recording.md](../demo-recording.md). The recorder does not start or seed anything, so section 0 must already be done.

```powershell
uv sync --extra demo
uv run playwright install chromium
uv run python scripts/demo/record_demo.py --proposal-only --student darved2305
```

The recorder now expects the ledger requester to be the selected student (`darved2305`) and types a first-person request. That path is covered by offline tests only, so watch the first take closely. Keep the raw files under `%LOCALAPPDATA%\LabQuorum\demo\<UTC timestamp>\` (`student-video\`, `pi-video\`, `timing.json`, `shots.md`).

## 5. Edit and upload (15:00-16:30)

Follow the beats in [demo-script.md](../demo-script.md) and the proposal-only edit list in [issue-4-qa-video.md](issue-4-qa-video.md#215-edit-script-proposal-only-baseline): real request, actual conflict and alternative, pending state, certification limit, repository. Keep the synthetic-data label. Caption any cut wait with its real duration, and never speed waits up silently. Export under 3:00 (target 2:15), then watch the actual file with audio and captions. Upload unlisted, then play it in a logged-out window.

## 6. Submission PR (16:30-17:15)

On a branch from `main`, fill the TODO lines in [submission-final.md](../submission-final.md) and the README video line, resolve its retest TODO from your section 1 evidence, and work through its "Before submitting" checklist. Open the PR to `main`; Nikhil merges.

## 7. Wispr card (17:30-17:40)

Only after the last genuine dictation: Insights > Your usage > Share. Check that the export opens and is legible, then attach the original file to [issue #2](https://github.com/nikhilpravinpise/FlipTheSwitch/issues/2). See [issue-2-wispr.md](issue-2-wispr.md).
