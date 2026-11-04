## Verdict

**6/10.** Rubric: approval and trust boundary 2/4; implementation and runtime feasibility 1/2; consistency and traceability 1.5/2; source grounding and numerical accuracy 1.5/2. Scores assess the plan, not an implemented system.

Three largest remaining problems: the canonical decision is absent from C-13 and the oversized attachment path is not fully bound; the required real-runtime approval proof remains unexecuted; and the schedule gives the red-test harness no time while reserving a large unmeasured gate. The plan has improved substantially by explicitly stopping commits if certification fails.

To reach 9: fix VT-01 through VT-04, time-box and execute the full boundary tests on the pinned version tuple with recorded evidence, repair the remaining reference and scope inconsistencies, provide an executable core setup and template import, and reforecast from measured runtimes with non-overlapping blocks and explicit slack. Until then this is a contingent plan, not a certified approval system.

Status below judges whether the *plan text* remedies each finding. Resolved does not mean that implementation, E2E or installed-runtime certification has happened. Partly identifies an incomplete or conditional remedy. Research findings outside mechanism/technical scope are excluded; medium findings are sampled beyond half.

## Previous findings status

| ID | Status | Evidence quote or location |
|---|---|---|

| SW-01 | partly | 03 3.2: "deny `mcp__switch__update_agent_detail` on every agent" and reproduce/block; runtime evidence remains a release gate. |
| SW-02 | partly | 03 3.2: "inventory effective native, MCP and plugin tools" and deny PowerShell, Read, Glob, Grep and unapproved MCP; execution pending. |
| SW-03 | resolved | 03 3.2 specifies `onFailure: block`, timeout, absolute paths and four failure injections; fail startup if unproved. |
| SW-04 | resolved | 03 3.2: "Untested tuples fail preflight"; same session/tool, different payload, three repeats required. |
| SW-05 | partly | 03 3.2 requires canonical structured `decision` and full comparison; C-13 omits it and attachment branch is underspecified, VT-01/04. |
| SW-06 | resolved | 03 3.2: "domain request stays pending until independently recorded declined or expired"; interruption test three times. |
| SW-07 | resolved | Core and lab templates say each binding request needs its own decision and session consent never approves another; 03 and E2E-11 agree. |
| SW-08 | resolved | 03 3.2: "PI configures addressing in Console/Gateway before start; self-update is forbidden" and operation schema discovery. |
| SW-09 | resolved | 03 steward specifies rooms, cursor, generation, takeover, gap reconciliation, durable inbox/outbox and five recovery tests. |
| SW-10 | resolved | 06 EDGE-04 explicitly tests open/unclaimed, owner/unclaimed and claimed owner. |
| SW-11 | partly | 02 2.3 excludes external collaborators; however 02 2.1 still claims lab manager and safety can address only labops under anyone addressing. |
| SW-12 | partly | 03 3.7 and 07 K06 require creator updates and chat snapshots; 03 technology table still calls documents "the dashboard". |
| SW-13 | resolved | 03 says "Room groups and links ... Not provisioned", three HQ roles; 02 2.3 and project YAML now both use `rao-proj-<slug>` for lab `rao`. |
| SW-14 | partly | 03 3.9 specifies separate self-hosted path and 60-90 min, but 08 S0 says commands and health URL UNVERIFIED; no completed preflight or pinned image. |
| SW-15 | resolved | 03 effective configuration guard says managed vs local and "Unknown or ambiguous fails"; I-13 checks both modes. |
| SW-16 | resolved | 03 3.10 gives `3 + 5R` and room-to-ledger binding; S6 measures real session count. |
| SW-17 | resolved | 06 EDGE-01/05 require quiet unassigned group and follow-ups off. |
| SW-18 | resolved | 03 3.10 requires installed incoming/outgoing cap tests; I-27 checks both boundaries. |
| SW-19 | partly | 08 fallback demands rewrite all deliverables; 03 3.10 still says every commit uses cards and pull-plug assumes no card means no workflow. |
| SW-20 | resolved | 03 3.8 now says "set the actual provider model in Console and record it" rather than a nonexistent template model parameter. |
| SW-21 | resolved | 03 decision table: CLI only when settings pass and MCP launch alone fails; separate non-blanket Bash profile and recertification. |
| EN-01 | partly | 08 admits 40.75 h original and reforecasts 38 h 10 min; actual start must be rebased and tasks still do not fit, VT-02/03. |
| EN-02 | open | 08 09:30-11:30 places 120 min of spikes plus harness/red in 120 min; VT-02. |
| EN-03 | partly | 08 8.1 requires "behavioral red before binding commit implementation" but allocates no harness time, VT-02. |
| EN-04 | resolved | 03 specifies fail-closed hook and real failure tests, otherwise disable mutations. |
| EN-05 | partly | 03 3.2 admits "ledger does not receive an authenticated approval receipt" and excludes direct same-OS-user invocation; native boundary remains unproved pending tests. |
| EN-06 | resolved | 06 E2E-11 mandates same tool/session, actual second call, pending observation and three repeated pairs. |
| EN-07 | partly | 03 requires effective inventory and deny tests; still unexecuted and provider behavior conditional. |
| EN-08 | partly | 03 requires canonical `decision`, I-29 tests card; C-13 omits field and attachment path weak, VT-01/04. |
| EN-09 | resolved | 03 and E2E-05 distinguish native decline from domain state; E2E-10 tests both clocks. |
| EN-10 | resolved | 06 C-03 distinguishes LabQuorum exports and Switch attachment path; I-23 tests actual attachment; no broad no-export assurance. |
| EN-11 | partly | 03 operational preflight specifies staged roots and hash checks; actual interface and working runtime remain spike-dependent. |
| EN-12 | resolved | 06 E2E setup restarts relevant agent MCP processes against absolute test ledger and verifies four profile markers plus inspector. |
| EN-13 | resolved | 03 specifies per-room sessions and `3 + 5R`; 08 S6 measures actual placements. |
| EN-14 | partly | 03 operational preflight requires shared host limiter and task budgets; 3.4 still specifies individual API buckets and 3.8 per-profile rate, without clear shared mechanism or global model spend ceiling. |
| EN-15 | resolved | 03 operational preflight: check actual SQLite, fixed version or tested rollback journal; I-01/I-25 exercise it. |
| EN-16 | resolved | I-01 synchronizes before BEGIN IMMEDIATE and verifies unsafe control detection, 50 repetitions. |
| EN-17 | resolved | 06 says 50 total races, real timeout local, integration serial; CI uses separate selections. |
| EN-18 | partly | 06 6.6 has `uv lock --check`, explicit dev group and selected coverage; local-only exclusion is prose rather than executable marker expression. |
| EN-19 | resolved | 06 6.2 configures strict Pyright and CI invokes `uv run pyright`. |
| EN-20 | resolved | 06 6.6 uses `--block-network --record-mode=none`; 6.2 states scrub rules. |
| EN-21 | resolved | 03 technology choices explicitly pin `mcp<2` and test FastMCP stdio. |
| EN-22 | resolved | 03 3.6 replaces inferential recipe with descriptive summaries; SciPy inference is future work. |
| EN-23 | resolved | 03 3.6 and seed specify one synthetic plate, descriptive technical wells, no biological inference or p-values. |
| EN-24 | resolved | Seed 55-58 maps C5 to 8 ug/mL and 0.083 to 0.830; 03 stale example uses C5. |
| EN-25 | resolved | Seed 57: "synthetic high-OD QC anomalies ... not proven evaporation"; no blank subtraction or treatment outlier claim. |
| EN-26 | resolved | 02 2.3 synthetic absorbance question and seed descriptive limits remove sub-MIC claim. |
| EN-27 | resolved | Seed: "Booking holds 20 mL from 22 mL"; 12 mL rejects; purchase leaves stock unchanged. |
| EN-28 | resolved | 07 K05 rejects old revision and obtains fresh decision; I-24 checks race. |
| EN-29 | resolved | 08 Friday recording specifies a future valid slot; 07 T06 requires opening-hours check. |
| EN-30 | partly | 03 operational preflight defines revise_request, dataset supersession and packet proposal; finalization remains conditional and 06 mandatory scope needs clearer separation. |
| EN-31 | resolved | 03 3.10 describes staging, atomic rename, reconciliation and notification status; I-26 injects crashes. |
| EN-32 | resolved | 03 3.5 uses token-set for candidates only, requires full-title comparison and review of subsets; I-35 negatives. |
| EN-33 | resolved | 03 3.5 structured library IDs and separate support; 3.10 structured claims rendered from runs. |
| EN-34 | resolved | 03 3.8 calls heuristic limitations explicit and uses synthetic data; no confidentiality guarantee. |
| EN-35 | resolved | 03 3.8: "same-writer adversary can rewrite or truncate the chain". |
| EN-36 | partly | Targeted I-23 through I-35 repair many mappings; 07 L14, X10 and D08 still mismatch, VT-05. |
| EN-37 | partly | I-31 and I-32 cover several cases; I-31 still does not assert L14 dated wording, VT-05. |
| EN-38 | resolved | 06 reports Wilson [0.566, 1.000], 44.4% miss probability and labels smoke tests, not reliability proof. |
| EN-39 | partly | 06 makes full 60-run suite optional and core 15 trials; actual serial latency and mandatory E2E still unbudgeted, VT-03. |
| EN-40 | resolved | 06 setup isolated dependent scenario, E2E-10 triggers lazy expiry and tests both clocks; E2E-15 characterizes TTL. |
| EN-41 | resolved | 03 3.9 requires tzdata and ZoneInfo and rejects or disambiguates gaps/folds. |
| EN-42 | resolved | 03 3.10 and I-34 require finite values, positive duration, unit whitelist and unique wells. |
| EN-43 | partly | 03 says no groups/links and templates remove batch advice; 03 still describes room documents as a dashboard, VT-06. |
| EN-44 | resolved | 08 final Insights by 18:00, before 18:30 submission. |
| EN-45 | resolved | 06 labels 186 as planned; 07 says 120 cases are not evidence of execution. |
| EN-46 | resolved | 03 reserves CLI for launch-only failure with separate permissions and recertification. |
| EN-47 | partly | 02 cuts features and 08 makes fallback conditional, but spike allocation still overlaps, VT-02. |

