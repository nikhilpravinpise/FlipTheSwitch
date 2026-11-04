# 10. Decision record

Back to the [master plan](README.md).

## Method

Scores are prospective judgments on a 0 to 10 scale, where higher is better. Weighted totals are the sum of each score times its percentage weight divided by 100. Criteria and weights reflect the particular choice, not forecasts of judging. Risk scores are subjective ordinal judgments, with higher scores meaning lower risk. Margins compare the winner with the highest-scoring alternative; margins below 0.5 are flagged sensitive as a screening rule, not a robustness test. Evidence describes assumptions to test, not completed results. A conditional choice remains subject to its stated gate. Judging weights are Switch 30%, technical execution 25%, creativity and impact 25%, presentation 20% ([scorecard](09-submission-and-risks.md)); each local criterion approximates the relevant judging dimensions while explicitly accounting for builder-hours and delivery or authorization risk. These illustrative weights express the solo builder’s preferences and are not estimated risk probabilities or a conversion of the judging rubric. Score anchors: 0 means fails the criterion, 5 means partial or unproven, 10 means excellent and verified; local low/base/high ranges below are plausible judgments, not confidence intervals. Hard certification gates override weighted totals. Scores are ordinal estimates, not measured probabilities or forecasts; decimal totals are arithmetic, not measurement precision. Effort and risk can correlate; criteria address distinct consequences but independence is not assumed. A one-point score change shifts a total by the criterion weight divided by 100. Linked plans and reviews establish the rationale, not implementation.

## Summary

