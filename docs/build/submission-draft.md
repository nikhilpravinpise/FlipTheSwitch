# Submission draft

Working copy for the human submitter. Replace placeholders and update claims against current gate evidence before pasting. Source for fields and video limit: `docs/submission-fields.md`.

## Part 1 - Project Details

**Project title:** LabQuorum

**Tracks:** Best Business Workflow; Code with Wispr consideration requires the usage card in Track Details.

**Project description:** Shared lab instruments need conflict checks and decisions that people can inspect. LabQuorum is a booking workflow for a student and PI working with agents in a Switch room. The intended flow has `@labops` propose a conflict-free alternative and `@pi-desk` present the exact decision to the PI. Binding approval is pending certification; if it is not certified, the demonstrated outcome is a proposal only. Lab records in the demo are synthetic. Sources: `docs/plan/README.md`, `docs/build/team-impact.md`.

**GitHub repository or contribution:** [PLACEHOLDER: public repository URL after release and review; planned repository `https://github.com/nikhilpravinpise/FlipTheSwitch`]

**Demo video:** [PLACEHOLDER: public or unlisted YouTube or Loom URL, duration strictly under 3:00]

**Live demo or deployment:** [Leave blank unless a real deployment is available; planned private deployment is pending.]

## Part 2 - Optional: Track Details

**Pull requests:** [Leave blank; no Core Contribution claimed.]

**Blog post:** [PLACEHOLDER: Darshan's published blog URL, if completed.]

**Your Wispr usage card:** [PLACEHOLDER: upload genuine Insights > Your usage > Share card, accepted format and at most 5 MB per image. Record whose usage it represents.]

**Your #HowISwitch post:** [PLACEHOLDER: actual public post URL if published; otherwise leave blank.]

## Part 3 - How you used Switch

**How did you use Switch in your project?**

Our intended room connects Codex agents `@labops` and `@pi-desk` through Switch to Mattermost. Darshan plays a student requesting a shared instrument; Nikhil plays the PI. `@labops` checks booking rules and proposes a slot, and the PI-owned `@pi-desk` is intended to route an exact decision for review. We require a certified identity and approval path before a binding booking; otherwise we show only an unapproved proposal. The smoke setup recorded a real Codex agent reply in Mattermost, but the complete two-person booking workflow and model rollout proof remain pending. Sources: `docs/build/adr/000-spikes.md`, `docs/build/PHASES.md`, `docs/build/team-impact.md`.

**What did you like about Switch, and what would you improve?**

Switch's room and agent addressing give the workflow a place for people and agents to hand work off; the Console RPC also allowed us to inspect and configure a real environment. We hit practical friction: Console inherited a Windows PATH without Docker's credential helper, and UI Admin navigation timed out. After refreshing PATH, Mattermost became healthy. We would improve discoverability and reliability of setup and navigation, and make approval card field visibility and fresh per-decision consent easier to verify. Our Codex elicitation experiment advertised support but returned cancel instead of reaching the app-server client, so we revised the design and still need to certify the alternative. Sources: `docs/build/adr/000-spikes.md`, `docs/build/codex-boundary.md`.

Team details: [PLACEHOLDER: enter each participant's actual details as requested by the live form; specific fields are not recorded in `docs/submission-fields.md`.]
