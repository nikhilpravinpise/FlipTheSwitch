# Switch v0.40.1 facts for LabQuorum

## Scope and confidence

Primary source: Switch checkout at C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\ref\switch-v0.40.1, tag switch-console-v0.40.1, commit 6ab2ff463ad9518920ba2a15b182b1d2e760fd9f. Local citations are paths relative to that checkout. VERIFIED means read in that tag or official docs; UNVERIFIED means not established by those sources. No Switch or LabQuorum source files were edited.

Plan context read: docs/plan/03-architecture.md sections 3.1-3.2, docs/plan/02-product.md section 2.2, and docs/plan/templates/labquorum-core.template.yaml. The plan expects agent-folder settings and MCP config to apply, a fresh PI decision for each gated call, and a failure-blocking PreToolUse hook.

## 1. Claude adapter

**Launch. VERIFIED.** The adapter imports the Claude Agent SDK query(), builds its Options, and invokes queryFn({prompt, options}); it does not build a literal CLI argument list. It passes cwd: input.cwd, env: input.env, permission mode, MCP config, and canUseTool. On Windows the custom spawn receives the SDK-provided command, args, cwd, env, and piped stdio. The Windows path exists because npm Claude installs claude.cmd, which the SDK cannot start directly. See console/packages/agent-providers/src/claude/claude-adapter.ts:325-342,463-530.

Executable lookup: configured executable first; on Windows claude on PATH, then %USERPROFILE%\.local\bin\claude.exe; otherwise the SDK bundled CLI fallback. See claude-adapter.ts:296-323,475-477. SDK package is ^0.3.260 and lockfile version 0.3.260: console/packages/agent-providers/package.json:38, console/pnpm-lock.yaml:5836.

