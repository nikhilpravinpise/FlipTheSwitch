## Verdict

**7.5/10.** Rubric, scored as a plan: approval boundary and certification design 3.3/4; delivery sequence and time budget 1.0/2; consistency and test traceability 1.5/2; technical grounding and numerical accuracy 1.7/2. Unexecuted runtime results do not reduce this score when the procedure, criteria, time box and fallback are specified; the unallocated certification block and missing setup ordering do.

The three biggest remaining problems are the unfunded separate certification block (VT-01), the two-person fixture scheduled after dependent tests (VT-02), and the baseline template advertising unbuilt agent capabilities (VT-03). To reach 9: fund and sequence every prerequisite and the distinct certification block with a rebalanced schedule and retained contingency; make the installed template reflect the booking-only baseline; repair the privacy assertion and outage expectation; then rerun the catalogue, numeric and source-consistency checks. The fallback to proposal-only is appropriate when certification fails.

## Previous findings status

Statuses assess the written remedy, not implementation. SW/EN/RS IDs are from round1 as tracked in the round2 technical review; VT and VN entries are round2 findings. Research topics outside mechanisms, such as market comparison, are excluded. All prior SW and EN findings are included, exceeding the medium sampling requirement.

| ID | Status | Evidence quote or location |
|---|---|---|
| SW-01 | resolved | 03 3.2: "deny `mcp__switch__update_agent_detail` on every agent"; S3d boxes the negative test and failure disables commits. |
| SW-02 | resolved | 03 3.2: "inventory effective native, MCP and plugin tools" and deny unapproved tools; S3d boxes negative tests and failure disables commits. |
| SW-03 | resolved | 03 3.2 specifies `onFailure: block`, timeout, absolute paths and four failure injections; fail startup if unproved. |
| SW-04 | resolved | 03 3.2: "Untested tuples fail preflight"; same session/tool, different payload, three repeats required. |
| SW-05 | resolved | 03 3.2: "if it cannot fit or a critical field is truncated, refuse the commit"; 06 C-13 requires decision. |
| SW-06 | resolved | 03 3.2: "domain request stays pending until independently recorded declined or expired"; interruption test three times. |
| SW-07 | resolved | Core and lab templates say each binding request needs its own decision and session consent never approves another; 03 and E2E-11 agree. |
| SW-08 | resolved | 03 3.2: "PI configures addressing in Console/Gateway before start; self-update is forbidden" and operation schema discovery. |
| SW-09 | resolved | 03 steward specifies rooms, cursor, generation, takeover, gap reconciliation, durable inbox/outbox and five recovery tests. |
| SW-10 | resolved | 06 EDGE-04 explicitly tests open/unclaimed, owner/unclaimed and claimed owner. |
| SW-11 | resolved | 02 2.1 and 2.3: helpers are anyone; external collaborators excluded from internal rooms. |
| SW-12 | resolved | 03 3.7: "listing documents exposes metadata only"; chat snapshots. |
| SW-13 | resolved | 03 says "Room groups and links ... Not provisioned", three HQ roles; 02 2.3 and project YAML now both use `rao-proj-<slug>` for lab `rao`. |
| SW-14 | resolved | 08 S0: "Preflight B before relying on it"; 90 min, otherwise stop binding. |
| SW-15 | resolved | 03 effective configuration guard says managed vs local and "Unknown or ambiguous fails"; I-13 checks both modes. |
| SW-16 | resolved | 03 3.10 gives `3 + 5R` and room-to-ledger binding; S6 measures real session count. |
| SW-17 | resolved | 06 EDGE-01/05 require quiet unassigned group and follow-ups off. |
| SW-18 | resolved | 03 3.10 requires installed incoming/outgoing cap tests; I-27 checks both boundaries. |
| SW-19 | resolved | 08 8.1: "disable binding mutations and explicitly present a proposal-only demo". |
| SW-20 | resolved | 03 3.8 now says "set the actual provider model in Console and record it" rather than a nonexistent template model parameter. |
| SW-21 | resolved | 03 decision table: CLI only when settings pass and MCP launch alone fails; separate non-blanket Bash profile and recertification. |
| EN-01 | partly | 08 8.2 rebases to 38 h 10 min with 1 h 55 min slack, but the separately required certification is not allocated; VT-01. |
| EN-02 | partly | 08 8.2 allocates S2/S3 120 min and a separate 90 min harness block; certification and setup sequence still conflict, VT-01 and VT-02. |
| EN-03 | resolved | 08 13:30-15:00: "behavioral red before commit implementation". |
| EN-04 | resolved | 03 specifies fail-closed hook and real failure tests, otherwise disable mutations. |
| EN-05 | resolved | 03 3.2: ledger receives no authenticated receipt; same OS user excluded; failures disable commits. |
| EN-06 | resolved | 06 E2E-11 mandates same tool/session, actual second call, pending observation and three repeated pairs. |
| EN-07 | resolved | 03 3.2 inventory and negative tests required; failed certification disables commits. |
| EN-08 | resolved | 06 C-13 requires decision, hash and revision; I-29 rejects truncation. |
| EN-09 | resolved | 03 and E2E-05 distinguish native decline from domain state; E2E-10 tests both clocks. |
| EN-10 | resolved | 06 C-03 distinguishes LabQuorum exports and Switch attachment path; I-23 tests actual attachment; no broad no-export assurance. |
| EN-11 | resolved | 03 operational preflight stages and hashes paths and requires real path test. |
| EN-12 | resolved | 06 E2E setup restarts relevant agent MCP processes against absolute test ledger and verifies four profile markers plus inspector. |
| EN-13 | resolved | 03 specifies per-room sessions and `3 + 5R`; 08 S6 measures actual placements. |
| EN-14 | resolved | 03 operational preflight: "global spend ceiling" and shared host limits. |
| EN-15 | resolved | 03 operational preflight: check actual SQLite, fixed version or tested rollback journal; I-01/I-25 exercise it. |
| EN-16 | resolved | I-01 synchronizes before BEGIN IMMEDIATE and verifies unsafe control detection, 50 repetitions. |
| EN-17 | resolved | 06 says 50 total races, real timeout local, integration serial; CI uses separate selections. |
| EN-18 | resolved | 06 CI excludes local-only with marker expression; see CI. |
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
| EN-30 | resolved | 03 operational preflight specifies revise_request and supersession; release is conditional. |
| EN-31 | resolved | 03 3.10 describes staging, atomic rename, reconciliation and notification status; I-26 injects crashes. |
| EN-32 | resolved | 03 3.5 uses token-set for candidates only, requires full-title comparison and review of subsets; I-35 negatives. |
| EN-33 | resolved | 03 3.5 structured library IDs and separate support; 3.10 structured claims rendered from runs. |
| EN-34 | resolved | 03 3.8 calls heuristic limitations explicit and uses synthetic data; no confidentiality guarantee. |
| EN-35 | resolved | 03 3.8: "same-writer adversary can rewrite or truncate the chain". |
| EN-36 | resolved | 06 I-30/I-31 assert outbound public input, dated notice and inert HTML. |
| EN-37 | resolved | 06 I-31 explicitly tests empty search and dated wording. |
| EN-38 | resolved | 06 reports Wilson [0.566, 1.000], 44.4% miss probability and labels smoke tests, not reliability proof. |
| EN-39 | partly | 08 allocates 120 min E2E and 90 min EV with proposal-only fallback, but separately required certification has no distinct allocation; see VT-01. |
| EN-40 | resolved | 06 setup isolated dependent scenario, E2E-10 triggers lazy expiry and tests both clocks; E2E-15 characterizes TTL. |
| EN-41 | resolved | 03 3.9 requires tzdata and ZoneInfo and rejects or disambiguates gaps/folds. |
| EN-42 | resolved | 03 3.10 and I-34 require finite values, positive duration, unit whitelist and unique wells. |
| EN-43 | resolved | 03 3.7 says documents provide context, not human-readable dashboard. |
| EN-44 | resolved | 08 final Insights by 18:00, before 18:30 submission. |
| EN-45 | resolved | 06 labels 186 as planned; 07 says 120 cases are not evidence of execution. |
| EN-46 | resolved | 03 reserves CLI for launch-only failure with separate permissions and recertification. |
| EN-47 | resolved | 08 gives harness, S2/S3 and S3d non-overlapping blocks. |
| RS-02 | resolved | 03 3.10: "neither specialist agents nor card routing is novel here" and credits Switch payments example. |
| RS-03 | partly | 02 frames roles as scope choices but still uses several specialists without measured advantage; no comparative evidence. |
| RS-04 | resolved | 03 3.2 explicitly says proposals can be corrupted and tests six attacks; human deception remains possible. |
| RS-05 | partly | 03 3.4 says size limit is not privacy guarantee and synthetic/public only; stronger source-flow check is optional and arbitrary model text remains uncontrolled. |
| RS-06 | resolved | 06 C-13 includes canonical decision; I-29 rejects oversized or truncated input. |
| RS-07 | resolved | 03 3.2: "one authorized human, not a multi-person quorum"; scoped delegation roadmap. |
| RS-08 | resolved | Core and lab templates require individual decision and say session consent never approves another request. |
| RS-09 | resolved | 03 3.3 draft_section includes run ID, metric path, value, unit and rounding. |
| RS-10 | resolved | 02 core instructions require structured library IDs and separate human claim-support review. |
| RS-11 | resolved | 03 3.5 uses fuzzy matching for retrieval only and rejects or reviews material differences; I-35 covers subsets. |
| RS-12 | resolved | 03 3.5 says "General recall is unmeasured" and reports dated checked-source findings; G-03 expects UNRESOLVED. |
| RS-13 | resolved | 06 adds 24 source-separated holdout, DOI-only baseline, confusion matrix and Wilson intervals; 5/5 is explicitly smoke evidence. |
| RS-15 | resolved | 03 3.10 credits build-system and PROV-O foundations, identifies domain consequences. |
| RS-16 | resolved | 03 3.10 preserves performed version; copyedit zero numerical reruns and critical change REVIEW_REQUIRED. |
| RS-17 | resolved | 03 3.5: "Retraction-check snapshots are parents" and fresh check within 24 h; new retraction blocks claim. |
| RS-18 | resolved | 06 I-16 clean-environment rerun and tolerance comparison. |
| RS-19 | resolved | 03 3.10 specifies optional RO-Crate 1.2 file resolution and limited compliance claim. |
| RS-20 | resolved | Seed and 03 use descriptive single-plate response, no inference or sub-MIC conclusion. |
| RS-21 | resolved | 06 6.4 specifies three goldened pairs, three runs each and 9 comparisons. |
| RS-22 | resolved | 06 I-16 requires failed and rejected analyses and exclusions in timeline. |
| RS-24 | partly | 02 2.5 contains timing targets, but onboarding remains an unmeasured assumption and no explicit full task pilot gate is scheduled. |
| RS-25 | resolved | 03 3.10: "Correction-bound release and reapproval require a separately implemented and tested cycle". |

