# P4 live certification evidence

Certification is incomplete. The production runtime manifest remains binding off. No `--binding on` certification record was created.

| Scenario or run | Result | Evidence | Notes |
| --- | --- | --- | --- |
| E2E-01, first attempt | FAIL | [First smoke run](build/evidence/p4/e2e01-20261105T202309048402Z.json) | Timed out before the harness matched a user-facing reply. The temporary ledger had the wrong seed anchor, so the expected conflict was absent. |
| E2E-01, corrected fixture | FAIL in harness | [Second smoke run](build/evidence/p4/e2e01-20261105T204104259972Z.json) | The harness returned on a Switch progress post before the final reply. The author and progress filters have since been fixed and regression tested, but this live run was not repeated. |
| E2E-01, later live observation | Partial, not certified | [Live observation and card post](build/evidence/p4/e2e01-live-observation-AR-0042.json) | Maya received the conflict owner and interval, the 15:45-16:45 IST proposal, and request AR-0042 within 52.081 seconds. The request stayed pending, the audit chain verified, and no commit event existed at capture time. The PI approver card displayed the complete decision, but its Codex approval request was interrupted and the card remains open. |
| Model proof | PASS | [Live observation and card post](build/evidence/p4/e2e01-live-observation-AR-0042.json) | Both live rollouts show `gpt-6-luna` with `high` effort. |
| Refusal, approval once, decline, second commit limit, student answer, injection | NOT RUN | [Live observation and card post](build/evidence/p4/e2e01-live-observation-AR-0042.json) | The target Mattermost channel is private. `prof-rao` is claimed to Nikhil and is on the team, but is not a member of this channel; its channel GET and POST requests return HTTP 403. The open AR-0042 card has not been answered. |

The P4 run cannot continue until the PI persona can access the target room and read settled card posts. The harness also requires system-admin permission for Mattermost's `include_deleted=true` card verification.
