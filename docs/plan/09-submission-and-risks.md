# 9. Submission, prizes, judging, risks

Back to the [master plan](README.md). Event facts are in [`../flip-the-switch-hackathon.md`](../flip-the-switch-hackathon.md).

## 9.1 Prize stacking

| Prize | Evidence we submit | Award signal | Priority |
| --- | --- | --- | --- |
| **Track 1: Best Business Workflow** | Real room workflow, human gate, completed outputs, reproducible repo, video | $2,000 cash (main page) | Highest |
| **Code with Wispr** | Voice used for prompts, agent instructions, docs and a voice-first product feature; Insights screenshot; voice log | $500 cash | High: nearly all effort compounds with the build |
| **Best Blog** | First-timer guide to Switch approvals with exact steps and screenshots | AirPods (count differs between pages) | High after the core works |
| **#HowISwitch** | Short honest clips and the final video | Keyboards or swag (pages differ) | Medium, low effort |
| Core Contribution | Skipped solo ([08](08-build-schedule.md#84-core-contribution-pr)) | $100/PR | Only with a teammate |

Named cash opportunity: $2,500 for Track 1 plus Wispr, conditional on winning and on legitimate stacking (the event allows Wispr alongside a track and a blog alongside a workflow; it does not guarantee every combination). We do not enter the second workflow track with the same build.

## 9.2 Submission (website Submit form)

Submission is through the **Submit button on the hackathon website**. Spike S8 records the exact fields on Wednesday night; prepare everything as files and links before Saturday:

- [ ] Public GitHub repo, logged-out accessible, MIT or Apache-2.0 license, no vendored Switch code (Switch's license includes a Commons Clause)
- [ ] README (outline below) naming every agent, provider, room and bridge and how Switch is used
- [ ] Demo video link (YouTube, public or unlisted, verified logged out) plus a copy as a GitHub release asset
- [ ] Wispr Insights screenshot (`docs/wispr-insights-final.png`), baseline screenshot kept
- [ ] Blog link and #HowISwitch post links
- [ ] Track selection: Best Business Workflow; side tracks Code with Wispr and Best Blog
- [ ] Clean-room reproduction done (M-03); CI green; `docs/test-evidence.md` current
- [ ] gitleaks clean; no em dash anywhere; no secrets or private URLs in video or screenshots
- [ ] Synthetic data, role-play and any replay labeled
- [ ] Submitted by Saturday 19:00 IST; confirmation screenshot saved; every link re-checked in incognito afterwards

## 9.3 README outline

1. One-line pitch and a 20-second GIF of the refused click and the PI's approval.
2. Demo video.
3. Why it needs Switch (the pull-the-plug table).
4. What it does: the lifecycle table with shipped / simulated / roadmap labels.
5. Agents and rooms: names, providers, addressing, tools per profile, what needs approval.
6. How Switch is used, feature by feature, with doc links.
7. Quickstart (Windows first; macOS/Linux notes): prerequisites, `uv sync`, `lq init`, `lq doctor`, import both templates, link accounts, first message, expected output per step.
8. Reproduce the demo: `lq seed --demo --anchor-date YYYY-MM-DD` and the exact messages.
9. Tests: how to run each layer; CI badge; local E2E gate and latest evidence.
10. Architecture: diagrams, data model, ADRs.
11. Safety and limits: what is enforced in code, what is policy only, honest threat model, synthetic data.
12. Troubleshooting: silence vs "not available" vs refusal; trailing period; unlinked account; Docker memory; OneDrive.
13. Built by voice: Wispr usage, screenshots, voice log.
14. Roadmap and license.

## 9.4 Blog (Best Blog: clarity for a first-time Switch user)

Title: "I built a lab where AI agents do the legwork and only the PI can say yes: a first-timer's guide to Switch approvals". Sections: what Switch is in three sentences; the Windows setup with the two gotchas that cost time (account linking, trailing period); the key idea that card authority follows addressing, with a diagram; giving an agent your own tools through `.mcp.json` and `ask` rules (copy-pasteable); what comes back (answer, unavailable, silence, refusal) with screenshots; testing agent workflows (deterministic core, contracts, Playwright against Mattermost); building by voice with Wispr (what worked, the mention trap, the dictionary fix); what I would do next. Every Switch claim links to the docs. Published on dev.to or Hashnode with a copy in `docs/blog.md`.

## 9.5 #HowISwitch

- Thursday night: a 20-30 s clip of the first real approval card and the refused student click.
- Saturday: the final video and blog link. Draft: "A student can ask our lab agents for anything. Only the PI's click makes it real, and Switch records who clicked. Built LabQuorum with Switch and Wispr Flow (synthetic demo data). Video: <link> Code: <link> #HowISwitch"

## 9.6 Judging scorecard self-assessment

| Criterion (weight) | What earns it | Main risk | Target |
| --- | --- | --- | --- |
| **Use of Switch (30%)** | Templates; addressing as the authorization model; approval cards with "Chosen by"; handoffs; roles, documents, aliases, attachments, threads; commands; pull-the-plug test | Fallback to message-based approvals if spikes fail (still Switch identity, less visual) | 9.3 -> 27.9 |
| **Technical execution (25%)** | 173 test IDs, race test on Windows and Linux, verifier golden set, real E2E against Switch, clean-room README, `lq doctor` | Reproduction needs Console and a provider login; real E2E is local | 8.6 -> 21.5 |
| **Creativity and impact (25%)** | Evidence-backed pain; governance-first stance; deterministic citation and retraction checks; stale cascade; voice bench notes | Lab software is a known category; the first 30 s must show the difference | 8.6 -> 21.5 |
| **Presentation (20%)** | Tight 3:50 script with three wow moments, README led by Switch usage, diagrams, blog | Two personas played by one person can look staged; mitigated by labels | 8.7 -> 17.4 |
| **Total** | | | **about 88/100** if everything ships; 78-82 for the reduced build |

Marginal effort follows the weights: one authentic Switch-dependent approval beats another literature API.

## 9.7 Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Windows Console or server path fails | Medium-high | Critical | S0 first; two paths; Linux host as last resort |
| Folder `.mcp.json` or `ask` rules ignored under Console (S2) | Medium | High | CLI variant, then steward fallback |
| Session allow leaks across requests (S3b) | Low-medium | Critical | Ask rules, gate hook, E2E-11; steward fallback |
| Unclaimed users cannot address agents (S1) | Medium | Medium | Switch users plus claims per persona |
| Five sessions exceed laptop capacity (S6) | Medium | Medium | Cut `@scribe`; cheap model in development |
| LLM variance while recording | High | Medium | Deterministic core, tight instructions, baseline video, segment retakes |
| OpenAlex new-account pacing or budgets | Medium | Medium | Key created Wednesday; cache; cassettes; labeled replay |
| Scope creep | High | High | Cut lines A-D; freeze Fri 23:00 |
| Solo fatigue | High | High | Scheduled sleep |
| Overclaiming (privacy, compliance, IRB, Wispr API) | Medium | High | Limits section in README; honest labels |
| Submit form surprises | Low-medium | High | S8 on Wednesday; submit five hours early |

## 9.8 Questions for the organizers (WeMakeDevs Discord, Wednesday)

1. The Submit form: does it take the Wispr screenshot and blog and social links, and is there a video length or host requirement?
2. Can one project be entered in Track 1 and also Code with Wispr, Best Blog and #HowISwitch?
3. Is a demo where one person plays two disclosed personas (two Mattermost accounts) acceptable?
4. Is labeled synthetic experimental data acceptable when the software workflow is real?
5. If scholarly API responses are replayed from a labeled cache in the video, is that acceptable?
6. Is the Windows early-access Console fine for the reproducibility criterion, or should the README also document macOS/Linux?
7. For Code with Wispr: which Insights view, and are lifetime totals with a baseline acceptable?