| RS-02 | resolved | 03 3.10: "neither specialist agents nor card routing is novel here" and credits Switch payments example. |
| RS-03 | partly | 02 frames roles as scope choices but still uses several specialists without measured advantage; no comparative evidence. |
| RS-04 | resolved | 03 3.2 explicitly says proposals can be corrupted and tests six attacks; human deception remains possible. |
| RS-05 | partly | 03 3.4 says size limit is not privacy guarantee and synthetic/public only; stronger source-flow check is optional and arbitrary model text remains uncontrolled. |
| RS-06 | partly | 03 binds canonical decision but C-13 and long attachment path remain incomplete, VT-01/04. |
| RS-07 | resolved | 03 3.2: "one authorized human, not a multi-person quorum"; scoped delegation roadmap. |
| RS-08 | resolved | Core and lab templates require individual decision and say session consent never approves another request. |
| RS-09 | partly | 03 3.10 requires run ID, metric path, value, unit, rounding and rendered numbers; draft entity at 3.3 still only checks cited DOIs and run IDs. |
| RS-10 | partly | 03 3.5 specifies structured library IDs and separate claim support, but 3.3 and 02 core instructions retain DOI/run-ID-only wording. |
| RS-11 | resolved | 03 3.5 uses fuzzy matching for retrieval only and rejects or reviews material differences; I-35 covers subsets. |
| RS-12 | resolved | 03 3.5 says "General recall is unmeasured" and reports dated checked-source findings; G-03 expects UNRESOLVED. |
| RS-13 | resolved | 06 adds 24 source-separated holdout, DOI-only baseline, confusion matrix and Wilson intervals; 5/5 is explicitly smoke evidence. |
| RS-15 | resolved | 03 3.10 credits build-system and PROV-O foundations, identifies domain consequences. |
| RS-16 | resolved | 03 3.10 preserves performed version; copyedit zero numerical reruns and critical change REVIEW_REQUIRED. |
| RS-17 | resolved | 03 3.5: "Retraction-check snapshots are parents" and fresh check within 24 h; new retraction blocks claim. |
| RS-18 | partly | 03 3.7 specifies optional ZIP with recipe, lockfile, parameters, versions and command; I-16 still checks only shorter inventory and no clean-environment rerun. |
| RS-19 | resolved | 03 3.10 specifies optional RO-Crate 1.2 file resolution and limited compliance claim. |
| RS-20 | resolved | Seed and 03 use descriptive single-plate response, no inference or sub-MIC conclusion. |
| RS-21 | partly | Seed requires unchanged/permuted, withdrawn and reversed fixtures and "9/9 direction/abstention checks"; 06 requires same classes but does not define pairing or allocate nine runs. |
| RS-22 | partly | 03 3.7 includes sanitized decision/run timeline, but I-16 does not assert failed and rejected analyses or exclusions. |
| RS-24 | partly | 02 2.5 contains timing targets, but onboarding remains an unmeasured assumption and no explicit full task pilot gate is scheduled. |
| RS-25 | partly | 02 2.4 and 03 mark release conditional and 06 E2E-14 reflects that; 03 3.10 still asserts release/reapproval as a demonstrated consequence even if cut. |

