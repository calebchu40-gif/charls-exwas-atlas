# Wave 3 Blood weight target and estimand review (2026-10-30)

## Decision supported by official documentation

The CHARLS 2015 Blood Data Release Note states that CHARLS releases only cross-sectional blood weights for Wave 3 because a panel blood weight depends on the analysis purpose. `Blood_weight` is constructed from the individual cross-sectional weight and a logistic response model for blood collection, with the blood-response inverse-probability factor capped at the 99th percentile. The 2015 Codebook labels the field “Blood Weight with Household and Individual Response Adjustment.”

The same release note defines the blood collection target as all Wave 3 interviewees and separately identifies the cross-sectional subset. It reports 13,420 blood responders overall, including 13,013 cross-sectional responders; the Codebook lists 13,013 observed `Blood_weight` values. A protected ID-only reconciliation for this project found positive `Blood_weight` records in the official `Sample_Infor.crosssection==1` domain. This supports the released weight's cross-sectional scope and does not create a longitudinal blood weight.

## Proposed Wave 3 blood association target

For a Wave 3 cross-sectional blood association, define the initial survey frame by official `Sample_Infor`, then apply `crosssection==1`, blood-module participation, and the applicable valid positive `Blood_weight`. Each exposure–outcome pair then has its own complete-data subset; its final analytic denominator must be reported from the protected analysis and cannot be inferred from the Codebook's overall blood counts. If an age domain is chosen, first construct and validate age on the complete design frame, then use a design-valid domain estimator rather than dropping rows before design construction.

Do not substitute `INDV_weight_ad2`, `Biomarker_weight`, Wave 1 `bloodweight`, or an analyst-created panel weight for the official Wave 3 blood-response weight. Do not use `Blood_weight` to claim a longitudinal or within-person effect. A panel blood estimand would need a separately justified response/attrition model and independent review; it is outside this first cross-sectional atlas release.

## What remains unresolved

This source review closes the documentation question “what population does the released Wave 3 blood weight target?” It does not by itself freeze the exact exposure–phenotype estimand, certify all row-level weight values, validate age eligibility, determine the full sampling variance (PSU/strata/stage structure), settle fasting/top-coding/missing-outcome rules, or authorize modeling. Pairwise complete-case denominators, any nonresponse assumptions beyond the published weight, multiplicity family, and disclosure release also remain to be specified and reviewed.

## Sources

- `sources_official/CHARLS_2015_Blood_Release_Note.pdf`, sections 4–5 (“Response Rate” and “Weights”).
- `sources_official/CHARLS_2015_Codebook.pdf`, “Blood Data” (`Blood_weight`) and “Sample Information” (`crosssection`).
- `audit/wave3_official_blood_merge_pipeline_2026-10-27.md` for protected frame linkage and merge safeguards.
- [CHARLS 2015 Blood Data Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf).
- [CHARLS 2015 data page](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html).
