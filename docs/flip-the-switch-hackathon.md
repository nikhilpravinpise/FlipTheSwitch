# Flip the Switch Hackathon briefing

Checked against the live event pages and GitHub on 4 Nov 2026. [main] [schedule] [DTA] [issues]

## Table of contents

- [TLDR](#tldr)
- [Key dates and deadlines](#key-dates-and-deadlines)
- [Eligibility, team, and registration](#eligibility-team-and-registration)
- [The challenge](#the-challenge)
- [Submission requirements](#submission-requirements)
- [Tracks and prizes](#tracks-and-prizes)
- [Judging](#judging)
- [Rules that bite](#rules-that-bite)
- [Core Contribution track](#core-contribution-track)
  - [Current open hackathon issues](#current-open-hackathon-issues)
- [Switch essentials](#switch-essentials)
- [Resources and perks](#resources-and-perks)
- [Conflicts, ambiguities, and unknowns](#conflicts-ambiguities-and-unknowns)
- [Winning strategy notes](#winning-strategy-notes)
- [Sources](#sources)

## TLDR

- Flip the Switch is an online WeMakeDevs x DevTools Academy x Switch hackathon running Nov 4-7, 2026. [main] [DTA]
- Build a real workflow where a person and at least one AI agent work together in a team chat through Switch. [main] [DTA]
- Teams may be solo or up to 4 people; registration requires a WeMakeDevs account. [main] [DTA]
- Hacking opened Nov 4 at 12:01 AM IST; submission cutoff is Nov 7 at 11:59 PM IST. [schedule]
- Switch must be central; the largest judging weights are use of Switch at 30%, then technical execution and creativity/impact at 25% each. [main]
- The main page advertises $10,000 total, including $2,000 for each workflow track, $100 x 20 for core PRs, and $500 for Code with Wispr. [main]
- Biggest gotchas: the live /submit page has no visible upload form despite its submit-project metadata; prize counts conflict; official age and IP terms conflict; and GitHub's core-issue instructions differ from later maintainer comments. [rules] [main] [DTA] [submit route] [WMD terms] [issues]

## Key dates and deadlines

All UTC conversions below use IST = UTC+5:30. UTC values are derived from the published IST times. [schedule] [DTA]

| Event | Published time | UTC | Notes |
| --- | --- | --- | --- |
| Registration | Open now; opening date and time not stated | Not stated | Add teammates any time before submissions close. [schedule] [DTA] |
| Kickoff live stream | Nov 2, 2026, 3:30 PM UK time; Nov 2, 9:00 PM IST | Nov 2, 3:30 PM | DTA lists the kickoff as 9:00 PM GMT+5:30. No other live session or workshop appears in the event schedule. [schedule] [DTA] |
| Hacking begins | Nov 4, 2026, 12:01 AM IST | Nov 3, 6:31 PM | Start building. [schedule] |
| Submissions close | Nov 7, 2026, 11:59 PM IST | Nov 7, 6:29 PM | Repo, demo video, and README are due by this cutoff. [schedule] [DTA] |
| Judging | Early November 2026; time not stated | Not derivable | WeMakeDevs shortlists, then the joint panel judges finalists. [schedule] [DTA] |
| Winners announced | To be announced; date and time not stated | Not derivable | Winning projects are to be showcased by the hosts. [schedule] [DTA] |

## Eligibility, team, and registration

- The official rules require entrants to be at least 18, or the age of majority where they live if higher. [rules]
- The event FAQ says anyone may participate; the DTA FAQ says 18 or older. The WeMakeDevs sign-up form and platform Terms allow under-18 platform use with parent or guardian consent. The event-specific official rules do not state that exception. See [Conflicts, ambiguities, and unknowns](#conflicts-ambiguities-and-unknowns). [main] [DTA] [rules] [WMD terms] [WMD sign-up]
- Participation is open from anywhere except jurisdictions and people excluded by sanctions, trade rules, or later Sponsor exclusions. The Sponsor may change eligible jurisdictions. The current list named in the rules includes Cuba, Iran, North Korea, Syria, and Crimea, Donetsk, Luhansk, Zaporizhzhia, and Kherson regions of Ukraine. [rules]
- Teams may be solo or up to 4 people. Add teammates before submissions close. [main] [schedule] [DTA]
- The event is free to enter; the Official Rules say no purchase is necessary. [DTA] [rules]
- Create or sign in to a WeMakeDevs account, then register for the event. Email sign-up requires verification before first sign-in; GitHub sign-up is also offered. [main] [WMD sign-up]
- Use one accurate, verifiable identity, with a valid email and legal name that match prize verification. Do not create multiple accounts or use aliases or temporary email addresses. [rules] [WMD terms]
- A public project repository is required. GitHub is the linked Switch source and issue host for the Core Contribution track. [DTA] [repo]
- An AI provider account, subscription, or API key is needed for the agent you use. An external chat account is needed if you do not use the local Mattermost instance. [DTA] [resources] [switch docs: quickstart]
- A Wispr Flow account is needed only for the Code with Wispr side track. The event link advertises 1 month of Flow Pro free. [main] [Wispr offer]
- Starring the Switch repo is optional for entry; the event page offers a chance to win a Keychron keyboard for starring it. [main]
- Core contributors need a GitHub account to comment on issues and open a pull request; the first pull request requires the repository's contributor agreement. [main] [CONTRIBUTING]

## The challenge

> "Add at least one AI agent to a team chat using Switch, and build a workflow where the agent and the people in that chat get a real task done together." [DTA]

- Switch is mandatory and should be central to the workflow. The README should explain how Switch is used. [main] [DTA]
- The minimum is one human, one AI agent, a team chat, and one real task with a concrete outcome. A chatbot or new model is not required. [main] [DTA]
- Named agent providers include Claude Code, Codex, Cursor, OpenCode, and Antigravity. Custom agents built with LangChain, Google ADK, OpenAI, or other frameworks may connect through the Switch agent protocol. [main] [DTA] [switch docs: providers] [switch docs: protocol]
- Named chat platforms are Slack, Microsoft Teams, Discord, Telegram, and Mattermost. The event materials mention all five; Switch Console includes local Mattermost. [main] [DTA] [resources] [switch docs: messaging]
- Existing agents, libraries, and templates are allowed. The Switch setup and workflow the agents run must be built during the hackathon. [DTA]
- AI coding tools are allowed. Entrants should understand the submission and be able to explain how it works. [DTA] [rules]
- Do not automate registration or entry submission. Bots, scripts, macros, bulk/programmatic entry, multiple accounts, collusion, and vote manipulation are prohibited. AI used to develop a genuine project is permitted. [rules]

## Submission requirements

Use this checklist for the project package. The exact upload or submission route remains unclear. [DTA] [schedule] [submit route]

- [ ] Public project repository. [DTA]
- [ ] README explaining which agents were connected, how the chat channel is set up, how Switch is used, and how to run the project. [DTA] [main]
- [ ] Short demo video showing the workflow running. Video length and hosting location are not stated. [DTA]
- [ ] If entering Best Blog, a published blog post about what you built, how it was set up, and what you learned. Best Blog may be entered on its own or alongside a track. [main] [DTA]
- [ ] If entering Code with Wispr, a screenshot of the Wispr Flow usage scorecard from Insights in the Wispr Flow desktop app. The project should use voice for prompts, agent instructions, and docs. [main]
- [ ] If entering the social prize, share the build publicly with #HowISwitch. The number and type of social prizes conflict between the event pages. [main] [DTA]
- [ ] For Core Contribution, open a pull request linked with `Closes #number`. [main] [DTA]
- [ ] Submit all package links before Nov 7, 2026, 11:59 PM IST. [schedule] [DTA]

**Submission route:** DTA says to submit the repo, video, and README. The current WeMakeDevs /submit page has a submit-project title and metadata, but the captured live page loads only a placeholder and footer; its HTML exposes no form or upload control. No working submission form or separate project URL was found. Ask the organizers for the actual submission link and how to attach the Wispr screenshot and optional blog link. [DTA] [schedule] [submit route]

## Tracks and prizes

| Track or prize | Advertised prize | Winner count | What is judged or required |
| --- | --- | --- | --- |
| Best Business Workflow | $2,000 cash. DTA page still says prize to be announced. [main] [DTA] | Not stated | Practical workflow using Switch to help people and agents get work done; open to technical and nontechnical builders. [main] |
| Best Personal or Creative Workflow | $2,000 cash. DTA page still says prize to be announced. [main] [DTA] | Not stated | Use Switch and agents for everyday tasks, personal projects, or creative ideas. [main] |
| Best Core Contribution | Main page: $100 x 20 PRs. DTA page: $100 each for the top 10 PRs. [main] [DTA] | 20 on main page; 10 on DTA page | Meaningful Switch core improvements, including capabilities, integrations, performance, reliability, or developer experience. [main] [DTA] |
| Best Blog | Main page: AirPods 5 for the best post. DTA page: AirPods 5 for each of the top 5 posts. [main] [DTA] | One best post on main page; 5 on DTA page | Explain what you built, setup, and lessons; DTA says judging includes clarity, accuracy, and usefulness to a first-time Switch user. [main] [DTA] |
| Code with Wispr | $500 cash. [main] | One best-project award by the page wording | Build the Switch project by voice with Wispr Flow; submit the required scorecard screenshot. [main] |
| #HowISwitch social prize | Main page: Logitech mechanical keyboard for each of the top 5 posts. DTA page: swag for the top 20 posts. [main] [DTA] | 5 keyboards on main page; 20 swag awards on DTA page | Share the build on social media with #HowISwitch. [main] [DTA] |
| Random project swag | 20 project submissions picked at random on main page. DTA instead describes swag for top 20 #HowISwitch posts. [main] [DTA] | 20 random projects on main page; not separately listed on DTA | Main page says random draw among project submissions. [main] |
| Participation certificate | A certificate for every project submission. [main] [DTA] | Every submission | No win required. [main] [DTA] |
| Switch repo star draw | Chance to win a Keychron keyboard. [main] | Not stated | Star the Switch repository. This is presented separately from the judged tracks. [main] |

The $10,000 prize pool is stated on the main and DTA event pages; the WeMakeDevs hackathon listing says $8,000. The main page's named cash adds to $6,500 if the 20 Core PR count applies: $2,000 + $2,000 + (20 x $100) + $500. If only 10 Core PRs receive $100, named cash totals $5,500. Non-cash item values and the remaining pool arithmetic are not stated. [main] [DTA] [WMD listing]

The main page says entrants may enter more than one track. Best Blog may be standalone or paired with a track, and Code with Wispr may be entered alongside any track. A single entrant's ability to claim every side prize is not stated. [main] [DTA]

## Judging

| Criterion | Weight | Published wording |
| --- | ---: | --- |
| Use of Switch | 30% | "Is Switch central, and would the project stop working without it?" [main] |
| Technical execution | 25% | "Does it run, and could someone clone the repo and reproduce it?" [main] |
| Creativity and impact | 25% | "Is it a fresh idea that solves a problem a real team has?" [main] |
| Presentation | 20% | "Do the demo video and README make clear how Switch is used?" [main] |

- WeMakeDevs reviews all submissions and creates the shortlist. Switch, DevTools Academy, and WeMakeDevs judge the finalists. [main] [DTA] [schedule]
- Core Contribution is described in judging as the 10 most useful, best-built pull requests. This conflicts with the main prize block's top 20. [main]
- Best Blog judging is clarity, accuracy, and how much it helps a first-time Switch user. [main] [DTA]
- The DTA wording expands Presentation to "Presentation and documentation" and says the README should explain what was built as well as Switch use. [DTA]
- No detailed scoring rubric, tie-breaker, or score publication process is stated. [main] [DTA] [rules]

## Rules that bite

| Do | Don't | Source |
| --- | --- | --- |
| Enter with an accurate identity and meet the official eligibility rule: "at least 18 years of age (or the age of majority in their jurisdiction of residence, whichever is greater)." [rules] | Do not rely on the WeMakeDevs sign-up consent checkbox as proof of hackathon eligibility; the event rule is stricter and the organizer has not clarified the conflict. [rules] [WMD terms] [WMD sign-up] |
| Use AI coding tools for a genuine project and be ready to explain your work. [DTA] [rules] | Do not use bots, scripts, macros, automated agents, or bulk/programmatic methods to register or submit an entry. Do not use multiple accounts or manipulate judging. [rules] |
| Keep ownership of your project and use third-party components within their licenses. The official rule says entrants retain ownership and grants Sponsor a "non-exclusive, worldwide, royalty-free, fully paid-up, sublicensable, irrevocable license" for event operation, evaluation, documentation, and promotion. [rules] | Do not include third-party confidential information, unlawful content, malicious code, or material that infringes another party's rights. [rules] |
| Keep behavior within the WeMakeDevs Code of Conduct and event rules. [WMD terms] [rules] | Do not plagiarize, misrepresent what was built during the event, harass, abuse, defraud, disrupt, or tamper with submissions or judging. [WMD terms] [rules] |
| If selected, complete identity checks and tax paperwork when requested. Winners are responsible for taxes, duties, and reporting. [rules] | Do not transfer a prize. A prize unclaimed within "thirty (30) days of notification" may be reassigned or not awarded. [rules] |
| For code contributions, read CONTRIBUTING.md and sign the one-time CLA on the first pull request. [main] [CONTRIBUTING] | Do not submit a typo-only, formatting-only, or unreviewed AI-generated PR; those are excluded from judging. [main] [DTA] |

The official rules permit the Sponsor to disqualify entries for rule breaches, false or misleading information, eligibility/sanctions/identity failures, automated entry, tampering, or unlawful, abusive, fraudulent, or disruptive conduct. Prize decisions are final. [rules]

## Core Contribution track

Published website process:

1. Choose an open GitHub issue labeled hackathon. [main] [DTA]
2. Comment with a short implementation plan and tag @petr-sandbox. [main]
3. Wait for assignment before coding; the website says one person per issue. Read CONTRIBUTING.md first; it describes setup and the one-time CLA on a first PR. [main] [DTA] [CONTRIBUTING]
4. Link the assigned issue in the PR description with `Closes #number`. [main] [DTA]
5. The PR must be open by Nov 7, 2026, 11:59 PM IST. The main page says work can start before the hackathon; DTA says the PR should be opened between Nov 4 and the cutoff. [main] [DTA] [schedule]

Published constraints: up to 5 open PRs per contributor on the main page; DTA says work on one issue at a time and ask for the next after the current PR is up. Spam may remove a participant from the track. An issue with no activity for 48 hours may be handed to someone else. PRs for unassigned issues and low-effort fixes will not be judged. [main] [DTA]

**Current GitHub comments differ:** maintainer comments say participants do not need assignment, multiple contributors may work on the same issue, PRs are reviewed after the event window, and only one PR is selected per issue. On Nov 4, the maintainer said a second strong implementation was welcome on issues with low competing PR counts. The current issue list shows 4-10 listed assignees on each issue, so an assignee list is not a reliable signal that an issue has no room for another PR. Ask the organizers which process controls. [issue #777] [issue #768] [issue #781] [issues]

### Current open hackathon issues

Checked with `gh issue list --repo sandbox-quantum/switch --state open --label hackathon --limit 100` on 4 Nov 2026. The live query returned 63 open issues, matching the count in the original scrape. The status column gives the current number of listed assignees; click the issue link for handles and the full discussion. A dash in the comment column means no choice-changing note is summarized here, not that the issue has no comments. [issues]

| Issue | One-line ask | Current labels | Assignee/status | Notable comment |
| --- | --- | --- | --- | --- |
| [#768](https://github.com/sandbox-quantum/switch/issues/768) Add DeepSeek Harness as an agent provider | Add DeepSeek Harness as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P0; area: agent-cli | Open; 6 listed assignees | Maintainer: only one PR selected per issue after the event window [issue #768](https://github.com/sandbox-quantum/switch/issues/768). |
| [#769](https://github.com/sandbox-quantum/switch/issues/769) Add email as a messaging platform | Bridge email messages into Switch rooms. | hackathon; difficulty: hard; priority: P1; area: messaging-platform | Open; 7 listed assignees | - |
| [#770](https://github.com/sandbox-quantum/switch/issues/770) Enable the Linear connector | Connect Linear data and supported actions to agents through Switch. | hackathon; difficulty: medium; priority: P1; area: connector | Open; 10 listed assignees | - |
| [#771](https://github.com/sandbox-quantum/switch/issues/771) Scheduled messages to agents in a room | Schedule one-off or repeating messages to one or more room agents. | hackathon; difficulty: hard; priority: P2; area: feature | Open; 7 listed assignees | - |
| [#774](https://github.com/sandbox-quantum/switch/issues/774) Add Mistral Vibe as an agent provider | Add Mistral Vibe as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P0; area: agent-cli | Open; 6 listed assignees | - |
| [#775](https://github.com/sandbox-quantum/switch/issues/775) Add Grok Build as an agent provider | Add Grok Build as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P0; area: agent-cli | Open; 6 listed assignees | - |
| [#776](https://github.com/sandbox-quantum/switch/issues/776) Add Kimi Code as an agent provider | Add Kimi Code as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P0; area: agent-cli | Open; 6 listed assignees | - |
| [#777](https://github.com/sandbox-quantum/switch/issues/777) Add Pi as an agent provider | Add Pi as a Switch Console provider for agent rooms. | hackathon; difficulty: hard; priority: P0; area: agent-cli | Open; 8 listed assignees | Maintainer: assignment is not required; several people may work on the same issue [issue #777](https://github.com/sandbox-quantum/switch/issues/777). |
| [#778](https://github.com/sandbox-quantum/switch/issues/778) Add GitHub Copilot CLI as an agent provider | Add GitHub Copilot CLI as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P1; area: agent-cli | Open; 5 listed assignees | - |
| [#779](https://github.com/sandbox-quantum/switch/issues/779) Add Kiro CLI as an agent provider | Add Kiro CLI as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P1; area: agent-cli | Open; 7 listed assignees | - |
| [#780](https://github.com/sandbox-quantum/switch/issues/780) Add Goose as an agent provider | Add Goose as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P1; area: agent-cli | Open; 5 listed assignees | - |
| [#781](https://github.com/sandbox-quantum/switch/issues/781) Add Amp as an agent provider | Add Amp as a Switch Console provider for agent rooms. | hackathon; difficulty: hard; priority: P1; area: agent-cli | Open; 6 listed assignees | Maintainer: #785, #787, #795, and #797 each had 1 competing PR; another strong implementation was welcome [issue #781](https://github.com/sandbox-quantum/switch/issues/781). |
| [#782](https://github.com/sandbox-quantum/switch/issues/782) Add Qwen Code as an agent provider | Add Qwen Code as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P1; area: agent-cli | Open; 6 listed assignees | - |
| [#783](https://github.com/sandbox-quantum/switch/issues/783) Add Factory Droid as an agent provider | Add Factory Droid as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P1; area: agent-cli | Open; 6 listed assignees | - |
| [#784](https://github.com/sandbox-quantum/switch/issues/784) Add Cline CLI as an agent provider | Add Cline CLI as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P1; area: agent-cli | Open; 5 listed assignees | - |
| [#785](https://github.com/sandbox-quantum/switch/issues/785) Add Auggie as an agent provider | Add Auggie as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P1; area: agent-cli | Open; 5 listed assignees | Maintainer noted 1 competing PR as of Nov 4 [issue #781](https://github.com/sandbox-quantum/switch/issues/781). |
| [#786](https://github.com/sandbox-quantum/switch/issues/786) Add OpenHands as an agent provider | Add OpenHands as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P1; area: agent-cli | Open; 8 listed assignees | - |
| [#787](https://github.com/sandbox-quantum/switch/issues/787) Add Junie as an agent provider | Add Junie as a Switch Console provider for agent rooms. | hackathon; difficulty: medium; priority: P1; area: agent-cli | Open; 5 listed assignees | Maintainer noted 1 competing PR as of Nov 4 [issue #781](https://github.com/sandbox-quantum/switch/issues/781). |
| [#789](https://github.com/sandbox-quantum/switch/issues/789) Add WhatsApp as a messaging platform | Bridge WhatsApp messages into Switch rooms. | hackathon; difficulty: hard; priority: P1; area: messaging-platform | Open; 6 listed assignees | - |
| [#790](https://github.com/sandbox-quantum/switch/issues/790) Add Google Chat as a messaging platform | Bridge Google Chat messages into Switch rooms. | hackathon; difficulty: hard; priority: P2; area: messaging-platform | Open; 5 listed assignees | - |
| [#791](https://github.com/sandbox-quantum/switch/issues/791) Add Zulip as a messaging platform | Bridge Zulip messages into Switch rooms. | hackathon; difficulty: hard; priority: P2; area: messaging-platform | Open; 6 listed assignees | - |
| [#792](https://github.com/sandbox-quantum/switch/issues/792) Add Signal as a messaging platform | Bridge Signal messages into Switch rooms. | hackathon; difficulty: hard; priority: P2; area: messaging-platform | Open; 4 listed assignees | - |
| [#793](https://github.com/sandbox-quantum/switch/issues/793) Add external Matrix as a messaging platform | Bridge external Matrix messages into Switch rooms. | hackathon; difficulty: hard; priority: P2; area: messaging-platform | Open; 6 listed assignees | - |
| [#794](https://github.com/sandbox-quantum/switch/issues/794) Add Rocket.Chat as a messaging platform | Bridge Rocket.Chat messages into Switch rooms. | hackathon; difficulty: hard; priority: P3; area: messaging-platform | Open; 6 listed assignees | - |
| [#795](https://github.com/sandbox-quantum/switch/issues/795) Add Webex as a messaging platform | Bridge Webex messages into Switch rooms. | hackathon; difficulty: hard; priority: P3; area: messaging-platform | Open; 5 listed assignees | Maintainer noted 1 competing PR as of Nov 4 [issue #781](https://github.com/sandbox-quantum/switch/issues/781). |
| [#796](https://github.com/sandbox-quantum/switch/issues/796) Add SMS (Twilio) as a messaging platform | Bridge SMS (Twilio) messages into Switch rooms. | hackathon; difficulty: hard; priority: P3; area: messaging-platform | Open; 4 listed assignees | - |
| [#797](https://github.com/sandbox-quantum/switch/issues/797) Add Lark / Feishu as a messaging platform | Bridge Lark / Feishu messages into Switch rooms. | hackathon; difficulty: hard; priority: P3; area: messaging-platform | Open; 5 listed assignees | Maintainer noted 1 competing PR as of Nov 4 [issue #781](https://github.com/sandbox-quantum/switch/issues/781). |
| [#798](https://github.com/sandbox-quantum/switch/issues/798) Add IRC as a messaging platform | Bridge IRC messages into Switch rooms. | hackathon; difficulty: medium; priority: P3; area: messaging-platform | Open; 7 listed assignees | Maintainer said #1058 was not accepted and #798 remained open; another implementation was welcome [issue #798](https://github.com/sandbox-quantum/switch/issues/798). |
| [#799](https://github.com/sandbox-quantum/switch/issues/799) Bring-your-own messaging app (generic webhook platform) | Add a generic webhook messaging adapter for apps without a native connector. | hackathon; difficulty: hard; priority: P2; area: messaging-platform | Open; 8 listed assignees | - |
| [#800](https://github.com/sandbox-quantum/switch/issues/800) Cancel a pending message before the agent picks it up | Cancel an agent message while it is still queued. | hackathon; difficulty: medium; priority: P1; area: feature | Open; 10 listed assignees | - |
| [#801](https://github.com/sandbox-quantum/switch/issues/801) Deliver messages sent mid-turn to the running agent (steering) | Steer a running agent by delivering a message during its turn. | hackathon; difficulty: medium; priority: P1; area: feature | Open; 9 listed assignees | - |
| [#802](https://github.com/sandbox-quantum/switch/issues/802) Show running subagents on the activity card | Show live subagents and their work in the activity card. | hackathon; difficulty: hard; priority: P2; area: feature | Open; 8 listed assignees | - |
| [#803](https://github.com/sandbox-quantum/switch/issues/803) Show tool input and output in the channel, safely | Expose tool inputs and outputs safely in chat. | hackathon; difficulty: medium; priority: P2; area: feature | Open; 9 listed assignees | - |
| [#804](https://github.com/sandbox-quantum/switch/issues/804) Handle edits to a message the agent hasn't picked up yet | Make a queued agent request use the latest edited message. | hackathon; difficulty: medium; priority: P2; area: feature | Open; 8 listed assignees | - |
| [#805](https://github.com/sandbox-quantum/switch/issues/805) Room invites should respect who can talk to an agent | Apply an agent addressing policy when people invite it into a room. | hackathon; difficulty: medium; priority: P1; area: feature | Open; 10 listed assignees | - |
| [#806](https://github.com/sandbox-quantum/switch/issues/806) Prettify the agent controller CLI output | Improve readability and consistency of agent-controller CLI output. | hackathon; difficulty: easy; priority: P2; area: feature | Open; 10 listed assignees | - |
| [#807](https://github.com/sandbox-quantum/switch/issues/807) Write the agent controller guide | Write an install, enrollment, operations, and troubleshooting guide for the agent controller. | hackathon; difficulty: easy; priority: P2; area: docs | Open; 9 listed assignees | - |
| [#808](https://github.com/sandbox-quantum/switch/issues/808) Five-minute quickstart for new contributors | Write a short clone-to-first-change setup guide for contributors. | hackathon; difficulty: easy; priority: P2; area: docs | Open; 8 listed assignees | - |
| [#816](https://github.com/sandbox-quantum/switch/issues/816) Add the GitLab connector | Connect GitLab data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P1; area: connector | Open; 10 listed assignees | Maintainer: 10 assignees is the GitHub maximum; assignment is not required [issue #816](https://github.com/sandbox-quantum/switch/issues/816). |
| [#818](https://github.com/sandbox-quantum/switch/issues/818) Add the Bitbucket connector | Connect Bitbucket data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P2; area: connector | Open; 6 listed assignees | - |
| [#819](https://github.com/sandbox-quantum/switch/issues/819) Add the Notion connector | Connect Notion data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P1; area: connector | Open; 10 listed assignees | - |
| [#820](https://github.com/sandbox-quantum/switch/issues/820) Add the Sentry connector | Connect Sentry data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P1; area: connector | Open; 10 listed assignees | - |
| [#821](https://github.com/sandbox-quantum/switch/issues/821) Add the Asana connector | Connect Asana data and supported actions to agents through Switch. | hackathon; difficulty: medium; priority: P2; area: connector | Open; 8 listed assignees | - |
| [#822](https://github.com/sandbox-quantum/switch/issues/822) Add the Microsoft 365 connector | Connect Microsoft 365 data and supported actions to agents through Switch. | hackathon; difficulty: hard; priority: P2; area: connector | Open; 10 listed assignees | - |
| [#823](https://github.com/sandbox-quantum/switch/issues/823) Add the New Relic connector | Connect New Relic data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P2; area: connector | Open; 9 listed assignees | - |
| [#825](https://github.com/sandbox-quantum/switch/issues/825) Add the PagerDuty connector | Connect PagerDuty data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P2; area: connector | Open; 9 listed assignees | - |
| [#826](https://github.com/sandbox-quantum/switch/issues/826) Add the Grafana connector | Connect Grafana data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P2; area: connector | Open; 9 listed assignees | - |
| [#827](https://github.com/sandbox-quantum/switch/issues/827) Add the Supabase connector | Connect Supabase data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P2; area: connector | Open; 9 listed assignees | - |
| [#828](https://github.com/sandbox-quantum/switch/issues/828) Add the Cloudflare connector | Connect Cloudflare data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P2; area: connector | Open; 7 listed assignees | - |
| [#829](https://github.com/sandbox-quantum/switch/issues/829) Add the Stripe connector | Connect Stripe data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P2; area: connector | Open; 6 listed assignees | - |
| [#830](https://github.com/sandbox-quantum/switch/issues/830) Add the HubSpot connector | Connect HubSpot data and supported actions to agents through Switch. | hackathon; difficulty: medium; priority: P2; area: connector | Open; 9 listed assignees | - |
| [#831](https://github.com/sandbox-quantum/switch/issues/831) Add the Azure DevOps connector | Connect Azure DevOps data and supported actions to agents through Switch. | hackathon; difficulty: medium; priority: P2; area: connector | Open; 8 listed assignees | - |
| [#832](https://github.com/sandbox-quantum/switch/issues/832) Add the Box connector | Connect Box data and supported actions to agents through Switch. | hackathon; difficulty: medium; priority: P3; area: connector | Open; 6 listed assignees | - |
| [#833](https://github.com/sandbox-quantum/switch/issues/833) Add the Canva connector | Connect Canva data and supported actions to agents through Switch. | hackathon; difficulty: medium; priority: P3; area: connector | Open; 7 listed assignees | - |
| [#834](https://github.com/sandbox-quantum/switch/issues/834) Add the Salesforce connector | Connect Salesforce data and supported actions to agents through Switch. | hackathon; difficulty: hard; priority: P3; area: connector | Open; 7 listed assignees | - |
| [#835](https://github.com/sandbox-quantum/switch/issues/835) Add the Monday.com connector | Connect Monday.com data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P3; area: connector | Open; 7 listed assignees | - |
| [#836](https://github.com/sandbox-quantum/switch/issues/836) Add the ClickUp connector | Connect ClickUp data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P3; area: connector | Open; 6 listed assignees | - |
| [#837](https://github.com/sandbox-quantum/switch/issues/837) Add the Trello connector | Connect Trello data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P3; area: connector | Open; 9 listed assignees | - |
| [#839](https://github.com/sandbox-quantum/switch/issues/839) Add the Dropbox connector | Connect Dropbox data and supported actions to agents through Switch. | hackathon; difficulty: medium; priority: P3; area: connector | Open; 10 listed assignees | - |
| [#840](https://github.com/sandbox-quantum/switch/issues/840) Add the Snowflake connector | Connect Snowflake data and supported actions to agents through Switch. | hackathon; difficulty: hard; priority: P3; area: connector | Open; 8 listed assignees | - |
| [#841](https://github.com/sandbox-quantum/switch/issues/841) Add the BigQuery connector | Connect BigQuery data and supported actions to agents through Switch. | hackathon; difficulty: medium; priority: P3; area: connector | Open; 9 listed assignees | - |
| [#842](https://github.com/sandbox-quantum/switch/issues/842) Add the Intercom connector | Connect Intercom data and supported actions to agents through Switch. | hackathon; difficulty: easy; priority: P3; area: connector | Open; 10 listed assignees | - |
| [#843](https://github.com/sandbox-quantum/switch/issues/843) Add the Zendesk connector | Connect Zendesk data and supported actions to agents through Switch. | hackathon; difficulty: hard; priority: P3; area: connector | Open; 8 listed assignees | - |

## Switch essentials

**What Switch does:** Switch connects AI agents to chat workspaces. A room is a chat channel with shared messages, instructions, roles, tasks, documents, and references for its people and agents. [main] [DTA] [switch docs: room] [switch docs: context]

Switch is open source and free to self-host. It includes no agent or model; participants bring a provider account, subscription, or API key. [DTA] [main] [switch docs: quickstart]

### Setup path

1. Install Switch Console. Current docs provide macOS Apple silicon and Intel builds, plus early-access Windows and Linux builds. [switch docs: install]
2. Install and start Docker, then run Switch locally. Console starts a local server in Docker and bundles Mattermost, so no company chat workspace is needed for a working demo. [DTA] [switch docs: quickstart]
3. Install and sign in to an agent provider. Console supports Claude Code, Codex, Cursor, OpenCode, and Antigravity. For a local setup, the quickstart shows these login commands:

       claude auth login
       codex login
       opencode auth login

   Cursor and Antigravity are listed as supported providers; use the setup instructions shown in Console for their sign-in steps. [switch docs: providers] [switch docs: quickstart]
4. In Console, add or run a Switch server, connect the chat platform to that workspace, and link your messaging account. [switch docs: quickstart] [switch docs: messaging]
5. Create a room or adopt an existing channel, add an onboarded agent, write room instructions, then address the agent by its exact @name. [switch docs: room] [switch docs: work]
6. Keep Console running during a demo if it runs the agent locally. Quitting Console stops local agent sessions; remote or managed hosts have separate uptime requirements. [switch docs: runtime]

The supported agent provider and messaging platform choices are separate. Connect one or more providers in Console, connect a supported chat app to the workspace, then put an agent in a room on that chat. The event and docs list Claude Code, Codex, Cursor, OpenCode, Antigravity and Slack, Microsoft Teams, Discord, Telegram, Mattermost; no provider-to-platform restrictions are listed. [main] [DTA] [switch docs: providers] [switch docs: messaging]

### Messaging app setup notes

| Chat app | Connection requirements and gotchas |
| --- | --- |
| Slack | Approval to install a custom app may be needed. Agent-name autocomplete requires a paid plan and permission for the bot to manage user groups. [switch docs: messaging] |
| Microsoft Teams | Needs Azure and Microsoft 365 administration plus a public HTTPS address. The Switch bot must be mentioned before commands unless channel subscriptions are configured. [switch docs: messaging] [switch docs: commands] |
| Discord | Need permission to add a bot and manage channels. [switch docs: messaging] |
| Telegram | No admin rights required, but turn off Group Privacy in BotFather before adding the bot. Create the Telegram group first; Switch does not create Telegram channels. [switch docs: messaging] |
| Mattermost | Switch Console starts and connects a local Mattermost server for you. For a separate Mattermost server, an admin account is needed. [switch docs: messaging] [switch docs: quickstart] |

Every app connection requires an admin and is made once per workspace on the server. A connected app's channels can become rooms. Every agent in that workspace can work in those rooms. [switch docs: messaging]

### Rooms, roles, and approvals

- Room instructions are shared with every agent that joins. Attach documents for room knowledge and references for resources such as a repository or issue tracker. [switch docs: room] [switch docs: context]
- Mention an agent as @agent-name to address it. A role such as @reviewer routes work to whichever agent holds that role; use !roles to see role holders. [switch docs: work] [switch docs: commands]
- When an agent requests permission, a person can choose Allow once, Allow for this session, or Decline. Switch records who approved or declined. By default, only the agent owner can respond; the owner can permit more people to talk to the agent. [switch docs: work]
- A room is shared context, not a guarantee that every person can command every agent. Agent owners control who can address their agents. [switch docs: work] [switch docs: payments]

### Useful room commands

Commands start with ! and must be the first character of a message. The ! form works across bridged apps. [switch docs: commands]

| Command | Use |
| --- | --- |
| `!help` | List Switch room commands. [switch docs: commands] |
| `!list-agents` | List agents in this room. [switch docs: commands] |
| `!agents-status` | See agent presence and capabilities. [switch docs: commands] |
| `!roles` | See room roles and their current holders. [switch docs: commands] |
| `!list-documents` and `!list-references` | See room materials. [switch docs: commands] |
| `!invite-agent @agent-name` | Add a registered agent to this room. [switch docs: commands] |
| `!interrupt @agent-name` | Stop the target agent's current work, if the provider supports it. [switch docs: commands] |
| `!compact @agent-name` | Compact the target agent's context, if supported. [switch docs: commands] |
| `!reset @agent-name` | Clear and reconnect the target agent, if supported. [switch docs: commands] |

Do not paste a command into a channel as an example unless you intend to run it. Teams may need the Switch bot mention before a command. Support for interrupt, compact, and reset depends on the agent provider. [switch docs: commands]

### Example agent template

The repository's triage-pair template creates a triager and a reproducer, then puts them and the creator in a named room. This abbreviated excerpt shows the basic shape; Console can load the full template from the repo. [main] [triage-pair]

    agents:
      - name: "{team}-triager"
        description: Reads reports, files and routes them
        addressing: anyone
        provider: "{provider}"
        instructions: |
          Restate the report.
          Classify it as a bug, a question, or a request.
          Route bugs to the reproducer by name.
      - name: "{team}-repro"
        description: Reproduces the reported problem
        addressing: owner-agents
        provider: "{provider}"
        instructions: |
          Write and run the smallest script that shows the problem.
          Report the exact output in the same thread.
    room:
      name: "{team}-triage"
      bridge: "{bridge}"
      agents: ["{team}-triager", "{team}-repro"]

### Limits and gotchas

- Switch does not include an AI agent or model. You bring a provider account, subscription, or API key. [main] [DTA] [switch docs: quickstart]
- If you run the provider locally, Console needs to stay open for the agent to answer. [switch docs: runtime]
- The event page's protocol blurb says "Server-sent events in, HTTP out." Current Switch docs say new clients use WebSocket for room events and HTTP calls for actions; older SSE clients are deprecated. Use the current protocol page for a new custom agent. [main] [switch docs: protocol]
- Names and mentions must match the agent name. A trailing period can cause the mention to address nobody. Without follow-ups enabled, an ordinary unmentioned message does not reach an agent. [switch docs: work]
- Microsoft Teams does not pass attached files through to agents; provide an accessible link instead. [switch docs: work]
- Windows and Linux Console builds are early access and may have release-specific rough edges. [switch docs: install] [DTA]

## Resources and perks

| Resource | Use or status |
| --- | --- |
| [Switch quickstart](https://docs.switchagents.ai/switch-rooms/getting-started) | One agent answering in a room in about 10 minutes. [resources] [switch docs: quickstart] |
| [Switch Console downloads](https://github.com/sandbox-quantum/switch/releases/latest) | Latest stable release links for macOS, Windows, and Linux. Windows and Linux are early access in current docs. [resources] [switch docs: install] |
| [Switch documentation](https://docs.switchagents.ai/) | Room setup, providers, chat bridges, agent protocol, and worked examples. [resources] |
| [Payments room example](https://docs.switchagents.ai/switch-rooms/building/payments-room) | Worked example from a channel to an operational room. [resources] [switch docs: payments] |
| [Triage-pair agent template](https://github.com/sandbox-quantum/switch/blob/main/examples/agent-templates/triage-pair.template.yaml) | Example of two agents collaborating in a room. [main] [triage-pair] |
| [Switch source and issues](https://github.com/sandbox-quantum/switch) | Repo, CONTRIBUTING.md, and the current hackathon issue pool. [resources] [repo] |
| [WMD Switch workflow article](https://www.wemakedevs.org/blogs/how-to-build-a-switch-workflow-that-finishes-a-real-task) | Hackathon-focused example and demo advice. [WMD blog] |
| [WeMakeDevs Discord](https://discord.gg/E2rWw2Yhsm) | Event page says support is open throughout the event; invite worked in the captured check. [main] [WMD Discord] |
| [Switch Discord](https://discord.gg/E6a2Jnb6G) | Linked from the DTA page, but its invite API returned expired in the captured check. Use the WeMakeDevs Discord link for support. [DTA] [DTA Discord invite check] |
| [Wispr Flow offer](https://wisprflow.ai/?promo_code=WEMAKEDEVS&utm_source=wemakedevs&utm_medium=partner&utm_campaign=wemakedevs&dub_id=1oU35MQWSE7nktLN) | 1 month of Flow Pro free through the event link. Billing, card, eligibility, and cancellation terms are not stated in the event materials. [main] [Wispr offer] |
| Star the Switch repository | Event page offers a chance to win a Keychron keyboard. [main] |

## Conflicts, ambiguities, and unknowns

| Topic | What the sources say | What to ask |
| --- | --- | --- |
| Prize pool and core PR count | Main and DTA pages say $10,000, WMD listing says $8,000. Main gives $100 x 20 Core PRs, while DTA says top 10 and judging says 10 useful PRs. Named cash is $6,500 on a 20-PR count, or $5,500 on a 10-PR count; non-cash valuations are absent. [main] [DTA] [WMD listing] | Is the Core Contribution award 10 or 20 PRs, and what items or cash make up the advertised total? |
| Blog, social, and swag awards | Main page gives AirPods 5 for the best blog, keyboards for the top 5 #HowISwitch posts, and random swag to 20 projects. DTA says AirPods 5 for the top 5 posts and swag for the top 20 #HowISwitch posts. [main] [DTA] | Which Best Blog count and #HowISwitch prize list controls? Is the random project swag still active? |
| Core issue allocation | Website says wait for assignment, one person per issue, up to 5 open PRs; DTA says one issue at a time. Maintainer comments say assignment is not required, several people may work on an issue, and only one PR is selected per issue. Live issues show multiple assignees. [main] [DTA] [issue #777] [issue #768] [issues] | Is assignment required? Does the 5 open PR limit still apply? May a contributor open PRs on several issues? |
| Submission route | DTA asks for repo, README, and demo video; schedule says submit before the cutoff; the current /submit page metadata describes project filing, but its captured live render exposes no form or upload control. [DTA] [schedule] [submit route] | Where should the package be submitted, and how should screenshot/blog links be attached? |
| Age requirement | Event-specific Rules require 18 or the higher local majority; WMD Terms and sign-up accept parent or guardian consent; DTA FAQ says 18+. [rules] [WMD terms] [WMD sign-up] [DTA] | Can a participant under 18 enter this specific event with guardian consent? |
| Submission IP license | Official Rules grant Sponsor a sublicensable, irrevocable license for event operation, judging, documentation, and promotion. WMD Terms grant a limited, non-exclusive license for judging, promotion, and showcasing. Entrant ownership is retained in both. [rules] [WMD terms] | Which license governs, and does the Sponsor's derivative-work permission apply beyond event promotion and evaluation? |
| Agent protocol wording | Event page describes SSE in and HTTP out. Current Switch docs say WebSocket events and HTTP actions, with older SSE deprecated. [main] [switch docs: protocol] | For custom agents, should entrants implement the current WebSocket protocol only? |
| Repository license metadata | GitHub metadata reports Other/NOASSERTION, while the LICENSE file includes a Commons Clause restriction alongside Apache 2.0 language. [repo metadata] [repo license] | Which license summary should contributors and project reuse rely on? |
| Platform and media details | Video length, upload host, per-track entry limit, tie-breaker, and exact winner announcement date are not stated. The schedule lists only the kickoff as a live session. [DTA] [schedule] | Confirm any additional submission formatting, track limits, workshops, or judging dates. |
| Wispr offer | The event link advertises 1 month free, but renewal billing, card, cancellation, and eligibility terms are not stated on the event page. [main] [Wispr offer] | What exact redemption and post-trial billing terms apply? |

## Winning strategy notes

These are suggestions, not event rules.

- **Inference:** Make Switch essential to the task. Demonstrate shared room context, explicit agent participation, and a real completion path because Use of Switch is 30% of the score. [main] [DTA] [switch docs: context]
- **Inference:** Pick one bounded workflow with a clear start, human decision, and visible output. A complete reproducible workflow can address the 25% technical execution and 25% creativity/impact criteria. [main]
- **Inference:** Show the room, the people, the agent, any approval request, and the completed work in the demo. Keep the README runnable and explain the agent and channel setup to support the presentation score. [main] [DTA] [switch docs: work]
- **Inference:** Stack a workflow entry with Core Contribution and Best Blog; the event allows multiple tracks, and Code with Wispr can be added alongside any track. Post #HowISwitch separately if it fits your build. [main] [DTA]
- **Inference:** For lower observed PR competition, the maintainer reported one competing PR each for #785 Auggie, #787 Junie, #795 Webex, and #797 Lark / Feishu as of Nov 4, 2026, 06:45 UTC, and said another strong implementation would help. This may have changed; check the issue before choosing. [issue #781]
- **Inference:** Treat the submission route as an early blocker. Ask in the working WeMakeDevs Discord before polishing the final package, then make the public repo, README, demo, optional blog link, and any Wispr screenshot easy to find. [main] [DTA] [submit route]
- **Inference:** Suggested sequence: Nov 4, prove one end-to-end task and lock the repo structure; Nov 5-6, harden the workflow and documentation; Nov 7, record the demo, confirm every link, and submit before 11:59 PM IST. The published cutoff is Nov 7, 2026, 11:59 PM IST. [schedule] [DTA]

## Sources

| Tag | URL | Used for |
| --- | --- | --- |
| [main] | https://www.wemakedevs.org/hackathons/switch | Challenge, FAQ, prizes, tracks, judging, registration |
| [rules] | https://www.wemakedevs.org/hackathons/switch/rules | Eligibility, identity, disqualification, IP, prize conditions |
| [schedule] | https://www.wemakedevs.org/hackathons/switch/schedule | Event timeline and deadlines |
| [resources] | https://www.wemakedevs.org/hackathons/switch/resources | Official setup resources and help |
| [DTA] | https://www.devtoolsacademy.com/hackathons/flip-the-switch | Challenge, deliverables, tracks, judging, schedule |
| [WMD listing] | https://www.wemakedevs.org/hackathons | Conflicting $8,000 total prize listing |
| [submit route] | https://www.wemakedevs.org/hackathons/switch/submit | Submit-project title and metadata, but no visible form in the captured live page |
| [WMD terms] | https://www.wemakedevs.org/terms | Account age, conduct, IP, no-cheating terms |
| [WMD sign-up] | https://www.wemakedevs.org/sign-up?next=%2Fhackathons%2Fswitch%3Fresume%3Dregister | Account registration fields and consent checkbox |
| [repo] | https://github.com/sandbox-quantum/switch | Switch source repository |
| [repo metadata] | https://api.github.com/repos/sandbox-quantum/switch | GitHub license metadata |
| [repo license] | https://github.com/sandbox-quantum/switch/blob/main/LICENSE | License file |
| [issues] | https://github.com/sandbox-quantum/switch/issues?q=is%3Aissue+state%3Aopen+label%3Ahackathon | Current open issue pool, checked with gh on 4 Nov 2026 |
| [CONTRIBUTING] | https://github.com/sandbox-quantum/switch/blob/main/CONTRIBUTING.md | Contributor setup and CLA |
| [triage-pair] | https://github.com/sandbox-quantum/switch/blob/main/examples/agent-templates/triage-pair.template.yaml | Example agent and room template |
| [WMD blog] | https://www.wemakedevs.org/blogs/how-to-build-a-switch-workflow-that-finishes-a-real-task | Hackathon-specific Switch workflow walkthrough |
| [Wispr offer] | https://wisprflow.ai/?promo_code=WEMAKEDEVS&utm_source=wemakedevs&utm_medium=partner&utm_campaign=wemakedevs&dub_id=1oU35MQWSE7nktLN | Event-linked trial offer |
| [WMD Discord] | https://discord.gg/E2rWw2Yhsm | WeMakeDevs event support channel |
| [DTA Discord invite check] | https://discord.com/api/v10/invites/E6a2Jnb6G?with_counts=true&with_expiration=true | Captured expired-invite status for DTA's Switch Discord |
| [switch docs: quickstart] | https://docs.switchagents.ai/switch-rooms/getting-started | Local setup path and agent login |
| [switch docs: install] | https://docs.switchagents.ai/switch-rooms/getting-started/install-switch-console | Console platforms and install notes |
| [switch docs: providers] | https://docs.switchagents.ai/switch-rooms/getting-started/set-up-agent-providers | Supported agent providers and sign-in |
| [switch docs: messaging] | https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/index | Supported chat apps and connection requirements |
| [switch docs: room] | https://docs.switchagents.ai/switch-rooms/getting-started/create-a-room | Create/adopt rooms and write instructions |
| [switch docs: work] | https://docs.switchagents.ai/switch-rooms/using/work-in-a-room | Addressing, roles, permissions, approvals |
| [switch docs: context] | https://docs.switchagents.ai/switch-rooms/using/shared-context | Room instructions, docs, references |
| [switch docs: commands] | https://docs.switchagents.ai/switch-rooms/resources/room-commands | Commands and command limits |
| [switch docs: protocol] | https://docs.switchagents.ai/switch-rooms/internals/agent-protocol | Current custom-agent transport |
| [switch docs: payments] | https://docs.switchagents.ai/switch-rooms/building/payments-room | Worked example |
| [switch docs: runtime] | https://docs.switchagents.ai/switch-rooms/getting-started/what-keeps-your-agent-running | Agent process availability |