**Settings sources. VERIFIED.** Adapter does not set settingSources; tests assert the option is undefined (claude-adapter.test.ts:128-135,224,978-981). The official SDK reference says: "When settingSources is omitted or undefined, query() loads the same filesystem settings as the Claude Code CLI: user, project, and local." [SDK reference](https://code.claude.com/docs/en/agent-sdk/typescript). Since Switch passes the agent directory as cwd, .claude/settings.json from the session's primary working directory is the relevant project file; an agent-folder file applies when that folder is the session cwd. Local source is enabled too, but its settings.local.json path is platform/version-dependent: current Settings docs note that on Windows it may stay beside shared project settings rather than in a subdirectory. The tag does not pass projectConfigRoot. See https://code.claude.com/docs/en/settings.

**MCP sources. VERIFIED.** Adapter sets strictMcpConfig: false and passes host mcpServers (claude-adapter.ts:488-493,516-518). Strict config is the SDK option that restricts the session to passed MCP servers and ignores project .mcp.json; false does not isolate the session. Official MCP docs say that project .mcp.json is rooted at the project and "it loads project-scoped servers without asking" in Agent SDK sessions: [MCP docs](https://code.claude.com/docs/en/mcp). Thus project .mcp.json is loaded by default when located at the SDK session project root. Whether a nested agents/<name>/.mcp.json is recognized as that root by the pinned CLI is UNVERIFIED: adapter supplies cwd but does not set projectConfigRoot, and current MCP docs specify project-root scope. Test the nested layout with the installed CLI. Settings-file hooks are likewise read; the adapter itself passes no hooks option.

**Host MCP allow behavior. VERIFIED.** For each MCP server Switch registers, the adapter adds a permission allow entry mcp__<name> and auto-allows matching mcp__<server>__ prefixes inside canUseTool. User/project-configured MCP servers not registered through this host input do not get this special allow. See claude-adapter.ts:358-360,391-403,471-493,1124-1142. Switch's own loopback host MCP server is named switch (console/packages/switch-agent-runtime/src/hosted.ts:108-116).

**Permission modes. VERIFIED.** Runtime mapping is approval-required -> default, auto-accept-edits -> acceptEdits, auto -> auto, full-access -> bypassPermissions (claude-mapping.ts:25-30). Console resolves autoApprove first to full-access, else autoMode to auto, else approval-required (console/packages/agent-providers/src/adapter.ts:36-41). Thus auto_mode:false and auto_approve:false select Claude default mode. Full-access also sets allowDangerouslySkipPermissions:true (claude-adapter.ts:491-495).

## 2. canUseTool, approval cards, session grants

**Flow. VERIFIED.** Claude SDK invokes adapter canUseTool(toolName, toolInput, options). Adapter denies a missing session, specially handles AskUserQuestion, auto-allows full-access and host-registered MCP prefixes, then sends other permission requests to requestApproval (claude-adapter.ts:1124-1142). It emits request.opened with tool name, input, title/detail and choices (claude-adapter.ts:1189-1243). SessionHost turns that into a Switch Request and publishes it (console/packages/agent-providers/src/host/session-host.ts:1136-1179); Switch routes activity through core/switch_core/bridges/agent/api/activity_routes.py:232-260 and core/switch_core/session_activity/publisher.py:537-622. A platform button or typed answer is handled by core/switch_core/session_activity/bridge_answers.py:88-153,177-219, then checked by session_activity/service.py:452-503,571-620.

**Choices and results. VERIFIED.** Buttons are Allow once, Allow for this session, and Decline (claude-adapter.ts:117-121). Allow once resolves the current callback with behavior: allow. Allow for this session returns allow plus SDK updatedPermissions, with each provider suggestion rewritten to destination: session. Decline resolves deny, with message "The user declined this request. Do not retry it another way." See claude-adapter.ts:369-372,1204-1228.

For an MCP call, card title is "<server> wants to run <tool>" and detail is compact JSON of the complete tool input, including string arguments. Empty input has no detail. Detail is capped at 1,000 characters, then gets an omitted-character count (console/packages/agent-providers/src/mcp-approval.ts:1-28). A gated LabQuorum card therefore shows its request arguments, subject to that cap.

**Who can answer. VERIFIED.** The bridge must resolve the platform sender to a Switch identity, and the service checks whether that identity may address the agent in the request room. A claimed platform identity is needed for owner-scoped approval. See bridge_answers.py:177-219, session_activity/service.py:452-503,571-620, and core/switch_core/addressing.py:100-150,169-198. Room membership alone does not make a human an eligible approver.

**Unanswered request. VERIFIED.** SessionHost sets expiresAt:null on this adapter path (session-host.ts:1138-1144). The callback waits for an answer or abort and has no local timer (claude-adapter.ts:1204-1232). Switch accepts optional expiry and limits a supplied expiry to 24 hours (session_activity/service.py:70-72,359-387); this adapter supplies none. Therefore there is no fixed Switch card timeout here. The tool call stays pending until answered or the session/turn is cancelled or closed. Hook timeout is a separate mechanism.

**Session scope. VERIFIED with CLI-supplied scope caveat.** Allow for this session is not inherently a one-call grant. Switch takes the SDK permission suggestions and changes only their destination to session (claude-adapter.ts:369-372,1213-1218). A test for MCP tool mcp__atlassian__search shows a suggestion containing the tool name and session destination, without an input constraint (claude-adapter.test.ts:876-906,1317-1355). The SDK docs describe suggestions as updates so "the user is not prompted again for this tool": [SDK reference](https://code.claude.com/docs/en/agent-sdk/typescript). In that observed example, scope is every call to that tool in the Claude session, regardless of payload, not a Switch user setting or single argument value. Exact suggestion for a future mcp__labquorum__commit_booking call is UNVERIFIED.

A matching Claude ask rule is checked before allow rules, and SDK docs say it falls through to canUseTool even in bypass mode. A per-call PreToolUse hook also runs before permission rules. These can require another card despite a session suggestion, but the exact combination of LabQuorum hook, installed CLI and this adapter has not been run here. See [SDK permission order](https://code.claude.com/docs/en/agent-sdk/permissions) and section 9.

## 3. Hooks and current Claude Code docs

**Pass-through. VERIFIED.** Adapter passes no SDK hooks option; test asserts hooks undefined (claude-adapter.test.ts:978-981). However project settings load by default as above, so hooks declared in the agent project's .claude/settings.json are read. This is settings pass-through, not an adapter hook callback.

**PreToolUse. VERIFIED in current official docs.** PreToolUse hookSpecificOutput.permissionDecision accepts allow, deny, ask, or defer; docs say ask requests permission and deny blocks. [Hooks reference](https://code.claude.com/docs/en/hooks), decision table and PreToolUse decision section.

**Failure blocking. VERIFIED in current official docs, version-dependent.** Docs say: "To block the action instead, set `"onFailure": "block"` on a `command` or `http` hook. Requires Claude Code v2.1.295 or later." [Hooks reference](https://code.claude.com/docs/en/hooks). This is a documented feature, but not independent of CLI version. SDK package in this checkout is 0.3.260; the tag does not establish the SDK-bundled CLI version. Adapter prefers a configured or PATH CLI and does not check a minimum. Whether fallback CLI in this exact Console build is >=2.1.295 is UNVERIFIED. Pin or check the actual executable before relying on onFailure:block.

## 4. Template format and validation

**Parser and shapes. VERIFIED.** Switch uses a V1 room YAML parser in core/switch_core/rooms_yaml.py and V1/V2 agent template planning/compiler in core/switch_core/agent_templates.py and core/switch_core/template_v2.py. In V1, version is an integer accepted but not acted on (rooms_yaml.py:18-19,611-629). V2 is detected by version 2 or a resources key (template_v2.py:67-68).

- V1 agent template top-level keys include agent or agents, params, version, and optional room material: room, or group with rooms and links. kickoff is top-level for a single room. Agent extraction is agent_templates.py:57-60; room projection is agent_templates.py:280-288. Room parser accepts single-room top keys room, params, version, kickoff, or group keys group, rooms, links, params, version; group kickoff belongs inside each room (rooms_yaml.py:606-623).
- V2 documented envelope: version, params, resources, form. Resource types: agent, room, group. Each resource has type, optional if, and fields for that type (template_guide.py:19-35; template_v2.py:48-68,174-205).
- V2 agent fields: instructions, provider, machine, directory, name, display_name, icon_url, description, model, advanced_config, isolation, auto_mode, auto_approve, can_manage_agents, addressing, connections, repo, join, sources, allow_existing (template_guide.py:51-81). Legacy V1 also supports location instead of machine; AgentSlot/planner read provider, machine, location, model, directory and connections (agent_templates.py:120-132,631-731).
- Room fields accepted by V1 schema: name, description, instructions, bridge, channel_type, read_visibility, write_visibility, agents, users, roles, references, docs, aliases, kickoff (rooms_yaml.py:418-437). V2 guide adds the room resource group reference (template_guide.py:108-123). Room role fields: name, instructions, exclusive (room_service.py:69-72). Room doc fields: name, description, instructions, content (rooms_yaml.py:411-415). Group metadata accepts name, description, color, and links accept from, to, label (rooms_yaml.py:443-460).
- Param types: string, number, boolean, enum, agent, bridge, room, user, provider, location, machine, directory. V1 fields: type, description, label, default, required, input, enum, pattern, min, max, multiline (rooms_yaml.py:109-161). V2 adds param if (template_guide.py:131-147); compiler removes it before V1 validation (template_v2.py:335-341). V2 also allows if on resources and conditional alternatives within field values (template_guide.py:37-49).
- Addressing strings: owner, owner-agents, anyone; V2 additionally accepts {anyone_in: [room resource keys]} (template_guide.py:71-73; template_v2.py:299-315). There is no plural kickoffs key. Field is singular kickoff; group templates place it on each room (rooms_yaml.py:6-9,611-623).

**Resolution. VERIFIED.** Machine params select an owner machine; $first selects the first online machine supporting the needed provider(s) (agent_templates.py:570-583,637-663). Provider params try candidates in order; $first means first provider ready on the chosen machine (agent_templates.py:585-603,694-715). A location string names an owner machine only if it matches one; otherwise it falls back to first suitable owner machine (agent_templates.py:664-685). Directory must be given as a field or param and is interpolated as the agent working path (agent_templates.py:718-731). For bridge, $first is the first active bridge, with configured default sorted first (rooms_yaml.py:837-877). These selection rules do not guarantee Windows local support for persistent SDK agents.

**Validate labquorum-core.template.yaml key by key. VERIFIED: no schema mismatches found.**

| Template keys | Result |
|---|---|
| Top-level version: 1, params, agents, room, singular kickoff | Supported for this V1 agent-plus-room template. |
| Param lab: string, description, pattern | Supported. |
| workspace: directory, description | Supported; no default means required input. |
| provider: provider, description, default candidate list [claude], input advanced | Supported. |
| location: location, description, default local, input advanced | Supported; resolved as above, not proof of Windows-local persistent-agent support. |
| bridge: bridge, description, default [$first] | Supported; requires a resolvable active bridge, preferring the default. |
| Agent keys: name, description, addressing, provider, location, directory, auto_mode, auto_approve, instructions, can_manage_agents | All supported; addressing values and boolean types are valid. |
| Room keys: name, description, bridge, channel_type, agents, users, aliases, roles, instructions, docs | All supported. {$creator} is a built-in placeholder. Role and room-doc fields are supported. |

Evidence for actual template keys: docs/plan/templates/labquorum-core.template.yaml:2-29,30-67,68-95,112-141. Caveats: workspace is required, bridge must resolve, and location must resolve to a supported execution machine.

## 5. Addressing and identity

**Addressing. VERIFIED.** owner admits the agent owner's claimed human identity only. owner-agents admits that owner and agents owned by the same user. anyone is open to non-platform senders in the room; platform identities still need an applicable rule. A no-rule policy is open; new agents default to owner plus owner agents. See core/switch_core/addressing.py:23-46,100-150,249-306. Approval answers use the same addressing check (session_activity/service.py:452-503,571-620).

**Claiming Mattermost identity. VERIFIED.** A platform account is claimed/linked to a Switch user. Unclaimed accounts resolve to nobody, and a Switch user can claim multiple accounts: docs/official/internals/identity-and-access.md:126-134. Console flow: Home > Messaging apps > Link, search handle/name/email, select "This is me": docs/official/getting-started/add-a-server.md:76-104.

**Non-owner addressed message. VERIFIED.** It is not silently ignored. Switch demotes the attempted address to ordinary room chatter and returns an explicit refusal for an unclaimed or unauthorized sender addressing an owner-scoped agent: core/switch_core/delivery/addressing.py:378-405; docs/official/using/what-comes-back.md:97-105. A room-wide command that addresses no agent can quietly decline, a separate path (docs/official/internals/identity-and-access.md:141).

## 6. Switch MCP tools and policy mutation

**Names and server. VERIFIED.** MCP server name is switch; operation names are exported verbatim from Python function names (console/packages/switch-agent-runtime/src/hosted.ts:108-116,138-153,243-255; core/switch_core/bridges/agent/operations/registry.py:78-85). Each profile receives operations enabled for its server/profile plus runtime attachment helpers. Full declared surface:

- Room/session/context: list_rooms, connect_to_room, list_references, list_linked_rooms, load_internal_documents, create_room_document, update_room_document, delete_room_document, read_context, list_participants, post_message, send_targeted_message, get_my_context.
- Rooms, roles, references: create_room, list_roles, get_role_detail, define_role, edit_role, delete_role, assume_role, release_role, list_reference_types, create_reference, attach_reference_to_room, list_all_references, link_rooms, unlink_rooms, list_bridges, invite_agent_to_room, remove_agent_from_room, add_users_to_room, list_all_rooms, list_room_groups, create_room_group, get_room_group_detail, update_room, archive_room, unarchive_room.
- Templates and agents: create_room_from_yaml, get_template_guide, list_templates, get_template, run_template, save_template, update_template, delete_template, list_agents, get_agent_detail, request_agent_deletion, update_agent_detail.
- Service grants: set_agent_service, remove_agent_service.
- Runtime helpers: download_attachment, send_attachment (hosted.ts:156-200,243-255).
- Optional agent-management group: list_machines, get_advanced_config, create_agent, list_managed_agents; exposed only while the optional group is enabled (agent_management.py:124-276; operations/registry.py:59-62,89-118).

**Policy-affecting tools. VERIFIED.** update_agent_detail accepts addressing and can change another same-owner agent's addressing policy. It forbids self-edit, but an ordinary helper can target a peer even if can_manage_agents is false for managed fields (definitions.py:2202-2243,2278-2360). Room create/update set visibility and membership; invite/remove agent and add users change membership (definitions.py:877-1001,1369-1439,2396-2476). Template create/update/run can encode or deploy future configuration (definitions.py:1551-1580,1876-2080). Service grant tools change connected service access (agent_services.py:43-120). Room document tools modify context, not addressing policy.

**Can Claude rules deny them? VERIFIED.** Yes, for example permissions.deny: ["mcp__switch__update_agent_detail"]; server segment is switch. Official docs say: "To match one tool, write its full name, mcp__<server>__<tool>." [Permission docs](https://code.claude.com/docs/en/permissions). SDK permission order checks settings deny before allow and says deny applies even in bypass: [SDK permission docs](https://code.claude.com/docs/en/agent-sdk/permissions). This matters because Switch auto-allows its own registered MCP prefix. A LabQuorum server named labquorum has tool names like mcp__labquorum__commit_booking; Switch's host-prefix allow does not cover it.

## 7. Local server, Docker, Windows

**Server without Docker. VERIFIED.** Switch docs say Console starts its local server natively without Docker; Docker is only for optional built-in Mattermost (docs/official/deploy/index.md:15-27). Native startup resolves PostgreSQL, installs Switch Core, initializes and starts the database cluster, then launches Switch Core (console/apps/switch-console-desktop/src/main/core/managed-switch-server/native/native-stack.ts:352-366,383-396,424). Core is spawned as python -m switch_core.main, detached and hidden on Windows (native/core-process.ts:117-145).

Mattermost is container-only; launcher writes compose config, runs docker compose up -d, then runs the seeder (native/mattermost.ts:18-25,152-157,181-215). Docker Desktop networking uses host.docker.internal in the generated setup (native/mattermost.ts:60-95). With no Docker, native Switch works but the optional local Mattermost bridge does not.

**Windows persistent agents. VERIFIED.** Native local Windows Switch server is possible, but persistent SDK sessions cannot run on a local Windows execution host. Console throws "Persistent SDK sessions require a POSIX execution host. Configure an SSH host for Windows Console." at console/apps/switch-console-desktop/src/main/core/sdk-host/shared-agent-runtime.ts:410-412. For persistent Claude agents from Windows Console, use a POSIX SSH host.

**Known initialization issue. VERIFIED as an open report; root cause UNVERIFIED.** GitHub issue [#1335](https://github.com/sandbox-quantum/switch/issues/1335) is open and reports Console v0.40.1 on Windows 11 failing at initdb with exit 3221226505 (issue lines 108-174). Reporter later succeeded running bundled initdb manually with broad matching options, leaving Console process invocation implicated but root cause unproven (issue lines 357-448). Source chooses a supported installed PostgreSQL before bundled PostgreSQL for a fresh cluster (native/postgres-binaries.ts:292-329). No #1335 reference was found in checked clone docs/troubleshooting or source. Treat as a real deployment risk, not a confirmed universal failure.

## 8. Room commands and roles

Commands begin with !; checked-in guide and registrations are docs/official/resources/room-commands.md:11-27,37-100,117-188 and core/switch_core/bridges/agent/commands.py:1852-2084.

Available commands: !help, !reset, !reset-all-agents, !compact, !compact-all-agents, !interrupt, !interrupt-all-agents, !list-agents, !agents-status, !roles, !list-documents, !list-references, !list-aliases, !follow-ups, !assign-agent, !unassign-agent, !set-alias, !remove-alias, !invite-agent, !remove-agent, !rename-agent, !delete-agent, !room-url, !list-switch-agents, !agents-greet, !run-cmd. Reset/compact/interrupt have named-target and explicit all-agent forms; !agents-status is named that way because Slack reserves /status (commands.py:1852-1949).

Roles are room-scoped instruction bundles with name, instructions, exclusive. Exclusive means at most one live agent can hold the lease; it auto-releases after disconnect. Shared roles can have multiple holders. An agent assumes a role to receive its instructions and releases it when done; any room member may assume it unless an exclusive role is occupied (room_service.py:69-72; definitions.py:1016-1129). !roles lists roles and holders. Targeting @role fans out to its live holder(s), one for exclusive roles and all for shared roles (definitions.py:801-823).

## 9. Section 3.2 assumptions checked against Switch source

- **Session approval is not inherently fresh per call. CONTRADICTION if design relies on the card alone.** Switch offers Allow for this session and returns the CLI permission suggestion scoped to the Claude session. The tested generic MCP suggestion is tool-name-only, and SDK docs say the user is not prompted again for that tool. That can suppress the plan's second card. A matching ask rule or per-call hook may force later calls back through canUseTool; exact LabQuorum tool and installed CLI behavior is UNVERIFIED and must be tested. Evidence: claude-adapter.ts:369-372,1213-1218; claude-adapter.test.ts:876-906,1317-1355; [SDK permission order](https://code.claude.com/docs/en/agent-sdk/permissions), [SDK reference](https://code.claude.com/docs/en/agent-sdk/typescript).
- **Switch does not enforce the CLI version required by the proposed hook. SOURCE DOES NOT GUARANTEE THE PLAN'S VERSION.** It may use configured/PATH CLI or SDK fallback, with no >=2.1.295 check (claude-adapter.ts:296-323,475-477). Current docs require >=2.1.295 for command/HTTP onFailure:block. The build must enforce and record this itself.
- **Switch callback is not a general policy gate for Switch MCP tools.** Host Switch MCP calls are pre-allowed by adapter rules and callback prefix shortcut; they do not get native approval cards. This supports the plan's explicit deny of mcp__switch__update_agent_detail. Explicit Claude deny is checked before allow, including bypass (SDK permission docs above). Evidence: claude-adapter.ts:391-403,1124-1142; claude-adapter.test.ts:1287-1298.
- **No automatic Switch-card expiry is supplied in this adapter path.** If section 3.2's timeout means closing an unanswered provider card, current adapter does not do so; expiresAt is null and no timer starts. The plan's 5-second hook timeout is separate. Evidence: session-host.ts:1138-1144; claude-adapter.ts:1204-1232; session_activity/service.py:359-387.
- **Switch-side identity claim is consistent with the plan.** Switch checks platform identity and addressing when answering. LabQuorum's future decision hash, ledger transaction, and structured-decision validation are not Switch behavior and remain UNVERIFIED by this research.

## Build implications

1. Put each agent's .claude/settings.json under the directory Switch passes as cwd. For .mcp.json, use the directory the pinned CLI treats as project root; Switch passes cwd and strictMcpConfig:false, but the exact nested agents/<name> lookup is UNVERIFIED. Test with the deployed CLI. Use strict JSON. Default SDK sources load user/project/local settings; current Windows settings.local.json placement can differ.
2. Name the LabQuorum server labquorum in .mcp.json; tools then appear as mcp__labquorum__<tool>. Use a project-scoped server config with argument arrays, absolute executable/project paths where needed, and environment-variable expansion for machine-specific values. Do not name it switch, which is the host integration. Exact LabQuorum command/args depend on its future MCP entrypoint and are UNVERIFIED.
3. In settings, deny Switch control-plane mutators by exact MCP name, at minimum mcp__switch__update_agent_detail for every agent. Include room membership/configuration and service grant mutators according to the desired boundary. Deny rules precede Switch host allow and apply in bypass.
4. For gated LabQuorum tools, add an exact ask rule and/or PreToolUse hook matching mcp__labquorum__commit_booking. Have the hook return ask for every eligible call in the certified mode; deny auto/bypass/dontAsk/unknown modes; set onFailure:block for command/HTTP hooks. Use generated absolute executable/project paths and quote Windows paths with spaces. Verify repeated same-session calls still make distinct Switch cards after someone selects Allow for this session.
5. Pin or preflight actual Claude executable >=2.1.295 before relying on hook failure blocking. Adapter's PATH/fallback resolution does not prove that version. On Windows, use a POSIX SSH execution host for persistent SDK agents; native local server and local Windows agent execution are separate capabilities.
6. The template can remain V1: top-level agents, room, params, version: 1, and singular top-level kickoff. Supplied keys match the parser. Supply workspace, ensure a default bridge exists for $first, and point location resolution at a POSIX SSH machine for persistent agents.

## UNVERIFIED and open issues

- Exact future LabQuorum executable command/args and Claude's permission suggestion for mcp__labquorum__commit_booking.
- Whether a specific Console-resolved CLI is >=2.1.295, and exact hook/session-allow behavior on that tuple.
- LabQuorum ledger, canonical decision, expiry, revision, and audit guarantees are outside this Switch source review.
- Windows native initdb issue #1335 is open; this research does not establish a fix or universal root cause.

