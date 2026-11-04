## Verdict

**9.1/10. Pass:** no open blocker or high finding in this scope. Rubric, 2.5 points each: prior-art attribution and bounded novelty 2.4; market evidence and citations 2.2; decision rationale and sensitivity 2.2; traceability and actionable validation 2.3. This scores the plan, not an implemented product or earned judging score.

The three biggest remaining problems are: (1) the market file omits one hour of mandatory certification and its attack cases, VN-01; (2) the funded booking-only demonstration is an application of existing patterns and the more distinctive correction-to-release loop is unfunded; and (3) user demand and comparative advantage remain unverified, with the comparison also unfunded. The last two are explicitly acknowledged, so they do not fail this plan-level review. To strengthen a 9+ plan, make the exact edit in VN-01; no additional edit is required to reach 9 under the stated scoring rule. Do not claim the stretch distinction or a practical advantage until their existing conditions are met.

The requested round4/research.md and round4/market.md do not exist in this checkout. The immediate previous review is round4/v-novelty.md, which carries forward those reviews. All three of its findings are checked below, including its high and both medium/low findings. The round-three citation ledger is the baseline for unchanged claims, not proof of continued availability; the changed RSpace claim was rechecked against the vendor. No missing file is treated as evidence.

## Previous findings status

| ID | Status | Evidence quote or location |
|---|---|---|
| VN-02 (round 4), MK-29 | resolved | 01 section 1.2: "Academic managed Team EUR5,000 or USD6,000 minimum annual subscription; seat count and additional-user tariffs UNVERIFIED." The vendor page supports the revised minimum. |
| VN-01 (round 4) | resolved | 10 Method: "illustrative weights express the solo builder’s preferences" and "Hard certification gates override weighted totals"; High-impact sensitivity bounds gives low/base/high scores, alternative 100% weights, flip thresholds and provisional choices for all four specified decisions. |
| VN-03 (round 4) | resolved | 01 opening: "The dated citation ledger assessed the 145 occurrences then present; changed claims require a fresh check, and inaccessible or unsupported details are individually UNVERIFIED." |

## New findings

| ID | Severity | File and section | What is wrong | Evidence | Exact fix | Reasoning metric |
|---|---|---|---|---|---|---|
| VN-01 | medium | 01 section 1.4, Bounded authority | Certification duration and scope are stale after six attack/control cases were added. A reader following this procedure could omit mandatory tests or reserve too little time. | 01 specifies 120 minutes in five blocks; 08 section 8.2 and 03 section 3.2 specify 180 minutes including 60 minutes for I-36 through I-41 and legitimate controls. 06 requires all six and controls to pass. | Change 120 to 180 minutes; add the 60-minute I-36 through I-41 attack and legitimate-control block and state all cases must pass within the cap. Retain proposal-only on failure or timeout. | 25 + 35 + 25 + 20 + 15 = 120; adding 60 = 180 minutes, a 50% increase. |

## Verified facts

- [RSpace pricing](https://www.researchspace.com/pricing) currently lists the managed academic Team minimum annual subscription as EUR5,000 / USD6,000; the displayed page does not establish the removed 15-seat or additional-user terms. This is the only changed external claim identified in the round-four novelty fix log.
- The prior [citation ledger](../round3/citations.md) records 145 URL occurrences assessed, with one inaccessible source and four partial rows. This review relies on that dated audit for unchanged citations; it does not independently assert that every URL still resolves. The related-work section contains 14 external link occurrences, as stated. Its qualified claims distinguish prior scientific-agent teams, citation checks and provenance from the proposed, unproven combination.
- Independently checked all 39 decision sections: 78 weighted totals match their stated scores, all 39 criterion-weight sets sum to 100% and match both formulas, and all 39 margins are correct. The four changed sensitivity rows also calculate correctly: alternative weights give approval 7.25 versus 6.00, agents 7.20 versus 6.25, database 7.50 versus 7.50, and room 7.30 versus 7.00. The stated one-variable flip thresholds 3.44, 2.875, 0.667 and 1.5 are correct rounding of the respective margins divided by their criterion weights. These subjective sensitivity examples do not establish empirical robustness.
- README scenario totals are correct: 24 + 16.25 + 13.75 + 14 = 68; 24 + 17.5 + 16.25 + 15 = 72.75; 27 + 20 + 18.75 + 17 = 82.75. The plan labels them conditional judgments, not earned scores.
- Other scoped arithmetic: 99/176 = 56.25%; 84 - 62 = 22 percentage points; 155 x 0.21 = 32.55, approximately 33; 10 x 2 x 30 seconds = 10 minutes; 10 x $35 = $350; 12 x $50 = $600; 12 x 2 x $25 = $600; one fewer of five agents = 20%; and 23:59 minus 19:00 = 4 hours 59 minutes. The full pilot bounds add to 1.25-1.75 hours. These are arithmetic checks, not independent validation of unchanged source claims.
