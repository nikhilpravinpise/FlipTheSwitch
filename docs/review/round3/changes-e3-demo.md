## Applied

- VP-02, VP-06 (round 2), JD-17: 09 9.6 separates booking, stale and full-release scenarios, per-criterion gates and recalculated weighted totals.
- VP-03, JD-12: 09 9.3-9.5 supplies proposal-only README, blog and social wording with matching artifact.
- VP-04, JD-26: 05 5.6 and 09 9.2 bound capture and form verification, specify failure and uncertain side-track status.
- VP-05, JD-28: 09 9.4 drops the blog from the shared 75-minute block and supplies evidence-dependent titles only for separately funded work.
- VP-06: 09 9.2 distinguishes local test users from the event identity.
- VN-02: 09 9.5 marks the half-hour booking observation unfunded and distinguishes the 1.25-1.75-hour full pilot.
- Citation ledger: 05 citations checked; its entries are supported and require no correction.

- VP-01, VP-04 (round 2), JD-01, JD-02: 04 4.3 budgets 4 + 15 + 1 seconds for the opener and tests Switch comprehension.
- VP-03: 04 4.3 provides a timed proposal-only cut and verifiable artifact.
- VP-06: 04 4.4 distinguishes local test personas from the single event identity.
- VT-04 (round 2): 04 4.3 now fails closed on truncation, matching 03 3.2; the prior attachment exception conflicted with the reviewed rule and the Switch card formatter truncates JSON at 1,000 characters ([source](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/console/packages/agent-providers/src/mcp-approval.ts)).

## Rejected

- VP-05 optional blog allocation: reject adding 30 or 90 minutes to the funded schedule; 08 now reserves all 75 minutes for README (45) and link audit (30). Reconsider only after a separate block is allocated.

## Identifier changes

- New artifact path `docs/evidence/proposal-only/` holds the matching transcript or screenshot and status export; no existing test, agent or profile IDs renamed.

## Requests for other owners

- VP-02, README Numbers and first actions: replace the old three projections and "booking-only cut has no numerical projection" with: "Conditional booking-only, separately funded stale-detection and full-release projections are 68, 72.75 and 82.75 out of 100; no score is earned, and proposal-only has no projection. See [submission and risks](../../plan/09-submission-and-risks.md)."
- VP-03, README opening: add "If certification fails, the filmed workflow is proposal-only: an unapproved alternative and no committed booking, subject to the recorded status evidence." Link `docs/evidence/proposal-only/` only after the matching artifact exists.

## Open questions

- `docs/review/round3/url-check.md` is absent; no findings from that file could be inspected.
- Authenticated Submit form acceptance of the Wispr screenshot and the applicability of participation identity rules to local synthetic users remain unverified; seek organizer clarification as described in 09 9.2 and 9.8.
- Runtime certification, actual agent latency, artifact capture and the two-viewer test are unexecuted. The 120-minute certification and its fallback are specified in 08.
