# 5. Wispr Flow everywhere

Back to the [master plan](README.md). Goal: win **Code with Wispr** ($500) honestly while making voice a real product feature, not decoration. Event requirement: build by voice (prompts, agent instructions, docs) and submit a screenshot of the Wispr Flow usage scorecard from **Insights** in the desktop app ([event page](https://www.wemakedevs.org/hackathons/switch)).

**Status (Wed 22:20 IST): the event's Flow Pro offer is redeemed.** That removes the free tier's 2,000 words/week cap ([free tier](https://docs.wisprflow.ai/articles/4760791189)) and unlocks Command Mode.

## 5.1 What Wispr Flow actually is (verified)

| Capability | What it does | Source | Boundary |
| --- | --- | --- | --- |
| Flow dictation | System-wide dictation into any text field; Windows default push-to-talk **Ctrl+Win** | [IDE guide](https://docs.wisprflow.ai/articles/6434410694-use-flow-with-cursor-vs-code-and-other-ides), [terminal guide](https://docs.wisprflow.ai/articles/6478598909-using-flow-with-linux-wsl-and-terminal-applications) | Text entry, not an audio SDK; review before sending |
| IDE and terminal support | Variable recognition in VS Code, Cursor, Windsurf (VS Code needs Screen Reader Optimized mode); file tagging in Cursor/Windsurf chat; on Windows pastes with Shift+Insert in IDEs; terminals get no variable formatting | [IDE guide](https://docs.wisprflow.ai/articles/6434410694-use-flow-with-cursor-vs-code-and-other-ides), [variable recognition](https://docs.wisprflow.ai/articles/8554805225-variable-recognition) | Dictate prose prompts, not shell syntax |
| Command Mode | Select text, hold the Command Mode shortcut (Windows default Ctrl+Win+Alt), speak an edit; enable in Settings > Experimental; Pro | [Command Mode](https://docs.wisprflow.ai/articles/4816967992-how-to-use-command-mode) | Never use it on data values, DOIs, paths, commands or quoted evidence |
| Dictionary | Custom words and spoken-to-written replacements | [dictionary](https://docs.wisprflow.ai/articles/9639977157-view-shared-dictionary-words-and-snippets-in-the-admin-portal) | Corrects vocabulary, does not validate a number |
| Snippets | A spoken cue expands to saved text | [snippets](https://docs.wisprflow.ai/articles/5784437944-create-and-use-snippets) | Text only; never an "approve" snippet |
| Styles | Formatting per context (formal, casual, very casual, excited; terminals and AI tools use Other) | [styles](https://docs.wisprflow.ai/articles/2368263928-how-to-setup-flow-styles) | Formal punctuation can put a period after a mention (see 5.4) |
| Insights > Your usage | Desktop only (Mac, Windows): words per minute (with Top X%), fixes made by Flow, total words (lifetime, desktop + mobile), desktop usage by category (personal messages, work messages, emails, AI prompts, documents, other) with Power/Moderate/Light, distinct apps, daily heatmap with current and longest streak | [usage tab](https://docs.wisprflow.ai/articles/8760230576-your-usage-tab-track-your-dictation-stats-in-wispr-flow) | Lifetime totals include pre-hackathon use; it does not prove productivity |
| Mobile keyboard | Flow on iOS and Android; mobile words count toward totals and the heatmap | same | For Telegram `#bench` (polish) |
| Privacy Mode, HIPAA BAA | Zero data retention mode; BAA path for healthcare | [HIPAA](https://docs.wisprflow.ai/articles/4218718535-HIPAA-Compliance-&-Healthcare-Use) | README guidance for labs with sensitive data |
| Remote MCP | OAuth endpoint `https://api.wisprflow.ai/connect/mcp`, read-only meeting/context data ([guide, Nov 3](https://docs.wisprflow.ai/articles/9551372685-connect-an-mcp-client-to-wispr-flow-remote-mcp-server), [plugin repo](https://github.com/Wispr-AI/wispr-flow-plugin)) | | Not dictation, no dictation history. **Stretch only** |
| Dictation API / SDK | None public | | **We never claim a Wispr API integration** |

## 5.2 Every place voice is used

| Where | What is dictated | Feature | Insights category |
| --- | --- | --- | --- |
| Claude Code and Codex prompts (Windows Terminal, VS Code) | Every implementation prompt: "write failing tests for the booking conflict rules first...", bug reproductions, review requests | Flow; variable recognition in VS Code | AI prompts |
| Test design | Given/When/Then for every E2E and the edge-case catalogue | Flow, then Command Mode "turn this into Given When Then" | Documents |
| Agent instructions and room briefs | The five agents' instructions, `Lab handbook`, project charters in the templates | Flow + Command Mode tightening | Documents |
| Room messages to agents | Every message to `@scout`, `@labops`, `@analyst`, `@scribe`, `@pi-desk` in build, tests and the demo | Flow; dictionary for handles | Work messages |
| Bench logging (product feature) | Observations with sample, time, value, unit, deviation | Flow desktop in Mattermost; mobile keyboard in Telegram (polish) | Work messages / mobile |
| ADRs, spike results, decisions log | `docs/adr/*.md` | Flow | Documents |
| README narrative, blog, video script, voice log | All prose (commands are pasted, not dictated) | Flow + Command Mode | Documents |
| Commit messages, PR and issue text | Every commit body (dictate in the editor `git commit` opens) | Flow | Other / documents |
| Organizer questions, #HowISwitch posts | Discord and social posts | Flow, work style | Work messages |

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
| "approval etiquette" | The handbook paragraph on Allow once vs Allow for this session |
| "test skeleton" | `Given ... When ... Then ...` |
| "failing test first" | "Write the failing test for this behavior first, run it, show me the red output, then implement the smallest change and rerun." |

## 5.4 The voice-and-mention trap

Wispr adds punctuation. "book it at labops" can become "Book it @labops." and Switch reads `@labops.` as a different name: **nothing happens and nothing warns you** ([mention and message](https://github.com/sandbox-quantum/switch/blob/main/docs/official/using/mention-and-message.md)). Mitigations:

1. **Mention first**, always ("at labops comma ..."). A comma or colon after a mention still routes.
2. Dictionary entries make the spelling exact.
3. Agent names avoid characters Wispr mangles (only `pi-desk` has a hyphen).
4. Use the "work messages" style in Mattermost and check it does not add a trailing period after a lone mention.
5. Tests EDGE-01 and EDGE-02 ([06](06-testing.md)) pin the platform behavior.

## 5.5 Voice-first product feature: bench notes with read-back

At the bench, a person dictates: "at labops log plate 3, well C5, OD was 0.830, typo in the export". `@labops` calls `bench_log_draft`, which parses deterministically and returns:

```text
Draft OBS-014: PRJ egcg / plate 3 / C5 / OD590 = 0.830 (no unit expected)
Deviation: transcription error in export. Protocol: PRT-007 v3.
Confirm with: @labops confirm OBS-014 K7P2
```

Only `bench_log_confirm` with the matching, unexpired token writes the entry; a changed draft invalidates the token; corrections append, never overwrite; the original transcript is kept; `observed_at` and `confirmed_at` are separate. Numbers outside plausible ranges or without units get one clarifying question. Honest framing: **voice-assisted, not hands-free** (Flow needs a focused text field and the send is deliberate); we cannot know a message came from Wispr, so there is no "voice-verified" label; we never process or store audio.

## 5.6 Maximizing the scorecard legitimately

- Baseline Insights screenshot now (tonight), final screenshot Saturday about 20:00 IST after the last README and blog edits; keep both originals; label lifetime vs hackathon context in the README.
- Dictate every day Nov 4-7 so the heatmap shows the streak.
- No numeric word target. Dictate **all** real natural-language work (prompts are the bulk); never filler, loops or replayed audio. Judges can compare the scorecard with the commit history.
- Spread naturally across AI prompts, documents and work messages.
- Keep `docs/voice-log.md`: one dictated line per day of what was built by voice, plus failures (the mention trap) and fixes.
- Record a 20-second clip of dictating a test-first prompt into Claude Code for the blog and #HowISwitch.

## 5.7 Showing voice in the video

The Wispr indicator stays visible on every dictated message; the first two get a "dictated with Wispr Flow" caption; the bench-note correction in wow 3 is dictated; the end card shows the Insights screenshot for 2 seconds.