## New findings

| ID | Severity | File and section | What is wrong | Evidence | Exact fix | Reasoning metric |
|---|---|---|---|---|---|---|

| VT-01 | high | 06, C-13; 03, 3.2 | Contract omits the decision object required to bind what the human sees; a schema passing C-13 can lack it. | C-13 requires only `request_id`, `revision`, `content_hash`; 3.2 requires canonical structured `decision`. | Require the action-specific decision fields and hash equality in C-13 and negative schema tests; test full visible input including fallback attachment. | One of four mandatory input components omitted; hash-only conformance can pass. |
| VT-02 | high | 08, 8.1-8.2 | The spike and behavioral red do not fit the assigned windows without overlap. | 09:30-11:30 assigns S2 60 min and S3a-c 60 min plus building and running the harness; the two spikes alone fill 120 min. S0/S1 require 110 min plus S8 10 min in 130 min, leaving 10 min for screenshot and transitions. | Give the harness and red test their own measured block; explicitly move work or reduce scope. Account for version certification and fallback preflight separately. | Harness has 0 min in its 120 min block; S0/S1/S8 consume 120 of 130 min. |
| VT-03 | high | 06, MVP gate; 08, 8.2 | The mandatory MVP suite still includes expiry and revision machinery beyond the single booking implementation, with no independently allocated implementation time. | 06 requires E2E-01-06 and 10-13 before recording; 08 budgets 5 h for domain/store/MCP and 3 h for selected E2E, S6 and resets. E2E-10 runs two clock orders and E2E-11 repeats three pairs plus 30 s observations. | List implementation and execution subtasks, prerequisite states and measured times; protect mandatory expiry/revision/session tests or explicitly cut capability and corresponding mandatory case. | E2E-11 alone has at least 90 s observation, excluding six calls/cards; E2E-10 has two 2 min holds if both use its stated hold, at least 4 min. |
| VT-04 | high | 03, 3.2; 06, I-29 | The long-payload attachment fallback is not bound to what is reviewed or proven visible before approval. | 3.2 says use a deterministic versioned attachment and reference if input cannot fit; no contract makes the card contain a verified attachment digest, all omitted critical fields, and a proof the PI could inspect it. I-29 permits attachment instead of card fields. | Define canonical attachment bytes and digest in the card, match them transactionally to the request, provide an accessible immutable attachment before the card, and require actual human inspection or fail closed for oversized decisions. | One alternative path lacks a specified end-to-end binding and visibility test; <900 characters applies only to the other path. |
| VT-05 | medium | 07, L14/X10/D08; 06, I-27/I-30/I-31 | Some references resolve by ID but do not test the listed property. | L14 cites I-31, which does not assert dated retraction wording; X10 cites I-27 path handling and U-D09 spreadsheet formula escaping, neither asserts safe HTML rendering; D08 cites I-30 prompt injection, not outbound query allowlisting. | Add precise assertions for dated output, HTML escaping and outbound public-input policy, or mark each manual/unverified. | 3 concrete mismatches despite zero syntactically unresolved edge references. |
| VT-06 | medium | 03, 3.3 and 3.10; 02, 2.3; templates | Stale broad architecture claims survive the MVP revision. | 03 technology table says room documents are the dashboard, though 3.7 says metadata only. 03 feature table promises a five-agent/two-room video; 02 calls both roadmap while 02 onboarding still directs users to the two roadmap templates instead of the core template. | Replace with chat snapshots, describe four-agent core and mark two-room video optional; onboard with the actual core template. | Three conflicting representations; no room group is provisioned. |
| VT-07 | medium | 10, decision record | The repeated scoring vectors make tradeoffs nominal without decision-specific justification. | For 7/7/8/8/8/8 the weighted judging sum is 7.45 and the total is 7.615; 8/8/7/8/8/8 gives 7.825. The identical vectors are reused for unrelated choices. | Retain correct arithmetic but supply option-specific evidence, uncertainty and sensitivity rather than identical unexplained inputs. | 25+ rows reuse one pair of vectors; numerical precision is not evidence of measured relative benefit. |