| Decision | Winner | Margin | Sensitivity |
| --- | --- | ---: | --- |
| [Name](#name) | LabQuorum | 0.75 | Not within 0.5 |
| [Approval mechanism](#approval-mechanism) | Certified native card | 1.55 | Not within 0.5 |
| [Agent count](#agent-count) | Four core agents | 1.15 | Not within 0.5 |
| [Provider](#provider) | Claude Code only | 2.75 | Not within 0.5 |
| [Application stack](#application-stack) | Python and MCP | 3.25 | Not within 0.5 |
| [Database](#database) | SQLite | 0.30 | Sensitive |
| [MCP versus CLI](#mcp-versus-cli) | MCP profiles | 1.65 | Not within 0.5 |
| [Analysis isolation](#analysis-isolation) | Fixed descriptive recipe | 2.20 | Not within 0.5 |
| [Scholarly APIs](#scholarly-apis) | OpenAlex plus Crossref | 0.25 | Sensitive |
| [Verifier thresholds](#verifier-thresholds) | Frozen 40 regression plus 24 holdout | 1.25 | Not within 0.5 |
| [Stale cascade](#stale-cascade) | Detect stale | 0.60 | Not within 0.5 |
| [Demo scenario](#demo-scenario) | Synthetic EGCG plate | 2.15 | Not within 0.5 |
| [Demo duration](#demo-duration) | 3:50 target | 1.05 | Not within 0.5 |
| [Cut order](#cut-order) | Cut discovery order roles mobile first | 5.10 | Not within 0.5 |
| [Test tools](#test-tools) | pytest and Playwright | 3.00 | Not within 0.5 |
| [Eval metric](#eval-metric) | pass^3 plus Wilson intervals | 2.75 | Not within 0.5 |
| [CI scope](#ci-scope) | Offline deterministic matrix | 2.60 | Not within 0.5 |
| [Schedule](#schedule) | Rebased 41 h 10 min core | 2.20 | Not within 0.5 |
| [Wispr usage](#wispr-usage) | Authentic build dictation and Insights | 3.75 | Not within 0.5 |
| [Prize stacking](#prize-stacking) | Main track plus eligible side tracks | 3.60 | Not within 0.5 |
| [Core PR](#core-pr) | Skip before submission | 3.30 | Not within 0.5 |
| [Novelty: release gate](#novelty-release-gate) | Conditional tested release gate | 4.80 | Not within 0.5 |
| [Novelty: source flow](#novelty-source-flow) | Optional source labeling | 2.55 | Not within 0.5 |
| [Novelty: RO-Crate](#novelty-ro-crate) | Optional provenance export | 2.55 | Not within 0.5 |
| [Novelty: delegation](#novelty-delegation) | Defer scoped delegation | 4.00 | Not within 0.5 |
| [User study](#user-study) | One optional 0.5 h booking observation | 0.20 | Sensitive |
| [Room layout](#room-layout) | One core room | 0.60 | Not within 0.5 |
| [External sharing](#external-sharing) | Synthetic internal demo | 3.70 | Not within 0.5 |
| [Server path](#server-path) | Native Windows first | 1.35 | Not within 0.5 |
| [WAL safety](#wal-safety) | Fixed SQLite or rollback journal | 3.20 | Not within 0.5 |
| [Citation fixture](#citation-fixture) | Pinned known relationship or labeled generic | 4.30 | Not within 0.5 |
| [Decision snapshot](#decision-snapshot) | Canonical fields and transactional hash | 2.45 | Not within 0.5 |
| [Booking stock](#booking-stock) | 22 mL available with 20 mL example | 4.70 | Not within 0.5 |
| [Submission timing](#submission-timing) | 19:00 target | 4.70 | Not within 0.5 |
| [Oversized approval payload](#oversized-approval-payload) | Fail closed on truncation | 2.70 | Not within 0.5 |
| [Citation identity matching](#citation-identity-matching) | Exact normalized full title or review | 3.15 | Not within 0.5 |
| [Protocol history](#protocol-history) | Preserve performed version and classify changes | 2.80 | Not within 0.5 |
| [Numeric claim grounding](#numeric-claim-grounding) | Render structured values from run JSON | 3.10 | Not within 0.5 |
| [Booking duration](#booking-duration) | 60 minutes within 14:00-17:00 | 5.80 | Not within 0.5 |


## Decisions

### Name

- **Recognition, 45%:** first viewers must understand the project.
- **Fit, 35%:** the name should convey lab coordination.
- **Change cost, 20%:** late renaming consumes packaging time.

**LabQuorum: 7.20/10.** Recognition 7/10: lab context is explicit. Fit 7/10: coordination is suggested but quorum may imply multiple approvers. Change cost 8/10: current plan already uses it.

Total: 0.45 x 7 + 0.35 x 7 + 0.20 x 8 = 7.20.

**BenchRelay: 6.45/10.** Recognition 7/10: short and readable. Fit 6/10: relay suggests handoff without a lab decision. Change cost 6/10: existing references require editing.

Total: 0.45 x 7 + 0.35 x 6 + 0.20 x 6 = 6.45.

Margin: 0.75 points. Evidence: [02-product.md](02-product.md). Revisit: Ask a fresh viewer whether the name implies multiple approvers and check for a name conflict before publication.

### Approval mechanism

- **Boundary evidence, 45%:** unauthorized commits have high impact.
- **Builder time, 30%:** the deadline limits fallback work.
- **Switch demonstration, 25%:** the platform decision must be visible.

**Certified native card: 7.35/10.** Boundary evidence 6/10: card behavior is supported by source but S2 and S3 remain unexecuted. Builder time 8/10: reuses provider and Switch facilities. Switch demonstration 9/10: the request and actor appear in the room.

Total: 0.45 x 6 + 0.30 x 8 + 0.25 x 9 = 7.35.

**Certified steward: 5.80/10.** Boundary evidence 7/10: sender and revision checks can work if replay and crash tests pass. Builder time 3/10: architecture estimates 3-5 hours plus tests. Switch demonstration 7/10: Switch routes messages while steward checks identity.

Total: 0.45 x 7 + 0.30 x 3 + 0.25 x 7 = 5.80.

Margin: 1.55 points. Evidence: [03-architecture.md#32-the-two-layer-approval-model](03-architecture.md#32-the-two-layer-approval-model). Revisit: Run S2 and S3a-d plus E2E-11; disable commits on failure unless a separately funded steward passes its full suite.

### Agent count

- **Scope fit, 40%:** roles must cover the demo.
- **Builder time, 35%:** each agent needs setup and tests.
- **Capacity risk, 25%:** session pressure can block the demo.

**Four core agents: 7.15/10.** Scope fit 8/10: separates booking operations and decisions; scout and analyst are present but analysis and writing are deferred. The prospective scope-fit score remains 8 for the funded booking demonstration. Builder time 7/10: one fewer profile than the five-agent template. Capacity risk 6/10: S6 capacity is unmeasured.

Total: 0.40 x 8 + 0.35 x 7 + 0.25 x 6 = 7.15.

**Five core agents: 6.00/10.** Scope fit 9/10: adds a dedicated specialist. Builder time 4/10: another agent expands setup and test surface. Capacity risk 4/10: one more session adds memory pressure.

Total: 0.40 x 9 + 0.35 x 4 + 0.25 x 4 = 6.00.

Margin: 1.15 points. Evidence: [02-product.md](02-product.md). Revisit: Measure S6 and 20% RAM headroom; compare same-task correctness and provider usage before adding a fifth.

### Provider

- **Certification risk, 45%:** provider changes can undermine approval.
- **Builder time, 35%:** each runtime needs tests.
- **Portability, 20%:** another provider reduces dependency.

**Claude Code only: 6.75/10.** Certification risk 7/10: named card and hook path has tests but no installed proof. Builder time 8/10: one provider tuple needs certification. Portability 4/10: core depends on one provider.

Total: 0.45 x 7 + 0.35 x 8 + 0.20 x 4 = 6.75.

**Multiple providers: 4.00/10.** Certification risk 3/10: each needs approval and bypass tests. Builder time 3/10: another integration consumes core hours. Portability 8/10: another certified provider reduces dependency.

Total: 0.45 x 3 + 0.35 x 3 + 0.20 x 8 = 4.00.

Margin: 2.75 points. Evidence: [03-architecture.md](03-architecture.md). Revisit: Revisit when a second provider passes all S2 and S3 gate tests within measured slack.

### Application stack

- **Shared implementation, 40%:** analysis and service should share dependencies.
- **Delivery time, 35%:** Windows setup must fit the deadline.
- **Interface reach, 25%:** a dedicated interface could improve access.

**Python and MCP: 7.90/10.** Shared implementation 9/10: recipe and ledger share the Python stack. Delivery time 8/10: one language and typed tools reduce integration work. Interface reach 6/10: users rely on Switch rather than a dedicated UI.

Total: 0.40 x 9 + 0.35 x 8 + 0.25 x 6 = 7.90.

**TypeScript web app: 4.65/10.** Shared implementation 4/10: analysis still needs a separate Python path. Delivery time 3/10: another interface and service add integration. Interface reach 8/10: dedicated browser views can improve reach.

Total: 0.40 x 4 + 0.35 x 3 + 0.25 x 8 = 4.65.

Margin: 3.25 points. Evidence: [03-architecture.md#technology-choices](03-architecture.md#technology-choices). Revisit: Run S2 and clean clone M-03; reconsider if Python setup or tool discovery blocks reproduction.

### Database

- **Transaction safety, 45%:** conflicts and duplicate commits have high impact.
- **Setup effort, 35%:** a solo demo needs reproducible provisioning.
- **Scaling, 20%:** future multi-host concurrency may matter.

**SQLite: 7.55/10.** Transaction safety 8/10: immediate transactions and busy timeout support local writes. Setup effort 9/10: one local file avoids another server. Scaling 4/10: multi-host write scaling is limited.

Total: 0.45 x 8 + 0.35 x 9 + 0.20 x 4 = 7.55.

**PostgreSQL: 7.25/10.** Transaction safety 9/10: server transactions support concurrent clients. Setup effort 4/10: server provisioning adds work. Scaling 9/10: multi-host concurrency is better supported.

Total: 0.45 x 9 + 0.35 x 4 + 0.20 x 9 = 7.25.

Margin: 0.30 points. Evidence: [03-architecture.md#technology-choices](03-architecture.md#technology-choices). Revisit: Run I-01 for 50 concurrent attempts and a restore test; reconsider for measured contention or multi-host requirements.
Calibration: during the scheduled transactional-store block, run I-01 and record actual contention and failures; absent results the scores are provisional. Sensitive: if I-01 reveals enough contention or transaction failures to lower SQLite transaction safety by one point, its total falls 0.45 and PostgreSQL leads.

### MCP versus CLI

- **Approval binding, 45%:** actions must map to permission decisions.
- **Runtime feasibility, 35%:** Console discovery must work.
- **Simplicity, 20%:** configuration must be maintainable.

**MCP profiles: 7.10/10.** Approval binding 8/10: typed per-action names support proposed ask rules. Runtime feasibility 6/10: S2 discovery and enforcement are unverified. Simplicity 7/10: profiles expose relevant tools.

Total: 0.45 x 8 + 0.35 x 6 + 0.20 x 7 = 7.10.

**Gate-only CLI: 5.45/10.** Approval binding 6/10: exact command approval depends on shell composition tests. Runtime feasibility 5/10: requires loaded settings and a separate profile. Simplicity 5/10: quoting and shell restrictions add complexity.

Total: 0.45 x 6 + 0.35 x 5 + 0.20 x 5 = 5.45.

Margin: 1.65 points. Evidence: [03-architecture.md#technology-choices](03-architecture.md#technology-choices). Revisit: If S2 shows settings work but MCP launch alone fails, test CLI shell composition and repeat the full gate suite.

### Analysis isolation

- **Scientific validity, 45%:** invalid inference would mislead.
- **Execution risk, 35%:** generated code expands the attack surface.
- **Flexibility, 20%:** additional recipes may serve future work.

**Fixed descriptive recipe: 7.55/10.** Scientific validity 8/10: a single plate supports descriptive results without biological inference. Execution risk 9/10: the model does not write arbitrary core code. Flexibility 4/10: only vetted recipes are available.

Total: 0.45 x 8 + 0.35 x 9 + 0.20 x 4 = 7.55.

**Generated script container: 5.35/10.** Scientific validity 4/10: a container alone does not validate statistics. Execution risk 5/10: generated code and sandbox require negative tests. Flexibility 9/10: arbitrary scripts cover more analyses.

Total: 0.45 x 4 + 0.35 x 5 + 0.20 x 9 = 5.35.

Margin: 2.20 points. Evidence: [03-architecture.md](03-architecture.md). Revisit: Run recipe golden tests and E2E-08; revisit for a validated sandbox and a demonstrated use case.

### Scholarly APIs

- **Coverage, 40%:** fixture signals must be available.
- **Operational risk, 35%:** rate limits can disrupt demonstrations.
- **Breadth, 25%:** more indexes may help discovery.

**OpenAlex plus Crossref: 7.10/10.** Coverage 7/10: planned discovery and relationship metadata. Operational risk 8/10: cassettes and caching limit outages. Breadth 6/10: two sources leave gaps.

Total: 0.40 x 7 + 0.35 x 8 + 0.25 x 6 = 7.10.

**Many APIs: 6.85/10.** Coverage 8/10: additional sources may fill gaps. Operational risk 4/10: more keys and failures require tests. Breadth 9/10: more indexes widen coverage.

Total: 0.40 x 8 + 0.35 x 4 + 0.25 x 9 = 6.85.

Margin: 0.25 points. Evidence: [03-architecture.md#34-scholarly-apis-and-budgets](03-architecture.md#34-scholarly-apis-and-budgets). Revisit: Inspect pinned fixture coverage and live budgets; add sources only for a demonstrated gap.
Calibration: scholarly work is deferred; before enabling it separately fund and time the pinned fixture comparison against an extra API, recording coverage and failures. Sensitive: if pinned fixture testing shows the chosen pair misses a required source that an extra API reliably supplies, lowering its coverage score by one point reduces its total by 0.40 and flips this choice.

### Verifier thresholds

- **False verification risk, 45%:** wrong verified citations can mislead.
- **Evidence quality, 35%:** a holdout reduces self-confirmation.
- **Implementation time, 20%:** labels must fit the build.

**Frozen 40 regression plus 24 holdout: 7.05/10.** False verification risk 8/10: adversarial classes expose false verification. Evidence quality 7/10: source-separated holdout is planned but unrun. Implementation time 5/10: 64 labels require adjudication.

Total: 0.45 x 8 + 0.35 x 7 + 0.20 x 5 = 7.05.

**DOI-only baseline: 5.80/10.** False verification risk 5/10: DOI alone does not prove identity or claim support. Evidence quality 5/10: baseline misses non-DOI cases. Implementation time 9/10: simple rule is quick.

Total: 0.45 x 5 + 0.35 x 5 + 0.20 x 9 = 5.80.

Margin: 1.25 points. Evidence: [06-testing.md](06-testing.md). Revisit: Run citation goldens and per-class confusion matrices against the DOI baseline; revisit for unacceptable false verification.

### Stale cascade

This conditional roadmap choice does not fund stale detection; the booking-only baseline has none.

- **Delivery risk, 45%:** unfunded work can threaten booking.
- **Demonstrated consequence, 35%:** release denial is the proposed distinction.
- **Claim integrity, 20%:** story must match behavior.

**Detect stale: 7.15/10.** Delivery risk 8/10: stale detection is scoped and release needs separate funding. Demonstrated consequence 5/10: a warning alone does not prevent release. Claim integrity 9/10: narrow claim follows observed behavior.

Total: 0.45 x 8 + 0.35 x 5 + 0.20 x 9 = 7.15.

**Promote minimal tested release gate: 6.55/10.** Delivery risk 4/10: four transitions lack funded implementation and E2E time. Demonstrated consequence 9/10: refusal rerun and fresh decision show consequence. Claim integrity 8/10: full claim is defensible after the cycle passes.

Total: 0.45 x 4 + 0.35 x 9 + 0.20 x 8 = 6.55.

Margin: 0.60 points. Evidence: [03-architecture.md#33-data-model-and-invariants](03-architecture.md#33-data-model-and-invariants). Revisit: Reforecast after core gates; promote only with funded implementation and E2E-14 proving correction refusal regeneration and fresh decision; see [VN-01](../review/round2/v-novelty.md).

### Demo scenario

This comparison selects a fixture for the separately funded expanded scenario. The funded booking-only demo uses the conflict and alternative in [04](04-demo.md); no plate is required.

- **Evidence trace, 45%:** a correction must map to exact data.
- **Clarity, 35%:** judges must understand the scenario.
- **Preparation, 20%:** fixtures must be ready.

**Synthetic EGCG plate: 7.65/10.** Evidence trace 8/10: C5 and dataset versions are pinned. Clarity 7/10: dose grid is visual but needs a synthetic label. Preparation 8/10: seed and correction are specified.

Total: 0.45 x 8 + 0.35 x 7 + 0.20 x 8 = 7.65.

**Cooling study: 5.50/10.** Evidence trace 5/10: no comparable correction fixture is specified. Clarity 7/10: cooling is a familiar scenario. Preparation 4/10: new data and narration need preparation.

Total: 0.45 x 5 + 0.35 x 7 + 0.20 x 4 = 5.50.

Margin: 2.15 points. Evidence: [04-demo.md](04-demo.md). Revisit: Rehearse C5 mapping and paired output; reconsider if viewers cannot follow or fixture fails.

### Demo duration

This compares expanded cuts only. The funded booking-only and proposal-only targets are each 2:00; the 3:50 expanded target requires separately funded capabilities.

- **Viewer comprehension, 40%:** proof must be legible.
- **Deadline effort, 35%:** editing competes with delivery.
- **Coverage, 25%:** core decision must fit.

**3:50 target: 7.10/10.** Viewer comprehension 7/10: short target focuses on refusal and commit but is unmeasured. Deadline effort 8/10: 230 seconds constrains editing. Coverage 6/10: optional beats make script dense.

Total: 0.40 x 7 + 0.35 x 8 + 0.25 x 6 = 7.10.

**Longer walkthrough: 6.05/10.** Viewer comprehension 6/10: more context can delay the decision. Deadline effort 4/10: more footage needs recording and review. Coverage 9/10: more time permits explanation.

Total: 0.40 x 6 + 0.35 x 4 + 0.25 x 9 = 6.05.

Margin: 1.05 points. Evidence: [04-demo.md](04-demo.md). Revisit: Time three rehearsals and inspect the submission form; adjust for measured legibility or actual limits.

### Cut order

- **Core integrity, 50%:** human decision is central to binding workflow.
- **Time recovery, 30%:** cuts must free implementation hours.
- **Presentation, 20%:** remaining story must be coherent.

**Cut discovery order roles mobile first: 8.30/10.** Core integrity 9/10: booking decision and refusal remain. Time recovery 8/10: optional integrations can be removed. Presentation 7/10: booking has a reduced-cut ending.

Total: 0.50 x 9 + 0.30 x 8 + 0.20 x 7 = 8.30.

**Cut human decision: 3.20/10.** Core integrity 1/10: central authorization claim disappears. Time recovery 7/10: gate and tests save time. Presentation 3/10: proposal lacks promised consequence.

Total: 0.50 x 1 + 0.30 x 7 + 0.20 x 3 = 3.20.

Margin: 5.10 points. Evidence: [08-build-schedule.md](08-build-schedule.md). Revisit: At each 08 checkpoint compare remaining hours with measured velocity and use booking-only shots when analysis is cut.

### Test tools

- **Stack fit, 45%:** tests must exercise implementation.
- **Browser coverage, 30%:** cards need real UI checks.
- **Setup cost, 25%:** toolchain overhead matters.

**pytest and Playwright: 8.20/10.** Stack fit 9/10: pytest covers Python and Playwright browser personas. Browser coverage 8/10: plan specifies actual UI and card checks. Setup cost 7/10: one Python runner plus browser setup.

Total: 0.45 x 9 + 0.30 x 8 + 0.25 x 7 = 8.20.

**TypeScript-only browser suite: 5.20/10.** Stack fit 4/10: Python domain needs a bridge or another runner. Browser coverage 8/10: Playwright exercises browser flows. Setup cost 4/10: another language adds integration work.

Total: 0.45 x 4 + 0.30 x 8 + 0.25 x 4 = 5.20.

Margin: 3.00 points. Evidence: [06-testing.md](06-testing.md). Revisit: Run first local test and E2E-02 and E2E-03 on Windows; reconsider if setup blocks execution.

### Eval metric

- **Repeatability, 45%:** one model run is weak evidence.
- **Uncertainty, 35%:** small samples must not imply precision.
- **Ease, 20%:** method must fit the deadline.

**pass^3 plus Wilson intervals: 7.40/10.** Repeatability 8/10: repeated trials expose variation. Uncertainty 8/10: Wilson reports uncertainty under assumptions. Ease 5/10: five trials and dependence checks take time.

Total: 0.45 x 8 + 0.35 x 8 + 0.20 x 5 = 7.40.

**Single pass rate: 4.65/10.** Repeatability 4/10: one pass can hide variation. Uncertainty 3/10: one result gives weak uncertainty. Ease 9/10: one execution is cheap.

Total: 0.45 x 4 + 0.35 x 3 + 0.20 x 9 = 4.65.

Margin: 2.75 points. Evidence: [06-testing.md](06-testing.md). Revisit: Run five-trial evals and inspect dependence; report counts without independence extrapolation if trials are dependent.

### CI scope

- **Reproducibility, 45%:** CI must run without provider availability.
- **Fault coverage, 30%:** API failures need explicit tests.
- **Live realism, 25%:** actual integrations need evidence.

**Offline deterministic matrix: 7.45/10.** Reproducibility 9/10: cassettes and network blocking avoid live dependence. Fault coverage 8/10: fault injection covers errors. Live realism 4/10: CI does not certify installed runtime.

Total: 0.45 x 9 + 0.30 x 8 + 0.25 x 4 = 7.45.

**Live provider tests in CI: 4.85/10.** Reproducibility 3/10: secrets and rate limits make runs variable. Fault coverage 5/10: real failures are visible but difficult to reproduce. Live realism 8/10: real calls exercise endpoints.

Total: 0.45 x 3 + 0.30 x 5 + 0.25 x 8 = 4.85.

Margin: 2.60 points. Evidence: [06-testing.md#66-ci-githubworkflowsciyml](06-testing.md#66-ci-githubworkflowsciyml). Revisit: Run offline Windows and Ubuntu matrix and separately record local real-runtime E2E; revisit with reliable isolated infrastructure.

### Schedule

- **Deadline feasibility, 50%:** delivery before cutoff is mandatory.
- **Functional coverage, 30%:** more scope can increase proof.
- **Fatigue and contingency, 20%:** one builder needs rest and slack.

**Rebased 41 h 10 min core: 5.60/10.** Deadline feasibility 6/10: smaller reforecast remains unvalidated and may overlap. Functional coverage 6/10: cuts retain booking while features fall away. Fatigue and contingency 4/10: 30 minutes defect slack and reduced rest make recovery less likely.

Total: 0.50 x 6 + 0.30 x 6 + 0.20 x 4 = 5.60.

**71-109 h full scope: 3.40/10.** Deadline feasibility 1/10: original range exceeds a short solo build. Functional coverage 9/10: more optional features could be demonstrated. Fatigue and contingency 1/10: extra hours leave inadequate recovery.

Total: 0.50 x 1 + 0.30 x 9 + 0.20 x 1 = 3.40.

Margin: 2.20 points. Evidence: [08-build-schedule.md](08-build-schedule.md). Revisit: Rebase from actual time and velocity at each checkpoint; cut when blocks overlap or work exceeds waking hours; see [VT-02](../review/round2/v-technical.md).

### Wispr usage

- **Evidence authenticity, 45%:** side-track proof must show real use.
- **Integration effort, 35%:** core competes for hours.
- **Product reach, 20%:** deeper integration could serve users.

**Authentic build dictation and Insights: 7.85/10.** Evidence authenticity 9/10: clips and desktop Insights are requested evidence. Integration effort 8/10: dictation overlaps build work. Product reach 5/10: this does not implement product voice features.

Total: 0.45 x 9 + 0.35 x 8 + 0.20 x 5 = 7.85.

**Remote MCP integration: 4.10/10.** Evidence authenticity 4/10: integration alone does not prove spoken build work. Integration effort 2/10: eligibility and tests add unbudgeted work. Product reach 8/10: could add a product interaction.

Total: 0.45 x 4 + 0.35 x 2 + 0.20 x 8 = 4.10.

Margin: 3.75 points. Evidence: [05-wispr-flow.md](05-wispr-flow.md). Revisit: Verify M-01 and capture three real clips and Insights by 18:00; revisit MCP after core and package green with measured slack.

### Prize stacking

- **Eligibility evidence, 45%:** rules and form control valid submission.
- **Effort, 35%:** main workflow must ship.
- **Upside, 20%:** side tracks reward reusable evidence.

**Main track plus eligible side tracks: 8.00/10.** Eligibility evidence 8/10: entry is allowed for specified side tracks but simultaneous awards unverified. Effort 8/10: voice evidence overlaps build. Upside 8/10: several eligible awards are possible.

Total: 0.45 x 8 + 0.35 x 8 + 0.20 x 8 = 8.00.

**Core PR during build: 4.40/10.** Eligibility evidence 6/10: distinct opportunity has conflicting prize counts. Effort 2/10: up to four hours divert from workflow. Upside 5/10: stated prize is smaller and uncertain.

Total: 0.45 x 6 + 0.35 x 2 + 0.20 x 5 = 4.40.

Margin: 3.60 points. Evidence: [09-submission-and-risks.md#91-prize-stacking](09-submission-and-risks.md#91-prize-stacking). Revisit: Inspect authenticated form at S8 and official rules; adjust for actual eligibility and controls.

### Core PR

- **Deadline protection, 50%:** submission is primary.
- **Incremental value, 30%:** upstream fix can help later.
- **Effort, 20%:** PR consumes scarce hours.

**Skip before submission: 7.80/10.** Deadline protection 9/10: keeps hours on deliverable. Incremental value 5/10: postpones upstream improvement. Effort 9/10: no pre-submission PR work.

Total: 0.50 x 9 + 0.30 x 5 + 0.20 x 9 = 7.80.

**Build PR before submission: 4.50/10.** Deadline protection 3/10: four-hour diversion can displace packaging. Incremental value 8/10: merged fix could improve platform. Effort 3/10: research implementation and review use the capped block.

Total: 0.50 x 3 + 0.30 x 8 + 0.20 x 3 = 4.50.

Margin: 3.30 points. Evidence: [08-build-schedule.md#84-core-contribution-pr](08-build-schedule.md#84-core-contribution-pr). Revisit: Reconsider after confirmed submission if a reproducible fix and actual time remain.

### Novelty: release gate

- **Evidence strength, 50%:** release claims need a tested transition.
- **Delivery fit, 30%:** no release block is funded.
- **Impact, 20%:** preventing release is stronger than warning.

**Conditional tested release gate: 8.10/10.** Evidence strength 9/10: claim follows observed refusal and fresh decision. Delivery fit 8/10: stale-only fallback remains available. Impact 6/10: distinctive consequence remains uncertain.

Total: 0.50 x 9 + 0.30 x 8 + 0.20 x 6 = 8.10.

**Unconditional release claim: 3.30/10.** Evidence strength 1/10: enforcement is currently unestablished. Delivery fit 8/10: writing a claim costs little. Impact 2/10: false safety claim undermines demo.

Total: 0.50 x 1 + 0.30 x 8 + 0.20 x 2 = 3.30.

Margin: 4.80 points. Evidence: [03-architecture.md](03-architecture.md). Revisit: Require E2E-14 old-release denial rerun and fresh authorized decision before advertising enforcement.

### Novelty: source flow

- **Core delivery, 45%:** labels must not displace gate tests.
- **Review value, 35%:** source status can aid inspection.
- **Cost, 20%:** implementation needs validation.

**Optional source labeling: 7.75/10.** Core delivery 9/10: outside critical path. Review value 6/10: labels help if implemented correctly. Cost 8/10: deferral preserves potential work time.

Total: 0.45 x 9 + 0.35 x 6 + 0.20 x 8 = 7.75.

**Mandatory source-flow work: 5.20/10.** Core delivery 4/10: competes with core and packaging. Review value 8/10: visible labels may aid review. Cost 3/10: extra work is unfunded.

Total: 0.45 x 4 + 0.35 x 8 + 0.20 x 3 = 5.20.

Margin: 2.55 points. Evidence: [03-architecture.md](03-architecture.md). Revisit: Add only with core green and 1.5-2 measured hours remaining; validate labels against pinned sources.

### Novelty: RO-Crate

- **Core delivery, 45%:** export must not displace gate work.
- **Interoperability, 35%:** standard packaging may aid reuse.
- **Verification cost, 20%:** claims need checked artifacts.

**Optional provenance export: 7.75/10.** Core delivery 9/10: core can ship without export. Interoperability 6/10: optional packet may help reproducibility. Verification cost 8/10: work deferred until slack exists.

Total: 0.45 x 9 + 0.35 x 6 + 0.20 x 8 = 7.75.

**Mandatory RO-Crate: 5.20/10.** Core delivery 4/10: packaging competes for build time. Interoperability 8/10: validated export supports reuse. Verification cost 3/10: compliance and reproduction need extra tests.

Total: 0.45 x 4 + 0.35 x 8 + 0.20 x 3 = 5.20.

Margin: 2.55 points. Evidence: [03-architecture.md](03-architecture.md). Revisit: If core is green and 1.5-2 hours remain run I-16 clean-environment reproduction; no compliance claim without validation.

### Novelty: delegation

- **Authorization risk, 55%:** forged delegation can authorize harmful commits.
- **Delivery effort, 25%:** delegation needs receipts.
- **Usability, 20%:** backup approver may reduce waiting.

**Defer scoped delegation: 8.00/10.** Authorization risk 9/10: one authorized human is core policy. Delivery effort 9/10: no delegation protocol ships. Usability 4/10: requests wait or expire when unavailable.

Total: 0.55 x 9 + 0.25 x 9 + 0.20 x 4 = 8.00.

**Enable delegation now: 4.00/10.** Authorization risk 3/10: trusted receipt and negative tests are unestablished. Delivery effort 3/10: replay and policy tests cost time. Usability 8/10: verified fallback can reduce waiting.

Total: 0.55 x 3 + 0.25 x 3 + 0.20 x 8 = 4.00.

Margin: 4.00 points. Evidence: [03-architecture.md](03-architecture.md). Revisit: Revisit with independent trusted receipts and wrong-person scope replay and expiry tests.

### User study

- **Evidence quality, 45%:** one observation cannot establish demand.
- **Feasibility, 35%:** recruitment must not threaten submission.
- **Breadth, 20%:** more participants can uncover issues.

**One optional 0.5 h booking observation: 5.65/10.** Evidence quality 5/10: one uncoached observation is exploratory. Feasibility 8/10: 09 caps this at half an hour after core. Breadth 3/10: one person covers little variation.

Total: 0.45 x 5 + 0.35 x 8 + 0.20 x 3 = 5.65.

**Recruit a cohort now: 5.45/10.** Evidence quality 7/10: suitable cohort can broaden qualitative evidence. Feasibility 2/10: recruitment competes with core. Breadth 8/10: more participants expose diverse problems.

Total: 0.45 x 7 + 0.35 x 2 + 0.20 x 8 = 5.45.

Margin: 0.20 points. Evidence: [01-problem-market-usp.md](01-problem-market-usp.md). Revisit: After core green measure completion and active versus wait time; plan a larger same-task comparison if access permits.
Sensitive: a one-point cohort feasibility increase raises its total by 0.35 to 5.80 and reverses the 0.20 margin. Calibrate only after core is green by timing recruitment, all cohort sessions and analysis against a separately funded block; recruiting alone is insufficient. The selected optional 0.5 h booking observation is unfunded and cannot validate the full 1.25-1.75 h protocol.

### Room layout

Sensitivity beyond the 0.5 screen: a two-point change to the 40% demonstration-coverage score changes a total by 0.80, exceeding the 0.60 margin. Calibrate with the S4 timed room import and the Saturday two-viewer review; until then retain one room unless the observed failure justifies a separately funded reforecast.

- **Demonstration coverage, 40%:** core needs a decision room.
- **Provisioning effort, 35%:** more rooms require tests.
- **Separation, 25%:** separate contexts can help future work.

**One core room: 7.35/10.** Demonstration coverage 8/10: supports booking and decision. Provisioning effort 9/10: one template and membership setup are simpler. Separation 4/10: cross-room isolation is not demonstrated.

Total: 0.40 x 8 + 0.35 x 9 + 0.25 x 4 = 7.35.

**Two rooms in core: 6.75/10.** Demonstration coverage 9/10: can show additional project context. Provisioning effort 4/10: two templates membership and handoffs need verification. Separation 7/10: separation is possible but unproven.

Total: 0.40 x 9 + 0.35 x 4 + 0.25 x 7 = 6.75.

Margin: 0.60 points. Evidence: [02-product.md](02-product.md). Revisit: Run S4 template import and S6 capacity; add a room after core delivery and isolation checks.

### External sharing

- **Disclosure risk, 50%:** raw-data exposure has high impact.
- **Demo feasibility, 30%:** synthetic data avoids collaborator setup.
- **Collaboration value, 20%:** external review can be useful.

**Synthetic internal demo: 8.00/10.** Disclosure risk 9/10: no real research data need sharing. Demo feasibility 9/10: builder-played personas fit setup. Collaboration value 4/10: external collaboration is not demonstrated.

Total: 0.50 x 9 + 0.30 x 9 + 0.20 x 4 = 8.00.

**External collaborator room: 4.30/10.** Disclosure risk 3/10: attachment and cross-room isolation are unproven. Demo feasibility 4/10: enrollment sanitization and tests add work. Collaboration value 8/10: can demonstrate review if secured.

Total: 0.50 x 3 + 0.30 x 4 + 0.20 x 8 = 4.30.

Margin: 3.70 points. Evidence: [02-product.md](02-product.md). Revisit: Run E2E-19 for attachments documents and cross-room access and establish policy before real sharing.

### Server path

- **Feasibility evidence, 45%:** installed Windows path must start.
- **Recovery time, 35%:** failed setup can consume schedule.
- **Portability, 20%:** fallback can rescue deployment.

**Native Windows first: 6.15/10.** Feasibility evidence 6/10: Console supports intended path but S0 is unexecuted. Recovery time 7/10: no separate host if successful. Portability 5/10: depends on local install.

Total: 0.45 x 6 + 0.35 x 7 + 0.20 x 5 = 6.15.

**External Linux Compose fallback: 4.80/10.** Feasibility evidence 4/10: image health command and connection are not preflighted. Recovery time 4/10: separate host and ownership require setup. Portability 8/10: can bypass native initialization issues.

Total: 0.45 x 4 + 0.35 x 4 + 0.20 x 8 = 4.80.

Margin: 1.35 points. Evidence: [08-build-schedule.md](08-build-schedule.md). Revisit: S0 hard-stop native debugging at 90 minutes; use fallback only after separately budgeted preflight reaches a responding agent; see [SW-14](../review/round1/switch.md).

### WAL safety

- **Corruption risk, 55%:** ledger damage threatens decisions.
- **Verification effort, 25%:** installed SQLite must be checked.
- **Concurrency, 20%:** journal affects readers and writers.

**Fixed SQLite or rollback journal: 8.15/10.** Corruption risk 9/10: plan requires fixed version or safer mode. Verification effort 8/10: doctor can inspect version and journal mode. Concurrency 6/10: rollback can limit concurrent readers.

Total: 0.55 x 9 + 0.25 x 8 + 0.20 x 6 = 8.15.

**Unverified WAL version: 4.95/10.** Corruption risk 2/10: assuming bundled version does not resolve advisory. Verification effort 9/10: no initial version check required. Concurrency 8/10: WAL supports readers if safe.

Total: 0.55 x 2 + 0.25 x 9 + 0.20 x 8 = 4.95.

Margin: 3.20 points. Evidence: [03-architecture.md](03-architecture.md). Revisit: Record SQLite version and journal mode in doctor; use WAL only after advisory review and I-01.

### Citation fixture

- **Truthfulness, 50%:** invented retraction relationship misleads.
- **Reproducibility, 30%:** pinned metadata must be inspectable.
- **Dramatic clarity, 20%:** example should be understandable.

**Pinned known relationship or labeled generic: 7.60/10.** Truthfulness 8/10: relationship versus unresolved case is distinguished but needs recheck. Reproducibility 8/10: pinned fixture and retrieval date support replay. Dramatic clarity 6/10: narrow metadata claim needs explanation.

Total: 0.50 x 8 + 0.30 x 8 + 0.20 x 6 = 7.60.

**Unverified retraction story: 3.30/10.** Truthfulness 1/10: notice relationship may be wrong or stale. Reproducibility 4/10: unchecked story cannot be reliably reproduced. Dramatic clarity 8/10: dramatic allegation is easy to understand.

Total: 0.50 x 1 + 0.30 x 4 + 0.20 x 8 = 3.30.

Margin: 4.30 points. Evidence: [04-demo.md](04-demo.md). Revisit: Recheck original and notice relationship before recording; use labeled generic example if unavailable.

### Decision snapshot

- **Binding integrity, 55%:** approved content must equal executed content.
- **Visibility, 25%:** human must see critical fields.
- **Complexity, 20%:** canonical checks cost time.

**Canonical fields and transactional hash: 7.15/10.** Binding integrity 8/10: action requester resource and interval or quantity are compared transactionally. Visibility 7/10: visibility and truncation require runtime tests. Complexity 5/10: serialization and mismatch checks add work.

Total: 0.55 x 8 + 0.25 x 7 + 0.20 x 5 = 7.15.

**Revision alone: 4.70/10.** Binding integrity 3/10: revision does not prove displayed and executed fields match. Visibility 5/10: revision conceals details. Complexity 9/10: version counter is simple.

Total: 0.55 x 3 + 0.25 x 5 + 0.20 x 9 = 4.70.

Margin: 2.45 points. Evidence: [03-architecture.md#32-the-two-layer-approval-model](03-architecture.md#32-the-two-layer-approval-model). Revisit: Run C-13 I-29 and changed-field tests; fail closed on oversized or truncated cards; see [VT-04](../review/round2/v-technical.md).

### Booking stock

- **Arithmetic consistency, 45%:** seed must support stated quantity.
- **Scope honesty, 35%:** stock holds are roadmap.
- **Illustration, 20%:** shortage can illustrate refusal.

**22 mL available with 20 mL example: 8.25/10.** Arithmetic consistency 9/10: 22 minus 20 leaves 2 mL if hold exists. Scope honesty 8/10: quantity is background until stock code exists. Illustration 7/10: figures make scenario concrete.

Total: 0.45 x 9 + 0.35 x 8 + 0.20 x 7 = 8.25.

**12 mL happy path: 3.55/10.** Arithmetic consistency 2/10: 12 cannot satisfy a 20 mL hold. Scope honesty 3/10: successful hold misrepresents availability. Illustration 8/10: shortage is useful as refusal.

Total: 0.45 x 2 + 0.35 x 3 + 0.20 x 8 = 3.55.

Margin: 4.70 points. Evidence: [templates/seed-data.md](templates/seed-data.md). Revisit: Check unit-safe fixture and inventory tests before showing hold; otherwise use 22 mL as background; see [VP-02](../review/round2/v-presentation.md).

### Submission timing

- **Deadline risk, 55%:** upload failure at cutoff can lose submission.
- **Finishing time, 25%:** later work can improve polish.
- **Recovery, 20%:** buffer permits link and receipt checks.

**19:00 target: 8.25/10.** Deadline risk 9/10: leaves 4 h 59 min before supplied 23:59 IST cutoff. Finishing time 6/10: reduces last-minute polish time. Recovery 9/10: allows retries and logged-out checks.

Total: 0.55 x 9 + 0.25 x 6 + 0.20 x 9 = 8.25.

**23:59 target: 3.55/10.** Deadline risk 2/10: no buffer remains for upload surprises. Finishing time 9/10: uses all build time. Recovery 1/10: no recovery window exists.

Total: 0.55 x 2 + 0.25 x 9 + 0.20 x 1 = 3.55.

Margin: 4.70 points. Evidence: [09-submission-and-risks.md](09-submission-and-risks.md). Revisit: Inspect real form at S8 and save confirmed receipt by 19:00 IST; revise on official deadline change.

### Oversized approval payload

- **Approval integrity, 55%:** unseen fields must not authorize another action.
- **Delivery effort, 25%:** attachment binding requires work.
- **Expressiveness, 20%:** some actions exceed card limits.

**Fail closed on truncation: 8.00/10.** Approval integrity 9/10: critical fields must be visible and match canonical bytes. Delivery effort 9/10: no unverified attachment route is implemented. Expressiveness 4/10: large requests must be reduced or refused.

Total: 0.55 x 9 + 0.25 x 9 + 0.20 x 4 = 8.00.

**Digest-bound attachment: 5.30/10.** Approval integrity 5/10: could work with immutable bytes and inspection proof but neither is certified. Delivery effort 3/10: needs contract UI and negative tests. Expressiveness 9/10: can represent larger decisions.

Total: 0.55 x 5 + 0.25 x 3 + 0.20 x 9 = 5.30.

Margin: 2.70 points. Evidence: [03-architecture.md#32-the-two-layer-approval-model](03-architecture.md#32-the-two-layer-approval-model). Revisit: Run I-29 oversized and truncated cases; reconsider after digest visibility and actual inspection are proven; see [VT-04](../review/round2/v-technical.md).

### Citation identity matching

- **False-match risk, 55%:** identity errors can mislead.
- **Recall, 25%:** correct ambiguous matches should be discoverable.
- **Effort, 20%:** conservative rules need examples.

**Exact normalized full title or review: 7.85/10.** False-match risk 9/10: subsets and negations must not auto-verify. Recall 6/10: ambiguous titles go to human review. Effort 7/10: deterministic rules support tests.

Total: 0.55 x 9 + 0.25 x 6 + 0.20 x 7 = 7.85.

**Token-set threshold alone: 4.70/10.** False-match risk 2/10: a subset can score 100 while omitting critical words. Recall 8/10: fuzzy retrieval can find variants. Effort 8/10: one threshold is simple.

Total: 0.55 x 2 + 0.25 x 8 + 0.20 x 8 = 4.70.

Margin: 3.15 points. Evidence: [03-architecture.md](03-architecture.md). Revisit: Run U-C02 subset negation and mismatch cases with zero automatic passes; see [VN-03](../review/round2/v-novelty.md).

### Protocol history

- **Historical integrity, 50%:** records preserve performed protocol.
- **Current suitability, 30%:** critical changes may need review.
- **Implementation effort, 20%:** change classes add logic.

**Preserve performed version and classify changes: 7.90/10.** Historical integrity 9/10: copyedits do not rewrite performed history. Current suitability 8/10: recipe and critical changes can trigger review. Implementation effort 5/10: three outcomes need tests.

Total: 0.50 x 9 + 0.30 x 8 + 0.20 x 5 = 7.90.

**Mark all old runs stale on any release: 5.10/10.** Historical integrity 3/10: copyedit would wrongly imply numeric invalidity. Current suitability 6/10: blanket invalidation hides reasons. Implementation effort 9/10: one generic rule is easy.

Total: 0.50 x 3 + 0.30 x 6 + 0.20 x 9 = 5.10.

Margin: 2.80 points. Evidence: [03-architecture.md](03-architecture.md). Revisit: Run U-S02 for copyedit computation change and critical scientific change while preserving performed version; see [VN-04](../review/round2/v-novelty.md).

### Numeric claim grounding

- **Numerical accuracy, 50%:** a run ID alone cannot verify prose.
- **Auditability, 30%:** reader must trace numbers.
- **Effort, 20%:** structured rendering has cost.

**Render structured values from run JSON: 8.20/10.** Numerical accuracy 9/10: metric path value unit and rounding bind claims to output. Auditability 9/10: run ID and path provide trace. Effort 5/10: schema renderer and tests take work.

Total: 0.50 x 9 + 0.30 x 9 + 0.20 x 5 = 8.20.

**Free text with run IDs: 5.10/10.** Numerical accuracy 3/10: prose can cite a run while altering a number. Auditability 6/10: run is identifiable but claim unchecked. Effort 9/10: free text is easy.

Total: 0.50 x 3 + 0.30 x 6 + 0.20 x 9 = 5.10.

Margin: 3.10 points. Evidence: [03-architecture.md#33-data-model-and-invariants](03-architecture.md#33-data-model-and-invariants). Revisit: Run applicable altered-value and n tests with actual denominators; CI and p are N/A for descriptive path; see [VN-06](../review/round2/v-novelty.md).

### Booking duration

- **Feasibility, 50%:** alternative must fit requested window.
- **Clarity, 30%:** duration must be explicit.
- **Demo effort, 20%:** fixture and tests must be deterministic.

**60 minutes within 14:00-17:00: 8.80/10.** Feasibility 9/10: 15:45-16:45 fits after cleaning gap. Clarity 9/10: duration and alternative are explicit. Demo effort 8/10: one pinned alternative can be tested.

Total: 0.50 x 9 + 0.30 x 9 + 0.20 x 8 = 8.80.

**Three-hour booking within 14:00-17:00: 3.00/10.** Feasibility 1/10: occupied slot and gap leave only 75 minutes. Clarity 5/10: duration is explicit but no same-window alternative fits. Demo effort 5/10: wider search or refusal required.

Total: 0.50 x 1 + 0.30 x 5 + 0.20 x 5 = 3.00.

Margin: 5.80 points. Evidence: [02-product.md](02-product.md). Revisit: Run E2E-06 and confirm exact alternative and same-duration rule; see [VP-01](../review/round2/v-presentation.md).

### High-impact sensitivity bounds (VN-01)

Ranges below are low/base/high for each option's criterion scores in the listed criterion order. They describe plausible subjective variation, not measured bounds. If weighted ranges overlap, retain the simpler funded choice provisionally, measure its stated gate and revisit; for approval, an unpassed gate always means proposal-only, regardless of score. One-at-a-time flip thresholds hold other scores and weights fixed.

| Choice | Winner low / base / high | Alternative low / base / high | Plausible weights, sum 100%; result and flip threshold |
| --- | --- | --- | --- |
| Approval | 5,7,8 / 6,8,9 / 7,9,10 | 6,2,6 / 7,3,7 / 8,4,8 | 50/25/25 yields 7.25 vs 6.00. At base weights native boundary must drop by more than 1.55/0.45 = 3.44 points to flip. Overlap: certify native or disable binding. |
| Agent count | 7,6,5 / 8,7,6 / 9,8,7 | 8,3,3 / 9,4,4 / 10,5,5 | 45/30/25 yields 7.20 vs 6.25. Four-agent scope must drop more than 1.15/0.40 = 2.875 points to flip at base weights. Overlap: retain four pending measured capacity. |
| Database | 7,8,3 / 8,9,4 / 9,10,5 | 8,3,8 / 9,4,9 / 10,5,10 | 50/30/20 yields 7.50 vs 7.50. SQLite safety drop greater than 0.30/0.45 = 0.667 points flips base result. Overlap: retain SQLite only if I-01 and restore pass; otherwise reforecast PostgreSQL. |
| Room layout | 7,8,3 / 8,9,4 / 9,10,5 | 8,3,6 / 9,4,7 / 10,5,8 | 45/30/25 yields 7.30 vs 7.00. One-room coverage drop greater than 0.60/0.40 = 1.5 points flips base result. Overlap: retain one room pending smoke and capacity results. |

