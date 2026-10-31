# Wave 3 Blood weight target and estimand review (2026-10-30)

## Execution update (2026-10-31)

The user-authorized 2015 cross-sectional blood analysis is complete. The project ran all 225 crosswalk-available housing-environment × blood-phenotype models using `Sample_Infor.crosssection`, positive official `Blood_weight`, an age-45+ domain, and pair-specific complete cases. Glucose and triglycerides were restricted to the official fasting code. The original 2015 questionnaire has a wave-specific route: `i020=1` proceeds to heating source `i021`; `i020=2` skips to cooking fuel. The main models use age and gender adjustment and WR Taylor variance clustered by `communityID`; official strata and the final split-community PSU map are not released, so this variance remains approximate. Results are a separate 2015 family and are not pooled with 2011.

The official 2015 crosswalk also identifies `bb001_w3_2` as a nominal current-residential-settlement measure with seven wave-specific categories. A separate 225-model sensitivity set added those categories without collapsing them into an analyst-defined urban/rural binary. All models fit; a private paired comparison found some coefficient movement relative to the age/sex main specification. The main family remains the registered age/sex specification, while settlement-adjusted estimates are retained as sensitivity results and are not in the public payload. Exact comparisons and QA remain on the private server. The reproducible runner is [`scripts/run_2015_household_environment_blood.py`](../scripts/run_2015_household_environment_blood.py).

## Decision supported by official documentation

The CHARLS 2015 Blood Data Release Note states that CHARLS releases only cross-sectional blood weights for Wave 3 because a panel blood weight depends on the analysis purpose. `Blood_weight` is constructed from the individual cross-sectional weight and a logistic response model for blood collection, with the blood-response inverse-probability factor capped at the 99th percentile. The 2015 Codebook labels the field “Blood Weight with Household and Individual Response Adjustment.”

The same release note defines the blood collection target as all Wave 3 interviewees and separately identifies the cross-sectional subset. It reports 13,420 blood responders overall, including 13,013 cross-sectional responders; the Codebook lists 13,013 observed `Blood_weight` values. A protected ID-only reconciliation for this project found positive `Blood_weight` records in the official `Sample_Infor.crosssection==1` domain. This supports the released weight's cross-sectional scope and does not create a longitudinal blood weight.

## Proposed Wave 3 blood association target

For a Wave 3 cross-sectional blood association, define the initial survey frame by official `Sample_Infor`, then apply `crosssection==1`, blood-module participation, and the applicable valid positive `Blood_weight`. Each exposure–outcome pair then has its own complete-data subset; its final analytic denominator must be reported from the protected analysis and cannot be inferred from the Codebook's overall blood counts. If an age domain is chosen, first construct and validate age on the complete design frame, then use a design-valid domain estimator rather than dropping rows before design construction.

Do not substitute `INDV_weight_ad2`, `Biomarker_weight`, Wave 1 `bloodweight`, or an analyst-created panel weight for the official Wave 3 blood-response weight. Do not use `Blood_weight` to claim a longitudinal or within-person effect. A panel blood estimand would need a separately justified response/attrition model and independent review; it is outside this first cross-sectional atlas release.

## Remaining methodological limitations

The registered 2015 family and its release checks are complete. The released materials still do not provide official strata or the final split-community PSU map, so the selected `communityID` WR Taylor variance is approximate. `Blood_weight` is the released blood-response weight; the fasting-restricted glucose and triglyceride analyses do not have a separately documented fasting-response weight in this release. Pairwise complete-case estimates therefore describe each fitted subset under the stated weighting, and do not claim correction for any additional fasting-substudy selection. Settlement categories are wave-specific and are not harmonized with Wave 1 `urban_nbs`. The 2015 family is kept separate from 2011, and later waves require their own source, eligibility, weight and variance review.

## Sources

- `sources_official/CHARLS_2015_Blood_Release_Note.pdf`, sections 4–5 (“Response Rate” and “Weights”).
- `sources_official/CHARLS_2015_Codebook.pdf`, “Blood Data” (`Blood_weight`) and “Sample Information” (`crosssection`).
- `audit/wave3_official_blood_merge_pipeline_2026-10-27.md` for protected frame linkage and merge safeguards.
- [CHARLS 2015 Blood Data Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf).
- [CHARLS 2015 data page](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html).
