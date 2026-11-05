# Submission text

## Project title

LabQuorum

## Tracks

Best Business Workflow; Code with Wispr

## Project description

Shared instruments are scarce, and lab members need to know whether a time is free before making plans around it. LabQuorum is a booking workflow for lab members and principal investigators working together in a team chat. A student asks the LabOps agent for an instrument and time; it checks availability, identifies a conflict and proposes an alternative for review. The PI desk is designed to present the exact booking decision through a native approval card, with access restricted to its owner. The workflow keeps proposed requests distinct from committed bookings and records actions in an audit trail. Switch connects the people and agents in a Mattermost room, so the request and its context stay in the conversation. In a live smoke test, LabOps named an existing booking and proposed a later slot; the request remained pending. The end-to-end approval and binding booking are pending certification, and later live retests did not produce the expected chat reply. Demo lab records are synthetic.

## GitHub repository URL

https://github.com/nikhilpravinpise/FlipTheSwitch

## Demo video

<YouTube unlisted link>

The video must be strictly under 3:00 and show the real chat workflow.

## Live demo

Leave blank: the Switch Console deployment is local, not a public instance.

## Blog post

<Darshan's blog URL>

Pull requests: leave blank; we are not entering Best Core Contribution.

## Wispr usage card

Upload both cards exported at the end from Wispr Flow: Insights > Your usage > Share.

## #HowISwitch post

<#HowISwitch post URL>

## How did you use Switch in your project?

We connected Codex gpt-6-luna agents `@labops` and `@pi-desk` in Switch Console to a Mattermost room bridged by Switch. Our team reaches the local Mattermost deployment over Tailscale. A student asks `@labops` to book a shared instrument; LabOps checks conflicts and proposes a slot. The intended next step is for the PI to review and approve the exact decision using a native card through the owner-only PI desk. Switch refused Darshan when he tried to address that desk as a non-owner.

In the live AR-0042 smoke, LabOps named Lena's 14:00-15:30 booking and proposed 15:45-16:45; the request stayed pending and the booking proposed. Darshan's real chat run exposed unnecessary read-tool approval prompts, a requester fixed to Maya, and card answers misread as training claims. Fixes were merged, but Darshan's own retest is pending. Later synthetic-user retests created pending proposals but did not deliver the expected reply in the allotted time. In an isolated certify session, Switch's journal recorded native `commit_booking` approval requests with decision fields and Approve, Decline and Cancel options; they were interrupted. Rendered card visibility, a PI decision and a binding end-to-end booking remain pending certification, so binding remains off. Evidence: `docs/build/p3-agents.md`, [issue #8](https://github.com/nikhilpravinpise/FlipTheSwitch/issues/8), and the commit approval diagnostic.

## What did you like about Switch, and what would you improve?

Rooms, agent addressing and identity claims gave our team a practical way to bring people and agents together. The owner-only refusal worked in Darshan's live run, and the session journal showed native approval requests with the booking decision and choices. We still need to verify the rendered card and a fresh human decision before enabling binding.

We would improve the Console template-run timeout relative to agent startup; the reported 30-second limit remains UNVERIFIED in the available evidence. We would also make it clearer that hosted agents need to use `post_message` for a chat reply: final assistant text is not shown to participants. A later test produced an activity summary and a pending proposal without the requested answer; the exact cause is unverified. Approval choices can persist for a session, so we need clearer per-decision consent controls. In our Codex 0.166.0 spike, server-initiated MCP elicitation was not forwarded to the app-server client and returned cancel. We also had to understand global versus per-session agent Codex homes and repair the inherited Windows PATH on first launch so Docker's credential helper could be found. Clearer setup diagnostics and configuration visibility would help.
