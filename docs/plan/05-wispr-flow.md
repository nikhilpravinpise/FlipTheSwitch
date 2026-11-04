# 5. Wispr Flow everywhere

Back to the [master plan](README.md). Goal: win **Code with Wispr** ($500) honestly with authentic voice-assisted build evidence. Event requirement: build by voice (prompts, agent instructions, docs) and submit a screenshot of the Wispr Flow usage scorecard from **Insights** in the desktop app ([event page](https://www.wemakedevs.org/hackathons/switch)).

**Status (Wed 22:20 IST): the event's Flow Pro offer is redeemed.** Active paid plans and trials are exempt from the free weekly allowance; Windows defaults warn after 2,000 words and block above 5,000, subject to account allowances ([free tier](https://docs.wisprflow.ai/articles/4760791189)). Verify the active plan and configured shortcuts in the app.

## 5.1 What Wispr Flow actually is (verified)

| Capability | What it does | Source | Boundary |
| --- | --- | --- | --- |
| Flow dictation | System-wide dictation into any text field; Windows default push-to-talk **Ctrl+Win** | [IDE guide](https://docs.wisprflow.ai/articles/6434410694-use-flow-with-cursor-vs-code-and-other-ides), [terminal guide](https://docs.wisprflow.ai/articles/6478598909-using-flow-with-linux-wsl-and-terminal-applications) | Text entry, not an audio SDK; review before sending |
| IDE and terminal support | Variable recognition in VS Code, Cursor, Windsurf (supported IDEs need Screen Reader Optimized mode); file tagging in Cursor/Windsurf chat; on Windows pastes with Shift+Insert in IDEs; terminals get no variable formatting | [IDE guide](https://docs.wisprflow.ai/articles/6434410694-use-flow-with-cursor-vs-code-and-other-ides), [variable recognition](https://docs.wisprflow.ai/articles/8554805225-variable-recognition) | Dictate prose prompts, not shell syntax |
| Command Mode | Select text, hold the Command Mode shortcut (Windows default Ctrl+Win+Alt), speak an edit; enable in Settings > Experimental; Pro | [Command Mode](https://docs.wisprflow.ai/articles/4816967992-how-to-use-command-mode) | Never use it on data values, DOIs, paths, commands or quoted evidence |
| Dictionary | Custom words and spoken-to-written replacements | [dictionary](https://docs.wisprflow.ai/articles/9639977157-view-shared-dictionary-words-and-snippets-in-the-admin-portal) | Corrects vocabulary, does not validate a number |
| Snippets | A spoken cue expands to saved text | [snippets](https://docs.wisprflow.ai/articles/5784437944-create-and-use-snippets) | Text only; never an "approve" snippet |
| Styles | Formatting per context (formal, casual, very casual, excited; terminals and AI tools use Other) | [styles](https://docs.wisprflow.ai/articles/2368263928-how-to-setup-flow-styles) | Formal punctuation can put a period after a mention (see 5.4) |
| Insights > Your usage | Desktop only (Mac, Windows): words per minute (conditional Top X% ranking), fixes made by Flow, total words (lifetime, desktop + mobile), desktop usage by category (personal messages, work messages, emails, AI prompts, documents, other) with Power/Moderate/Light, distinct apps, daily heatmap with current and longest streak | [usage tab](https://docs.wisprflow.ai/articles/8760230576-your-usage-tab-track-your-dictation-stats-in-wispr-flow) | Lifetime totals include pre-hackathon use; it does not prove productivity |
| Mobile | iPhone Flow keyboard or Android floating Flow bubble | [iPhone](https://docs.wisprflow.ai/articles/7453988911-set-up-the-flow-keyboard-on-iphone), [Android](https://docs.wisprflow.ai/articles/8858845757-setup-wispr-flow-on-android-android-settings) | Test device, permissions, Telegram and identity end to end; 30-minute polish cap, otherwise desktop. |
| Privacy and BAA | Review training, cloud storage and local history separately; demo content is synthetic | [HIPAA](https://docs.wisprflow.ai/articles/4218718535-HIPAA-Compliance-&-Healthcare-Use) | A Wispr BAA does not certify LabQuorum, model providers or chat deployment. Notetaker retention is separate. |
| Remote MCP | Read-only eligible meeting/context records, not dictation history | [guide](https://docs.wisprflow.ai/articles/9551372685-connect-an-mcp-client-to-wispr-flow-remote-mcp-server) | Requires Notetaker and MCP access; active BAA blocks MCP. Zero core hours; <=30 min stretch only after package is green. |
| Dictation API / SDK | No supported public dictation API or SDK verified in this review | [MCP guide](https://docs.wisprflow.ai/articles/9551372685-connect-an-mcp-client-to-wispr-flow-remote-mcp-server) | None used; do not claim an API integration. |

## 5.2 Every place voice is used

| Where | What is dictated | Feature | Expected category, verify in app |
| --- | --- | --- | --- |
| Claude Code and Codex prompts (Windows Terminal, VS Code) | Every implementation prompt: "write failing tests for the booking conflict rules first...", bug reproductions, review requests | Flow; variable recognition in VS Code | AI prompts |
| Test design | Given/When/Then for every E2E and the edge-case catalogue | Flow, then Command Mode "turn this into Given When Then" | Documents |
| Agent instructions and room briefs | The five agents' instructions, `Lab handbook`, project charters in the templates | Flow + Command Mode tightening | Documents |
| Room messages to agents | Manually authored messages to `@scout`, `@labops`, `@analyst`, `@scribe`, `@pi-desk`; automated E2E sends text programmatically and is not voice evidence | Flow; dictionary for handles | Work messages |
| Bench logging (roadmap; not in core) | Observations with sample, time, value, unit, deviation | Flow desktop in Mattermost; tested iPhone keyboard or Android bubble in Telegram (polish) | Work messages / mobile |
| ADRs, spike results, decisions log | `docs/adr/*.md` | Flow | Documents |
| README narrative, blog, video script, voice log | All prose (commands are pasted, not dictated) | Flow + Command Mode | Documents |
| Commit messages, PR and issue text | Every commit body (dictate in the editor `git commit` opens) | Flow | Other / documents |
| Organizer questions, #HowISwitch posts | Discord and social posts | Flow; category and style verified in app | Work messages |

## 5.3 Dictionary and snippets (load tonight)

| Spoken | Written |
| --- | --- |
| "at scout" | `@scout` |
| "at lab ops" / "at labops" | `@labops` |
| "at analyst" | `@analyst` |
| "at scribe" | `@scribe` |
| "at P I desk" / "at pie desk" | `@pi-desk` |
| "lab quorum" | `LabQuorum` |
| "E G C G" | `EGCG` |
| "O D five ninety" | `OD590` |
| "P R T zero zero seven" | `PRT-007` |
| Dunnett, OpenAlex, Crossref, Mattermost, pytest, Playwright, uv, pyright, Switch Console | correct casing |

| Snippet cue | Expands to |
| --- | --- |
| "bench template" | `@labops log: plate=, well=, time=, value=, unit=, deviation=` |
| "standup please" | `@labops standup: today's bookings, low stock, pending approvals, expiring training` |
| "approval etiquette" | Each binding request requires its own PI decision. Use Allow once. LabQuorum does not offer batch approval. Session-wide provider permission never authorizes another lab request. |
| "test skeleton" | `Given ... When ... Then ...` |
| "failing test first" | "Write the failing test for this behavior first, run it, show me the red output, then implement the smallest change and rerun." |

## 5.4 The voice-and-mention trap

Wispr can add punctuation. A trailing period may become part of the Switch mention token, so a bare `@labops.` may not address `@labops` ([mention source](https://github.com/sandbox-quantum/switch/blob/main/core/switch_core/clients/mentions.py)). Silence is conditional: follow-ups or an assigned main agent can route unmentioned text ([room routing](https://docs.switchagents.ai/switch-rooms/using/work-in-a-room.md)).

1. After each room creation run and verify `!follow-ups off` and `!unassign-agent` where supported; record installed behavior. Test in a quiet group room with no assignment, follow-up or mention pill.
2. Mention first, inspect the paste, and use comma or colon; dictionary entries help spelling. Complete personalization and select Casual for the category actually detected for Mattermost, not a supposed "work messages" style ([styles](https://docs.wisprflow.ai/articles/2368263928-how-to-setup-flow-styles)).
3. EDGE-01/EDGE-02 and M-01: period yields 0 addressed events; comma and colon each yield 1. Recreate the room and repeat. Card-answer yes/no follows a separate request-answer path.
4. In 10 minutes test Windows Terminal, VS Code and Mattermost: dictate a handle, sample ID, decimal and unit; verify each paste, routing and observed category.

## 5.5 Roadmap: bench notes with read-back

This unscheduled path is not a shipped feature or demo claim. If later implemented and tested, a person could dictate: "at labops log plate 3, well C5, OD was 0.830, typo in the export". `@labops` calls `bench_log_draft`, which parses deterministically and returns:

```text
Draft OBS-014: PRJ egcg / plate 3 / C5 / OD590 = 0.830 (no unit expected)
Deviation: transcription error in export. Protocol: PRT-007 v3.
Confirm with: @labops confirm OBS-014 K7P2
```

Only `bench_log_confirm` with the matching, unexpired token writes the entry; a changed draft invalidates the token; corrections append, never overwrite; the original transcript is kept; `observed_at` and `confirmed_at` are separate. Numbers outside plausible ranges or missing required units get one clarifying question; dimensionless OD requires no unit. Honest framing: **voice-assisted, not hands-free** (Flow needs a focused text field and the send is deliberate); we cannot know a message came from Wispr, so there is no "voice-verified" label; we never process or store audio.

Prior voice ELN work includes [LabTablet](https://doi.org/10.1145/2948992.2948998); the proposed contribution is revision-bound capture and downstream correction in team chat, not voice logging itself. Run ten matched voice and typed notes with four critical fields each (40 checks per modality); report pre-confirmation and final errors, corrections and active time. Target zero uncorrected critical-field errors; one builder is only a usability probe.

## 5.6 Maximizing the scorecard legitimately

- Reserve 17:45-18:00 for final capture and bounded refresh/retry; stop at 18:00. Pass only when a complete, legible desktop Insights screenshot is saved and opens, and the actual form-supported attachment or link route is confirmed. If refresh fails, preserve the timestamped prior complete screenshot and disclose its capture time; do not imply it includes later usage. If the route remains unconfirmed, label the Wispr entry uncertain and submit the core on time. The 15-minute cap preserves the 18:00 capture and 18:30 attachment milestones.
- Capture baseline now and keep an earlier complete backup. After the last real authoring dictation, capture final desktop Insights by Saturday 18:00 IST; attach and verify by 18:30 for 19:00 submission. Keep full originals and comparable account/count context.
- [Insights](https://docs.wisprflow.ai/articles/8760230576-your-usage-tab-track-your-dictation-stats-in-wispr-flow) uses UTC days (05:30-05:29 IST); hover dates when useful. Wait until the final dictation appears; use documented retry controls for errors. Rankings are conditional, not guaranteed. Final minus baseline measures account usage in the window, not authenticated project-only work or productivity.
- No word target or filler. Log actual work and correction failures in `docs/voice-log.md`; link resulting artifacts. Categories are observed, not promised.
- During existing work capture three authentic 15-25 second clips: test-first coding prompt and result, agent/room instruction authoring, and README prose. Show Flow listening, text, deliberate send/save and resulting artifact; retain originals. Budget 0.5-0.75 hour total; coverage is 3/3 named build uses plus the required screenshot.

## 5.7 Showing voice in the video

Use one short authentic excerpt in the main video and link the full three-clip reel and unaltered scorecard from the README. Actual clips and artifact links are UNVERIFIED until captured: for each, log the prompt, resulting artifact path and time, then check that the clip shows listening, text, deliberate send/save and the resulting artifact. Roadmap bench dictation is not build evidence. Do not infer that generated code was dictated or promise a time saving without a measurement.
