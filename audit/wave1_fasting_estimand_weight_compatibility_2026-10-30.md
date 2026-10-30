# Wave 1 fasting-domain estimand and weight compatibility review

**Date:** 2026-10-30
**Status:** Source-based methods issue identified; no glucose/triglyceride model is approved.
**Scope:** Distinguish the official fasting-code mapping from the population represented by a fasting-only analysis. No participant-level fasting values, outcome values, or counts were read for this memo.

## Official source evidence

1. The CHARLS 2011 Blood Users’ Guide says the released `bloodweight` adjusts for household and individual nonresponse and nonparticipation in blood collection. It separately notes that some collected blood samples were non-fasting (approximately 8% in the guide’s report) and warns that non-fasting glucose can be higher. The guide does not document an additional probability-of-fasting or fasting-response correction. This does **not** prove that no such adjustment exists elsewhere; it means we cannot assume `bloodweight` supplies it without an authoritative source. [CHARLS Blood Users’ Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)
2. The official 2011 Fieldwork Plan Appendix 2 and the Blood header establish `qc1_va003`: 1=fasting, 2=not fasting. The code mapping does not state how fasting status entered the weight construction. [Official 2011 documentation page](https://charls.pku.edu.cn/wd/a2011nqgjxdc.htm)
3. As a methods comparator only, CDC’s NHANES documentation says fasting subsample weights incorporate the additional subsampling and nonresponse and differ from the full examination weights. This NHANES rule is **not transferable** to CHARLS; it demonstrates why a fasting domain cannot automatically inherit the full blood-sample weight. [NHANES subsample-weight notes](https://wwwn.cdc.gov/nchs/nhanes/search/subsample_weights.aspx), [NHANES weighting tutorial](https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx)
4. Stata’s survey manual explains that a domain/subpopulation estimator should retain the full survey design with non-domain observations represented as outside the domain; simply dropping them corresponds to a different design/variance estimator. Applying a domain method addresses variance calculation under the declared design, but does not by itself correct selection or create a weight for a domain that had additional nonresponse. [Stata Survey Data Reference Manual, subpopulation estimation](https://www.stata.com/manuals/svysubpopulationestimation.pdf)

## Consequence for the current candidate

The previous draft described `qc1_va003==1` as a possible primary restriction and the full blood sample with fasting covariate as a sensitivity. The source evidence now shows that this ordering cannot be assumed: `bloodweight` is documented for blood-collection participation, while no official source reviewed here establishes that it corrects selection into the fasting subset. Therefore the current materials must **not** label fasting-only as the primary population estimate or imply that weighting it with `bloodweight` restores representativeness.

The code mapping remains resolved, but the glucose and triglyceride coefficients remain blocked until an independent reviewer chooses and documents a defensible estimand/weight combination. At least these options should be reviewed before freezing:

| Option | Candidate estimand/handling | Weight/interpretation issue |
|---|---|---|
| A | All observed Wave 1 blood respondents; retain `bloodweight`; include fasting status as a pre-specified measurement-condition covariate. Consider a pre-specified exposure-by-fasting interaction or stratified descriptive sensitivity only if scientifically justified. | Targets the weighted blood-sample population more directly, but a covariate may not remove all fasting-related measurement differences; interaction changes the hypothesis family and needs its own frozen plan. |
| B | Restrict to fasting blood respondents; analyze as a fasting-status domain while keeping the full design object for variance. | The resulting estimate is conditional on observed fasting status. Do not claim it represents the full CHARLS blood target unless a valid fasting-selection adjustment/weight is documented. Domain variance handling alone is insufficient. |
| C | If the reviewer concludes no defensible inferential weight/estimand exists for the fasting-sensitive analyte, retain the hypotheses but report them as not estimated or descriptive-only under a separately approved plan. | Preserves the registered family and avoids overstating population inference.

None of these options has been selected or frozen. The exact option must be reconciled with the user-selected approximate `communityID`/unstratified WR Taylor variance plan, the 45+ age domain, nonresponse/complete-case handling, and the K=240 hypothesis-family plan. Do not infer a fasting-response weight from the observed fasted fraction, and do not use outcome associations or p-values to choose an option.

## Required review questions

- Does any official CHARLS source document that `bloodweight` adjusts nonparticipation in fasting specifically, or is the target simply the blood-collection respondent population?
- What scientific population is intended for glucose/TG: all blood respondents with measurement condition modeled, or the observed fasting subset?
- If the fasting domain is used, what target does its weighted estimate represent, and can the weight support that target?
- Should fasting status be a covariate, an effect modifier, or only a sensitivity restriction? What is the corresponding estimand and multiplicity plan?
- How should the age-45+ domain be nested with fasting status while retaining the full design sample for variance estimation?

Until this review is signed against the current draft hashes, keep all 14 fasting-sensitive coefficients registered but blocked.

## 2026-10-31 AI-assisted review: proposed review priority (not frozen)

An independent AI document review found the all-blood-sample candidate more defensible as the primary estimand than a fasting-only primary, because CHARLS collected non-fasting specimens and describes `bloodweight` as a blood-collection response weight. It recommended submitting this concrete proposal to the independent methods reviewer:

1. Define the primary glucose/TG target as all observed Wave 1 Blood records with finite positive `bloodweight`, nested within the otherwise frozen age domain.
2. Retain `bloodweight` and include the source-supported `qc1_va003` fasting-status main effect (1/2) as a pre-specified measurement-condition covariate for glucose/TG. Do not add an exposure-by-fasting coefficient to the primary K=240 family; that would change the hypothesis family and estimand.
3. Keep fasting-only analysis as a conditional-domain sensitivity or descriptive check, using the complete survey object for the provisional domain variance, and do not claim that it represents the broader blood target without independent support for the selection/weight assumptions.
4. Keep all 14 hypotheses blocked until the reviewer approves the estimand, handling of missing/other fasting codes, the no-interaction primary specification, finite-value outcome rule, Option A variance caveat, support criteria and complete hash-bound family plan.

This is an AI-generated recommendation from source/method documents, not a signed independent methods decision and not permission to fit. It relies on bloodweight being applicable to the stated blood-response target and on the proposed fasting main-effect model matching the intended conditional association. It does not remove possible measurement error, fasting-related effect heterogeneity, or residual selection concerns. No fasting or biomarker observations were inspected for this recommendation.
