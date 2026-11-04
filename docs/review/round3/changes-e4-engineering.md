## Applied

- VT-01, EN-01/02/39 and VT-02/03 (round 2): 08 8.1-8.2 now allocates an independent 120-minute installed-runtime certification with steps, evidence, pass/fail and fallback; E2E retains its separate block. Forecast rises by 120 minutes to 40 h 10 min, with a 115-minute late block retained: 100 minutes defect slack and 15 minutes Insights retry.
- VT-02 and VT-12 (round 2): 08 S4 and 8.2 move the 30-minute two-person fixture after S0 and before S1/S3; both local personas must post. The old S4 allocation is removed.
- VP-04/JD-26: 08 S8 and 8.2 specify a 10-minute route decision, bounded 15-minute Insights retry, prior screenshot, uncertainty and core submission fallback.
- VP-05/JD-28: 08 8.2 drops the unfunded blog, preserving 45 minutes README and 30 minutes link audit.

- VT-04 / RS-05: 06 I-30 and 07 D08 defer scholarly outbound checks and remove the unsupported general privacy assertion; a future guard must test short model-generated private text. The existing architecture 3.4 explicitly says arbitrary model text is not tracked, so synthetic-only operation is not a proven classifier.

- VT-05: 06 E2E-15 explicitly requires zero commits both during outage and after restart in both expiry branches. Architecture wording needs the matching correction below.
- Catalogue audit: 187 unique test IDs, 120 edge rows and zero unresolved explicit edge test IDs; no IDs added or removed. Schedule rows sum to 2,410 minutes (40 h 10 min).

## Rejected

- VP-05: Optional blog is dropped rather than added to the 75-minute README/audit allocation; the proposed 90 minutes exceeds the entire block by 15 minutes before either mandatory task.
- RS-24: Full task pilot remains unfunded: the 1.25-1.75 h protocol cannot fit 100 minutes of defect slack while also reserving the possible 90-minute server preflight. Demand and usability remain unverified.

## Identifier changes

None. Existing IDs retained.

## Requests for other owners

- VT-03, template owner: In `templates/labquorum-core.template.yaml`, replace scout and analyst instructions that call `search_literature`, `register_dataset` or `dataset_profile` with: "Literature search and data analysis are unavailable in the booking-only baseline; say they are unavailable and do not attempt these tools." Ensure kickoff does not promise deferred capabilities. Update 02 2.2 to match. S4 cannot pass until the imported template has this scope.
- VT-05, architecture owner: In 03 3.10 replace the E2E-15 expectation "pending request is still pending" with "After restart, the ledger remains pending only if unexpired; otherwise lazy expiry occurs on read. No booking is committed in either branch, including during the outage."
- VT-01/02 and VP-04/05, integration owners: In README Numbers change "38 h 10 min including 1 h 55 min defect slack" to "40 h 10 min including 1 h 40 min defect slack and 15 min Insights retry". In 04 4.6 update Friday baseline and freeze to 20:15-22:15 and Sat 00:15; in 09 9.4 remove the 1.5-hour existing blog block and mark the blog unfunded. Coordinate 05 5.6-5.7 and 09 9.2 with the 17:45-18:00 bounded retry and form-supported screenshot route; if unconfirmed, preserve the prior timestamped screenshot, label Wispr submission uncertain and submit core on time.
- VP-03/JD-12, demo and submission owners: Add a timed proposal-only script and matching README/package showing the request, alternative and explicit unapproved/no-booking status, with an artifact link; omit decision, refusal, commit and stale claims unless observed.
- VP-02, README/submission owner: Separate booking-only, stale-detection and full-release scoring scenarios and independent gates; calculate subjective totals and synchronize README.
- VN-05, decision-record owner: Delete the stale instruction to reconcile conflicting U-C02 text; retain the adversarial identity tests.
- VT-04, architecture owner: In 03 3.4 mark scholarly calls and any provenance guard deferred in the booking baseline and avoid general private-text refusal claims, matching 06 I-30 and 07 D08.


## Open questions

- The authenticated Submit form and its screenshot route are unverified; S8 records acceptance or uncertainty. The [organizer page](https://www.wemakedevs.org/hackathons/switch) requests the scorecard.
- Installed Switch runtime behavior and all duration estimates remain unverified until the scheduled procedures run. The pinned source snapshot is not a substitute for certification; the Switch documentation fetch returned an access error.
- `url-check.md` was absent in this workspace; `citations.md` was in progress at final inspection; its two 06 findings support the existing SQLite and Wilson citations and require no correction. Integrator should apply any later corrections.

Primary-source resolution: [NIST Wilson method](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm) supports the existing 5/5 interval under the stated binomial assumptions; the [event page](https://www.wemakedevs.org/hackathons/switch) requests a scorecard but does not verify a form route. The architecture states it cannot track arbitrary model text; therefore I-30 does not assert a general guard.