| VT-01 (round2) | resolved | 06 C-13: "Require `request_id`, `revision`, `content_hash` and canonical structured `decision`"; reject mismatch. |
| VT-02 (round2) | partly | 08 8.2 has a separate 90-minute harness; 03 requires a separate certification block that 08 does not allocate. See VT-01 below. |
| VT-03 (round2) | partly | 08 allocates 120 min expiry, 90 min revision and 120 min E2E; the separate certification remains unfunded, VT-01. |
| VT-04 (round2) | resolved | 03 3.2: "if it cannot fit or a critical field is truncated, refuse the commit"; attachment is not a fallback. |
| VT-05 (round2) | resolved | 06 I-30 checks outbound private bytes; I-31 checks dated wording and inert HTML. |
| VT-06 (round2) | resolved | 02 2.3 onboards with core; 03 3.7 uses snapshots and 3.10 marks two-room optional. |
| VT-07 (round2) | resolved | 10 Method says "Scores are ordinal estimates" and uses choice-specific criteria, scores and sensitivity. |
| VT-08 (round2) | resolved | 06 6.2 includes core; CI explicitly names all three, and 06 says settings "are to be implemented and certified". |
| VT-09 (round2) | resolved | 08 S0 specifies 90-minute preflight, actual digest, commands and health URL, and says unavailable until proven; 03 uses self-host.md. |
| VT-10 (round2) | resolved | 06 I-16 requires clean-environment rerun, numeric tolerance comparison and failure/rejection timeline. |
| VT-11 (round2) | resolved | 02 2.2: "UNVERIFIED until certification" and "Any failed or unexecuted test disables commits". |
| VT-12 (round2) | partly | 08 S4 adds Maya to private room, but S1/S3 are earlier; see VT-02 below. |
| VN-03 (round2) | resolved | 06 U-C02: "Subsets, negations and material mismatches never auto-verify". |
| VN-04 (round2) | resolved | 06 U-S02 distinguishes copyedit, computation change and critical scientific change while preserving performed version. |
| VN-06 (round2) | resolved | 06 golden tests require three independently goldened pairs, 9 comparisons, metric paths and N/A for unsupported CI and p. |