| VT-08 | medium | templates/README; 06 6.2/6.6 | The build and CI layout omit the actual core template; README points to example agent settings in 03 that no longer exist. | 06 layout lists only lab and project templates; CI lints `switch/*.template.yaml` without ensuring core was copied. README says settings and ask rules "are in 03", but 03 contains requirements, not a ready-to-install settings file. | Add the core template to repo layout and explicit lint/import assertions; supply actual per-profile settings and hook installation steps or say they are to be implemented and tested. | One of three template files is absent from the proposed build layout; zero executable settings examples are supplied. |
| VT-09 | medium | 03 3.9; 08 S0 | Fallback guide link differs and 03 links to a nonexistent source-tree filename; no pinned fallback artifacts or health command are supplied. | The inspected Switch source has `docs/official/deploy/self-host.md`, which 08 links; 03 links `self-hosting.md`. S0 marks commands and health URL unverified. | Correct the link and write the pinned image/Compose version, commands, health endpoint, bridge connection and a timed preflight before declaring fallback ready. | Two links name different files; only one exists in the inspected source snapshot. |
| VT-10 | medium | 03 3.5, 3.7; 06 I-16 | The optional release packet lacks the concrete reproducibility acceptance test. | 03 lists recipe, lockfile, parameters and reproduction command; I-16 checks only data, manifest, figure, draft, BibTeX and label. | If packet ships, require a clean-environment unpack and execution from included artifacts, all reported numbers compared to stated tolerances, and failure/rejection timeline assertions. | One positive inventory test omits at least four required reproduction components and the rerun. |

