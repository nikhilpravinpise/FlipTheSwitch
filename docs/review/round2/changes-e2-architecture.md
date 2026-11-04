## Applied

- SW-11, VT-11: 02 2.1-2.2 corrects anyone addressing and makes effective enforcement contingent on runtime certification.
- VT-06, VT-08, VT-12: 02 2.3/2.5 and templates/README use the core import, require private-room enrollment and identify settings as unimplemented.
- VP-01/02: 02 2.2 and seed-data specify a 60-minute request and 15:45-16:45 alternative; inventory hold is roadmap only.
- RS-09/10, RS-21, VN-06: 02 core instructions and seed-data require structured evidence, paired goldens and honest applicable denominators.

- VT-01/04, SW-05, EN-08, RS-06: 03 3.2 binds structured decision and rejects any oversized or truncated payload. The earlier attachment alternative was removed because visibility and digest binding were not certified; this removes one unsafe path.
- SW-01/02, EN-05/07, VT-11: 03 3.2 specifies 2 h estimated certification, evidence, pass/fail and proposal-only fallback. Test execution remains outstanding.
- VT-06, SW-12/19, EN-43, RS-25, VN-01: 03 3.1/3.10 use snapshots, four-agent core and branch-specific/conditional claims.
- RS-09/10, VN-06: 03 3.3 specifies structured numeric and source fields and separate support review.
- RS-18/22, VT-10: 03 3.7 requires clean-environment reproduction, tolerance checks and failure/rejection timeline if packet ships.
- EN-14: 03 operational preflight clarifies aggregate host limiter and builder-selected global spend ceiling; enforcement remains unverified.
- VT-09: 03 3.9 fixes broken self-hosting link. Primary source [self-host.md](https://github.com/sandbox-quantum/switch/blob/main/docs/official/deploy/self-host.md) explicitly describes self-deployed server plus Console; [host-remotely.md](https://github.com/sandbox-quantum/switch/blob/main/docs/official/deploy/host-remotely.md) covers onboarding a host instead. No image, health command or connection was verified; fallback stays unavailable pending timed preflight.

## Rejected

- VT-04 attachment route: rejected from core because it needs an immutable, visible, digest-bound attachment and inspection proof not budgeted or certified; oversized requests fail closed.
- RS-05 source-flow guard and RS-19 provenance export: defer 1.5-2 h each until actual slack exists; 08 reports only 1.92 h projected slack before unresolved overlaps. Do not claim protection or export before implementation.
- RS-07 capability delegation: defer 3-4 h plus independent-receipt tests; it exceeds projected 1.92 h slack. Native single-human decision remains revision and action scoped.
- RS-03 comparative agent-count evaluation and RS-24 uncoached pilot: defer as unbudgeted; any comparative benefit or onboarding time remains unmeasured.

## Identifier changes

- None. No template field or existing test ID renamed; templates remain drafts pending S4 import.

## Requests for other owners

- VT-01/04, 06 C-13 and I-29: require action-specific structured `decision`, canonical hash equality and negative missing/changed-field tests; remove attachment alternative and assert oversized or truncated inputs fail closed.
- VT-02/03 and certification: 08 allocate distinct non-overlapping harness/red, up-to-2 h runtime certification and fallback-preflight blocks; reforecast expiry/revision implementation and E2E-10/11 execution separately, cut optional scope to fit and record actual timings.
- VT-08/12: 06 layout and CI explicitly include and lint/import `labquorum-core.template.yaml`; E2E setup and 08 S1/S4 explicitly add Maya to the private room and verify she can post before separate identity/approval tests.
- VT-05: 06 I-31 assert dated retraction wording, I-27 assert safe HTML rendering, and I-30 assert outbound public-input policy, or 07 L14/X10/D08 mark manual and unverified.
- VT-10/RS-22: 06 I-16, if release packet ships, unpack in clean environment, execute included reproduction command, compare every reported number to declared tolerances, and assert failed/rejected runs and exclusions in timeline.
- VN-03/04/06: 06 U-C02 reject subset/negation automatic verification; U-S02 distinguish copyedit, computational change and critical scientific change; 6.5 pair unchanged/permuted, withdrawn and reversed fixtures with independent goldens, report k/n and exclude N/A CI and p.
- VP-01/02/03/09 and VN-07: 04 explicitly request 60 minutes within 14:00-17:00 and alternative 15:45-16:45; drop mandatory inventory hold/order, give stale-only and booking-only cuts, and replace sub-inhibitory with illustrative concentrations.
- VT-09: 08 S0 use `https://github.com/sandbox-quantum/switch/blob/main/docs/official/deploy/self-host.md`; do not mark fallback ready until pinned artifacts, health command, bridge and timed proof are recorded.

## Open questions

- The pinned live Switch/Claude tuple, effective settings, per-request cards, oversized rejection and clean import have not been tested; no runtime certification is claimed.
- No self-host image digest, health endpoint or working Compose command has been measured; Path B is unavailable until independently verified.
- 2 h certification is an estimate requiring schedule-owner reforecast; projected slack is not yet reliable because the current schedule overlaps work.