## New findings

| ID | Severity | File and section | What is wrong | Evidence | Exact fix | Reasoning metric |
|---|---|---|---|---|---|---|

| VT-01 | high | 08 8.1-8.2; 03 3.2 | The promised separate two-hour installed-runtime certification has no distinct scheduled block. The Friday 120 minutes is already assigned to ten E2E scenarios and resets, while certification also requires I-14, I-23, I-29, bypass and restart tests. | 03 3.2 says "reserve a separate 2-hour maximum after building the behavioral-red harness"; 08 assigns Fri 12:45-14:45 to E2E-01-06 and 10-13. | Add a distinct 120-minute certification block and reforecast by removing work or using identified slack; specify which tests are shared only if their actual steps and elapsed time are explicitly included. Keep timeout and proposal-only fallback. | 120 min specified separately versus 0 min separately allocated; 10 E2E IDs already occupy the only 120-min block. |
| VT-02 | high | 08 S1, S3, S4 and 8.2 | Two-person identity and wrong-person approval checks precede creation and enrollment of the second person and import of the room. No earlier step provisions a test room or Maya. | S1 is Thu 08:00-09:30, S3 09:30-11:30; S4 creates PI and Maya and adds Maya Thu 19:30-22:30. | Move a separately timed minimal room, identities and membership setup before S1/S3, or explicitly allocate an equivalent disposable fixture and prove both personas can post. Rebalance the S4 and schedule totals. | Both S1 and S3 depend on fixture setup scheduled at least 8 hours after S3 starts. |
| VT-03 | medium | 02 2.2; templates/labquorum-core.template.yaml; 08 8.2 | The installed core template instructs scout and analyst to use literature and analysis tools that the funded booking-only baseline explicitly defers; kickoff wakes all four. A user can encounter missing tools, fabricated expectations or dead agent workflows. | 08 says "Literature, assay ... deferred"; core scout says "Search with search_literature" and analyst says "register_dataset, then dataset_profile"; kickoff addresses all four. | Make the baseline template instructions explicitly booking-only, tell deferred agents to state unavailable without attempting tools, or fund and test the advertised tool surfaces before enabling them. | 2 of 4 core agents advertise deferred specialist workflows; 0 implementation blocks fund them. |
| VT-04 | medium | 03 3.4; 06 I-30; 07 D08 | Outbound privacy assertions conflict with the stated limits of the implementation. I-30 requires private text refused and zero outbound private bytes; the stronger source-flow guard is roadmap and explicitly cannot track arbitrary model text. | 03: "This does not track arbitrary model text"; 07 D08 claims "Explicit allowlisted public inputs"; I-30 says "private text is refused". | For the funded core restrict requests to deterministic public fixture IDs and validate exact mapped values, or mark the assertion and D08 as deferred and do not claim general private-text refusal. Add a negative test for model-generated short private text if a guard is implemented. | 1 unconditional zero-byte assertion exceeds the 0 funded general provenance guards; synthetic-only use is an operational constraint, not classification proof. |
| VT-05 | low | 03 3.10; 06 E2E-15 | The cross-reference resolves but gives incompatible post-restart expected states when the request expires during outage. | 03 requires "pending request is still pending"; E2E-15 requires pending only if unexpired and lazy expiry otherwise. | Replace 03 expectation with the expiry-conditional E2E-15 wording and require zero commits in both branches. | 2 different expectations for the expired branch of 1 referenced test. |