| VT-11 | high | 02, 2.2; 03, 3.2 | The product presents policy enforcement as already assured, contrary to the conditional test and source behavior. | 02 says folder settings "deny everything else" and C-01 to C-12 fail if either drifts; C-06 names only a subset and file checks do not establish the effective provider tool surface. Switch adapter sets `strictMcpConfig: false` and session consent can return permission updates. | Make the paragraph prospective: only the certified tuple after the effective inventory, policy-widening, same-session and failure tests may claim this boundary; reference I-23 and S3d. | At least one stated all-tools guarantee rests on static contracts that omit several named tool categories. |
| VT-12 | medium | templates/core; 06 E2E setup; 08 S1/S4 | The real two-person test requires a second Mattermost user in a private room, but the core template lists only the creator and the setup omits the enrollment step. | Core YAML has `channel_type: channel_private` and `users: ["{$creator}"]`; E2E-02 and -03 need Maya to post and click. S4 only says check members. | Specify creating the distinct accounts and explicitly adding Maya to the private room, verifying she can post before running negative approval tests; keep identity claim cases separate. | 1 listed human member versus 2 required browser personas; enrollment time is not itemized. |

## Verified facts

- **Source and limits.** Inspected Switch source snapshot commit `8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5`, already present outside the workspace, and the earlier review's release comparison. This is source inspection, not an import, Console launch, security proof or live E2E. The actual installed version tuple is unknown.
- **Approval chain.** Switch's [Claude adapter](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/console/packages/agent-providers/src/claude/claude-adapter.ts) sets `strictMcpConfig: false` and maps session acceptance to session permission updates; [bridge answer handling](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/core/switch_core/session_activity/bridge_answers.py) identifies the platform actor before sending the answer to the service. [Same-owner update logic](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/core/switch_core/bridges/agent/protocol/agent_core.py) permits control of another same-owner agent subject to its checks. The [formatter](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/console/packages/agent-providers/src/mcp-approval.ts) caps input detail at 1,000 characters. [Claude permission documentation](https://code.claude.com/docs/en/permissions) documents deny/ask/allow precedence; [hooks documentation](https://code.claude.com/docs/en/hooks) documents blocking hook failure. None proves the proposed local deny rules are actually loaded.
- **Template language.** YAML files parse as YAML per integration log; source [template guide](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/core/switch_core/template_guide.py) supports the used room, roles, docs, aliases, auto flags and top-level kickoff form. [Parameter interpolation](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/core/switch_core/rooms_yaml.py) removes optional unset entity list entries and interpolates map keys. Core specifies four agents, one room and three roles; lab five and project one room; import, entity resolution, role acquisition and runtime behavior remain untested. Project name `{lab}-proj-{project}` matches `rao-proj-egcg`.
- **Catalogue.** Parsed all scoped files' explicit test IDs: 186 distinct definitions, no duplicates or dangling explicit test IDs. All explicit edge-case IDs in scoped files also resolve. Breakdown: 79 unit, 8 property, 16 contract, 35 integration, 6 golden groups, 12 eval, 20 E2E, 6 EDGE and 4 manual. Edge table has 120 distinct rows; R/K/D/L/S/X/V/T/W/P counts are 22/12/16/14/10/12/8/6/12/8, summing to 120. Syntactic resolution is not semantic coverage, see VT-05.
- **Arithmetic.** Actual schedule intervals total 38 h 10 min; rounded displayed decimals total 38.17 h, including 1 h 55 min slack, 5 min packaging and 30 min submission. Calendar contingency 19:00-23:59 is 4 h 59 min. Category decimals total 38.17 h, subject to the infeasible overlap in VT-02. Six citation groups total 40; 12 x 5 = 60, and 3 x 5 + 5 + 8 = 28. 0.85^5 = 44.37%; 5/5 Wilson 95% is approximately [0.566, 1.000]; pass^3 uses C(c,3)/C(5,3), giving 0.4 for 4/5 and 1 for 5/5 under the stated independence assumption. 22 - 20 = 2 mL; (0.830 - 0.083)/6 = 0.1245; 7 doses x 6 wells = 42; 4 instead of 5 agents is a 20% reduction. Onboarding 2 + 0.5 + 3 + 1 + 1 + 3 = 10.5 minutes as a hypothetical estimate. Decision vectors recompute to 7.615, 7.300, 7.825 and 6.250 as stated; these are subjective inputs, VT-07.

