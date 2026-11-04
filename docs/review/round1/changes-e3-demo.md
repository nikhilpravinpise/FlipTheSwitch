## Applied

- JD-01-16, JD-U1, RS-02, RS-06, SW-05/13/16/17/19/21: revised 04 sections 4.1-4.6 for coherent stock and well metadata, explicit latency and traceability, visible decision snapshot, honest branch-specific evidence and rehearsals. JD-03/04 also require fixture changes by other owners. Verified the renderer limit against [source](https://github.com/sandbox-quantum/switch/blob/8c2bd1dd8dd283770ea5b284c0fe593ce483e1f5/console/packages/agent-providers/src/mcp-approval.ts); the stricter 900-character target resolves RS-06 versus SW-05.

- JD-07, JD-18-25, JD-U4, RS-23, SW-07/17: updated 05 sections 5.1-5.7 for current Wispr limits, privacy, routing, build evidence, deadline and matched voice/type probe. Verified [free tier](https://docs.wisprflow.ai/articles/4760791189), [Insights](https://docs.wisprflow.ai/articles/8760230576-your-usage-tab-track-your-dictation-stats-in-wispr-flow), [MCP](https://docs.wisprflow.ai/articles/9551372685-connect-an-mcp-client-to-wispr-flow-remote-mcp-server) and [styles](https://docs.wisprflow.ai/articles/2368263928-how-to-setup-flow-styles).

- JD-06/08/10/12/14-17/19/25-28, JD-U2-U7, RS-02, SW-10/19: rewrote 09 sections 9.1-9.8 for form inspection, current event claims, reproducible README/blog, evidence-gated rubric, separately calculated reduced score and branch-aware risks. Verified [event prize/side-track terms](https://www.wemakedevs.org/hackathons/switch) and [DTA rubric](https://www.devtoolsacademy.com/hackathons/flip-the-switch); core prize count conflicts even within the main page and remains UNVERIFIED.

## Rejected

- JD-U7 as an unconditional activity: the 0.5-hour participant task is conditional on a reachable participant and a green core; no recruitment campaign or unsupported impact claim. Social cut capped at 0.25 hour. [Event](https://www.wemakedevs.org/hackathons/switch) publishes no odds or extra mobile bonus.
- JD-05 as an unconditional release promise: finalization is currently polish in 02; the shot is conditional on implementation and tests, otherwise explicitly reduced to stale detection. This prevents six-state proof from being asserted without evidence.
- Remote MCP as core work (JD-23/JD-U4): 0 core hours; <=0.5-hour stretch only after the package is green because the event requires build-by-voice and Insights, not MCP.

## Identifier changes

- No agent, profile, tool, test, edge-case or file ID renamed or removed. Corrected displayed project room from the erroneous `rao-proj-egcg` to template-generated `proj-egcg`; take rooms are `proj-egcg-take<N>`. Existing C5 remains C5; corrected concentration from 4 to 8 ug/mL.

## Requests for other owners

- JD-03/04, templates owner: in `docs/plan/templates/seed-data.md` and any seed/fixture text replace crystal violet `12 mL` with `22 mL` for the happy path; retain need `20 mL`, reorder threshold `25 mL`; replace `C5 (4 ug/mL, replicate 2)` with `C5 (8 ug/mL, replicate 2)`. Keep 12 mL as a separate rejection test; assert exactly one value differs between v1/v2.
- JD-05, product/architecture/testing owners: promote stale-release validation and a fresh PI decision to MVP if the full demo is desired; require CURRENT -> STALE -> denied release with zero effect -> new run -> new decision -> current release. Otherwise remove claims of blocked release and reapproval.
- SW-05/RS-06, architecture/testing owner: include canonical decision person, action, resource, interval/quantity, protocol/run fingerprint, revision and hash in commit arguments; compare to stored snapshot transactionally. Test mismatch rejection and rendered input without truncation, serialized target <900 characters.
- SW-07/JD-07, template owner: replace both batch-approval passages in `labquorum-lab.template.yaml` with: "Each binding request requires its own PI decision. Use Allow once. LabQuorum does not offer batch approval. Session-wide provider permission never authorizes another lab request." Preserve E2E-11.
- JD-06/17/18, README owner: replace "only the PI's click" and "every change to shared lab state" with "Bookings, purchase requests, protocol releases and final result releases require approval through the PI's Switch agent. Helpers can record observations and prepare drafts. The demonstrated card supports permitted clicks and typed answers." Replace 88/100 with 68.5 baseline and 82.75 only after all 09 evidence gates; replace 2,000-word free cap with warning above 2,000 and block above 5,000 on Windows defaults.
- JD-09, fixture owner: pin original/notice DOI relationship, retrieval dates and expected verdicts; place deliberate unresolved DOI separately from the valid-source allowlist and label unrelated retraction as planted. Never imply metadata proves claim support.
- SW-13/16/17/19/21, product, architecture, testing and schedule owners: use `proj-{project}`, three HQ roles, five project members; measure 3 + 5R actual sessions, serialize takes and require >=20% RAM headroom. Set and verify follow-ups off and no assignment for mention tests. Choose the gate by Thursday morning; for steward allocate 3-5 hours by cutting optional work and test wrong-person, replay, expiry and changed revision. Separate failed MCP launch from failed permission enforcement; gate-only CLI applies only to the former after enforcement passed.
- JD-14/19, schedule and README owners: clean room Saturday 09:00-10:30, final capture 10:30-12:30, edit 13:15-15:15; final Insights by 18:00, attach/check by 18:30, submit by 19:00. Skip core PR solo for this submission.

## Open questions

- The authenticated Submit form's fields, accepted formats and video limit require the builder's manual S8 inspection; simultaneous main/side awards and the conflicting core, blog and social prize counts remain unverified.
- `docs/review/round1/` contained four reviewer reports (judging, market, research, switch), not the five described in the brief; no engineering report was available to inspect.
- All proposed tests, recordings, source fixtures and user observations remain future work; no installed Switch/Wispr session was exercised in this editing pass.