## Verified facts


- **Source snapshot and limits:** inspected the local upstream Switch checkout at commit `8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5`, the same snapshot cited in the previous review. This is not evidence of the installed tuple or live behavior. Web fetches of the pinned GitHub pages returned cache errors; local source was available. The linked source is [Claude adapter](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/console/packages/agent-providers/src/claude/claude-adapter.ts), [bridge answer handler](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/core/switch_core/session_activity/bridge_answers.py), [agent update](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/core/switch_core/bridges/agent/protocol/agent_core.py), and [card formatter](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/console/packages/agent-providers/src/mcp-approval.ts).
- **Boundary:** the adapter sets `strictMcpConfig: false`, registers the provider callback and maps session suggestions to session scope. The bridge resolves the actor before passing the answer to the approval service; the handler documents the addressing check. Same-owner agent updates call `require_same_owner`; the formatter truncates JSON input after 1,000 characters. These facts justify, but do not themselves prove, the plan's installed-runtime tests. [Claude permissions](https://code.claude.com/docs/en/permissions) and [hooks](https://code.claude.com/docs/en/hooks) document the provider controls; effective settings require testing.
- **Templates:** all three files parse with PyYAML. Core creates four agents, one room and three roles; lab has five agents, one room and three roles; project has one room and no agent definitions. The inspected [template guide](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/core/switch_core/template_guide.py) and [interpolation implementation](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/core/switch_core/rooms_yaml.py) support the relevant field vocabulary and top-level single-room kickoff. YAML parsing and source inspection do not establish successful import, account linking or role acquisition.
- **Catalogue:** 187 distinct test definitions, no duplicates or unresolved explicit test references in the scoped plan and templates. Counts: 79 unit, 8 property, 16 contract, 35 integration, 6 golden groups, 12 eval, 20 E2E, 6 EDGE and 5 manual. The edge table contains 120 rows: 22 R, 12 K, 16 D, 14 L, 10 S, 12 X, 8 V, 6 T, 12 W and 8 P. ID resolution is not semantic coverage; see VT-04 and VT-05.
- **Arithmetic:** the 34 schedule rows total 2,290 minutes, 38 h 10 min; all nonzero displayed durations match their time intervals. Included slack is 115 min; post-target contingency is 4 h 59 min. A 90-min server fallback consumes 90/115 min of defect slack, leaving 25 min. The schedule total does not include the separately stated certification block, VT-01. All 78 option weighted totals and 39 displayed decision margins recompute correctly from the three criterion weights and values. The scoring inputs are subjective.
- **Other metrics:** 0.85^5 = 44.37%; 5/5 Wilson 95% interval is approximately [0.566, 1.000]; 15 core eval trials are 3 x 5, and the optional extension is 15 + 5 + 8 = 28. Three classes x three comparisons = 9. Four agents instead of five reduces configured count by 20%, not necessarily token usage. Seed arithmetic: 22 - 20 = 2 mL and the 15-minute gap after 15:30 yields 15:45; a 60-minute booking ends 16:45. These are arithmetic checks, not measured outcomes.
- **Coverage and budget:** this review inspected all SW and EN findings tracked in the prior technical review and the listed mechanism-related RS findings; the round1 RS-01, RS-14 and RS-23 relate to market comparison, citation statistics and voice novelty respectively and are outside this scope. Seven web opens were attempted, within the 20-fetch/search cap. No live Switch, model, Submit form or timing certification was run.
