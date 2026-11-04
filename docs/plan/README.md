# LabQuorum: the master plan

> Agents do the legwork in the lab's chat. Only the PI's click makes it real.

Flip the Switch hackathon (WeMakeDevs x DevTools Academy x Switch), **Track 1: Best Business Workflow**, stacked with **Code with Wispr**, **Best Blog** and **#HowISwitch**.
Builder: Nikhil, solo, Windows 11, AI-assisted (Claude Code, Codex), voice-first with Wispr Flow.
Plan written 2026-11-04 (Wednesday) about 20:00 IST. **Hard cutoff: Saturday 2026-11-07 23:59 IST (18:29 UTC).** Target submission: Saturday 19:00 IST.

This plan merges two independent, deeply researched plans: one by Claude Opus 5.5 (high effort) and one by Codex `gpt-6.1-sol` (high effort). Both are kept unedited in [`../inputs/`](../inputs/README.md). Where they disagreed, the decision and its evidence are in [Decisions](#decisions-where-the-two-planners-disagreed) below. I checked the decisive facts against the Switch source code and the Claude Code docs myself; the evidence column says which ones.

## How to read this plan

| # | Document | What it answers |
| --- | --- | --- |
| 0 | This file | The pitch, the core mechanism, the decisions, the numbers that matter |
| 1 | [Problem, market and USP](01-problem-market-usp.md) | Is the pain real? Who else is there (35 products)? Why do we win? |
| 2 | [Product: people, agents, rooms, scope](02-product.md) | Personas, the 5 agents, rooms and roles, MVP vs polish vs stretch, how users get the most out of it |
| 3 | [Architecture and Switch centrality](03-architecture.md) | Components, the two-layer approval model, data model, MCP tool profiles, scholarly APIs, citation verifier, analysis sandbox, stale cascade, Windows, "pull the plug" |
| 4 | [End-to-end demo](04-demo.md) | The 3:50 video script, seed data, rehearsal, fallbacks |
| 5 | [Wispr Flow everywhere](05-wispr-flow.md) | Every place voice is used, the mention/punctuation trap, the scorecard plan |
| 6 | [Test strategy and test catalogue](06-testing.md) | Test-first workflow, about 190 test IDs written before code, real E2E against Switch and Mattermost, LLM evals, CI, flake policy |
| 7 | [Edge cases and failure modes](07-edge-cases.md) | 120 cases with detection, handling, what the user sees and the covering test |
| 8 | [Build schedule](08-build-schedule.md) | Day-1 spikes with go/no-go rules, hour-by-hour plan to Saturday, cut lines |
| 9 | [Submission, prizes, scorecard, risks](09-submission-and-risks.md) | README, video, blog, social, Core PR call, judging self-assessment, risks, organizer questions |
| T | [`templates/`](templates/) | Draft Switch templates (lab and project), agent folder settings, seed data |

Event facts (rules, prizes, judging, Switch essentials) are in [`../flip-the-switch-hackathon.md`](../flip-the-switch-hackathon.md).

## The pitch

Academic labs run on a dozen disconnected tools: an ELN nobody updates, a booking spreadsheet for the plate reader, an inventory sheet, Zotero, Overleaf, a WhatsApp group, and now private AI chats that invent citations. **LabQuorum turns the lab's team chat into the lab's operating room.** Five specialist agents live in Switch rooms next to the PI, students and research assistants:

| Agent | Job | Who can ask it | Can it make anything binding? |
| --- | --- | --- | --- |
| `@scout` | Literature search, library, deterministic citation and retraction checks | Anyone in the room | No |
| `@labops` | Instruments, training, inventory, protocols, hazards, bench log | Anyone | No, it can only propose |
| `@analyst` | Dataset intake, validation, vetted analysis recipes, figures, provenance | Anyone | No, and it has no shell |
| `@scribe` | Methods and results drafts from released protocols and recorded runs, verified citations only | Anyone | No |
| `@pi-desk` | The gate: checks policy, presents one decision, commits after the PI approves | Only the PI (and the PI's own agents) | Yes, but every commit raises a Switch approval card that only the PI can answer |

Anyone can ask an agent to do the legwork. Only the PI can make it binding: every change to shared lab state (booking a scarce instrument, ordering a reagent, releasing a protocol with a hazard, finalizing a results packet) becomes a **Switch approval card**, settled in front of the whole lab with "Chosen by prof-rao from Mattermost". Every citation is checked in code against Crossref, OpenAlex and Retraction Watch data before it can enter a draft. Every number in a draft points to a recorded analysis run, and when the underlying data changes, every figure and paragraph built on it turns **stale** until it is re-run and re-approved.

**The one sentence for judges:** *LabQuorum's agents have no screen of their own: the Switch room is where the lab asks, where each agent's addressing policy decides who it listens to, and where the PI's approval card is the only way a booking, order or protocol becomes real. Pull Switch out and you have five unconnected chatbots that nobody is allowed to approve.*

## The core mechanism in one picture

```mermaid
sequenceDiagram
  autonumber
  actor Maya as Maya (student)
  participant LO as @labops (anyone may ask, propose-only tools)
  participant L as Lab ledger (SQLite, invariants in code)
  participant PD as @pi-desk (only the PI may address)
  participant S as Switch (rooms, addressing, approval cards)
  actor PI as Prof. Rao (PI)
  Maya->>LO: "@labops, book the plate reader Thu 2-5 pm for PRT-007, one plate"
  LO->>L: check training, conflicts, stock, hazards
  L-->>LO: conflict 14:00-15:30 (Lena); crystal violet short
  LO->>L: propose_booking AR-0042 (15:45-18:45), propose_order AR-0043
  LO->>PD: hand off AR-0042 and AR-0043 (send_targeted_message)
  PD->>L: get_request + policy_check (bound to request revision and hash)
  PD->>S: calls commit_booking(AR-0042, rev 1, hash) - an "ask" rule
  S-->>Maya: approval card in the thread
  Maya--xS: clicks Allow once: refused (Maya may not address @pi-desk)
  PI->>S: clicks Allow once
  S-->>PD: approved, recorded "Chosen by prof-rao from Mattermost"
  PD->>L: commit (transaction re-checks conflict, revision, expiry)
  L-->>PD: committed, audit event hash-chained
```

Why this is safe by construction, not by prompt:

1. **Tools a student can reach cannot commit.** The commit tools are registered only in the `approver` MCP profile, which only `@pi-desk` loads. The other four agents' tool profiles do not contain them, their settings deny them, and contract tests assert both.
2. **Only the PI can answer the card.** In Switch, answering an approval card counts as talking to the agent, so it requires the same permission as addressing it. Verified in the Switch source: `core/switch_core/session_activity/bridge_answers.py` resolves the answer to a Switch identity and `service.py` `answer_approval` refuses anyone who "may not address the agent" ([bridge_answers.py](https://github.com/sandbox-quantum/switch/blob/main/core/switch_core/session_activity/bridge_answers.py), [service.py](https://github.com/sandbox-quantum/switch/blob/main/core/switch_core/session_activity/service.py)). `@pi-desk` admits only its owner (the PI) and the PI's agents.
3. **"Allow for this session" cannot turn into a blank cheque.** Commit tools sit under a Claude Code `ask` rule. Claude Code evaluates deny, then ask, then allow, and "a matching ask rule still prompts even when the hook returned allow or ask" ([Claude Code permissions](https://code.claude.com/docs/en/permissions)), so a session-scoped allow should not suppress the next card. This is spike **S3b**: the E2E test `E2E-11` approves AR-1 "for this session" and then requires AR-2 to raise a fresh card. If it does not, the fallback in [03-architecture.md](03-architecture.md#the-two-layer-approval-model) applies (PreToolUse hook that forces `ask`, or the deterministic steward).
4. **The approval is bound to exactly what was shown.** The commit tool takes the request id, its revision and its content hash. The ledger refuses the commit if the request changed, expired, or was already decided, so an approval can never carry over to a different booking.

## Decisions: where the two planners disagreed

| Topic | Opus 5.5 proposed | Codex gpt-6.1-sol proposed | Chosen | Why (evidence) |
| --- | --- | --- | --- | --- |
| Name | LabQuorum | BenchRelay | **LabQuorum** | "Quorum" is the product: agents prepare, the right humans must be present for a decision to count. BenchRelay kept as the backup name. Trademark and domain checks are a 5-minute Day-1 task (UNVERIFIED). |
| Deadline weekday | Friday (from my brief) | Saturday | **Saturday Nov 7** | Codex caught my brief's error: 2026-11-07 is a Saturday. The date and time (23:59 IST) were always correct. |
| How a human decision becomes binding | Native Switch approval card on `@pi-desk`, raised by Claude Code `ask` rules on MCP commit tools | A custom deterministic "steward" agent over the Switch agent protocol that reads the trusted sender id of a PI's chat message ("approve APR-001 revision 1") | **Opus mechanism as primary, Codex's invariants inside it, Codex's steward as the documented fallback** | The card is the most Switch-native, most visible approval there is ("Chosen by ... from Mattermost") and needs no custom protocol client. I verified in Switch source that card answers require addressing permission. Codex's insight that an approval must bind to an exact revision and hash is adopted in the ledger. The steward is the fallback if spike S2 or S3b fails. |
| "Allow for this session" | Called a "batch approval ritual" (handbook recommends Allow once) | Treated native consent and scientific approval as separate layers | **Must not weaken the guarantee; tested in E2E-11** | The advisor pass flagged it as a hole. Claude Code docs say ask rules prompt regardless of other allows; we prove it on Day 1 and keep a fallback. |
| Number of agents | 5 (scout, labops, analyst, scribe, pi-desk) | 3 (evidence, analysis, steward) | **5, with `@scribe` first to cut** | 5 gives one agent per permission boundary and a richer Switch story (roles, handoffs). Laptop RAM and token cost of 5 concurrent Claude Code sessions plus Docker Mattermost is measured in spike S6; if it does not fit, `@scribe` folds into `@scout`/`@analyst` (cut line A). |
| Analysis execution | Vetted recipes (MVP) plus agent-written scripts in a sealed Docker container (polish), no shell for `@analyst` | One fixed, reviewed analysis job in a locked-down Docker container; no generated code | **Recipes MVP, Docker `run_script` polish** | Both agree the analyst must not have a shell. Recipes are deterministic and golden-testable; `run_script` adds flexibility only if the container is solid on Windows (cut line B). |
| Demo scenario | EGCG vs E. coli biofilm, crystal violet assay, plate reader, retracted citation | Cup-sleeve cooling study, 6 paired runs, honest negative result, stale cascade | **EGCG biofilm story plus Codex's stale cascade** | A biology lab with a shared plate reader is the recognizable academic pain. The stale cascade (corrected CSV turns the figure and draft stale) is the strongest "consequence" moment and is kept. Data are synthetic and labeled. |
| Data honesty | Synthetic plate data, caption for replayed APIs | Explicit labels for synthetic data, PI role-play, replay mode | **Codex's honesty rules everywhere** | Judges reward trust. Every synthetic or replayed element is labeled on screen and in the README. |
| Switch template shape | Two templates: lab (agents + HQ room) and project (agent-typed params, re-runnable) | Single `room:` with top-level `kickoff:` | **Opus two-template shape** | The real `support-desk` template nests `kickoff:` inside each room and a template that creates agents refuses to re-run (`name_taken`), so a per-project template is needed for demo takes and E2E runs. Verified in spike S4. |
| Windows server path | "Run a server on this computer" (background processes, no Docker); Mattermost needs Docker | Docker-backed Console path; flagged Windows native PostgreSQL issue #1335 | **Decided by spike S0, both paths written down** | Both are plausible from the docs; issue [#1335](https://github.com/sandbox-quantum/switch/issues/1335) is a real risk on the native path. The first hour proves one path. |
| Wispr Flow API | No public API; enterprise API mentioned in press | Official remote MCP exists (read-only meeting data); no dictation API | **No dictation API. Remote MCP is a stretch idea only** | Codex cited Wispr's Nov 3 help article for the MCP. Neither is needed for the core; we never claim a Wispr API integration. |
| Wispr word target | About 30,000 words | 2,000-5,000 words | **No numeric target; dictate all real natural-language work** | A big number invites padding. Opus's catch stands: the free tier caps at 2,000 words a week, so the event's Pro offer is redeemed before the first dictation. |
| Scholarly APIs in MVP | OpenAlex, Crossref, S2, arXiv, PubMed, Unpaywall | OpenAlex and Crossref only | **OpenAlex + Crossref (with Retraction Watch via Crossref) in MVP; S2 and arXiv polish; PubMed, Unpaywall stretch** | Two clients cover search, DOI verification and retractions. Fewer clients means fewer cassettes and less rate-limit risk. |
| E2E test language | `pytest-playwright` (Python) | Playwright Test (TypeScript) | **`pytest-playwright`** | One toolchain (uv, pytest, pyright) for the whole repo; the E2E helpers call the ledger directly in Python. |
| Read-only web dossier | None (Switch is the only UI) | Small read-only Jinja dossier | **None in MVP; room documents are the dashboard** | Any second UI dilutes "would it stop working without Switch". Provenance is shown via room documents and attachments. |
| Core Contribution PR | Default skip | #807 agent-controller guide, max 4 h, only after everything is green | **Skip by default; #807 only if ahead at Friday 13:00** | Lowest expected value per hour for a solo builder. |
| Video length | 3:40 | 3:50 | **3:50 hard cap 4:00, with a named cut order** | Retraction catch, wrong-person refusal, PI approval and stale cascade all fit only with tight segments; cut order is in [04-demo.md](04-demo.md). |

## The numbers that matter

| Item | Value |
| --- | --- |
| Time left at plan completion | about 75 hours, about 45 focused working hours after sleep and meals |
| Agents | 5 Switch agents (4 MVP-critical), on Claude Code; `@analyst` optionally on Codex |
| Rooms | `#rao-lab-hq` (operations), one `#rao-proj-<slug>` per project; `#bench` Telegram room as polish |
| Tests written before code | about 190 test IDs (unit, property, contract, integration, live evals, real E2E) |
| Edge cases catalogued | 120, each mapped to a test or a rehearsal step |
| Day-1 spikes | 9 time-boxed spikes with go/no-go rules, Wednesday night and Thursday morning |
| Video | 3:50, two "wow" moments (retracted citation caught; student cannot approve her own booking) plus the stale cascade |
| Self-assessed score | about 87/100 if everything ships; 78-82 for the reduced build (see [09](09-submission-and-risks.md#judging-scorecard-self-assessment)) |

## The first three actions (tonight)

1. **Redeem the Wispr Flow event Pro offer before dictating a single word**, take the baseline Insights screenshot, load the dictionary and snippets ([05](05-wispr-flow.md)).
2. **Ask the organizers the submission-route questions** in the WeMakeDevs Discord ([09](09-submission-and-risks.md#questions-for-the-organizers)).
3. **Run spikes S0 to S4** ([08](08-build-schedule.md#day-1-spikes-with-go-no-go-rules)): a real agent answering in Mattermost, a second user, an `ask`-gated MCP tool raising a Switch card, a non-PI click being refused, and "Allow for this session" not leaking to the next request. Nothing else matters until those are green or their fallbacks are chosen.
