# Wave 1 K150/K90 registry source and route reconciliation

**Date:** 2026-10-29  
**Scope:** Official questionnaire/Codebook metadata and protected source/header metadata only. No participant responses or private analysis outputs were read.

## Source authentication and field-key checks

- The protected Wave 1 intake manifest records the user's confirmation of authorized account downloads and a metadata-only identity review for official All Data, PSU, Weight and Blood sources. The exact hashes and private manifest remain in the protected workspace.
- The official baseline questionnaire/Codebook review maps the K150 environmental items to electricity (`i016`), running water (`i017`), coal/natural gas supply (`i019`), heating availability (`i020`) and cooking fuel (`i022`); the K90 route uses heating source (`i021`). The All Data archive contains the housing-characteristics module.
- Header-only metadata review found all six candidate environment field keys in the prepared Wave 1 table. A separate metadata-only review found all 15 candidate phenotype field keys in the official Blood file header. No respondent rows or values were read.
- Accordingly, the 240-row hypothesis register now distinguishes verified source identity/field-key presence from still-unreviewed response values, household-to-person linkage, item-level eligibility, missing/special-code handling, and outcome validity/transform rules. All 240 rows remain `planned_not_approved`; no analysis status was advanced.

## Route interpretation retained in the registry

- For the 2011 heating items, the questionnaire routes `i020=1` (Yes) past `i021` to cooking fuel; `i020=2` (No) proceeds to `i021`. Thus the K90 heating-energy comparisons apply only to the No-response route. This is not a full-sample heating-source estimand. Preserve the route explicitly and review the target/subpopulation before analysis.
- The 2011 cooking-fuel question has no explicit no-cooking answer. A blank must not be recoded as a no-cooking category; release-level eligibility and missingness still need review.
- These questionnaire routes support only the coded response structure. They do not establish that household-reported fuel or utility access measures individual exposure dose.

## Blood crosswalk status correction

A separate metadata-only check matched all 17 Wave 1 field keys in the public blood crosswalk (15 planned shared outcomes, cystatin C, and fasting metadata) to the protected official Blood-file header. The crosswalk's older “local directory checked; combine with the original Blood file and bloodweight” wording was replaced with the current source-identity/header status. This does not resolve the age-stratified cystatin C selection, field-specific weight applicability, analytical valid-value limits, special codes, transformations, or Wave 1 fasting response codes.

## Current gates and next steps

The source-identity gate for the Wave 1 packages is satisfied, and the candidate field keys are present. The formal analysis gate remains closed pending target-frame/age-domain validation, module-specific blood-weight applicability, respondent-to-final-PSU/strata variance review, unresolved fasting-code and outcome-validity rules, frozen analysis plan, and independent methods review. The registry's code/route corrections do not authorize model fitting or public release.

Official project source reviews: `audit/housing_context_source_review_2026-10-24.md`, `audit/housing_fuel_source_review_2026-10-24.md`, `audit/wave1_outcome_scale_readiness_2026-10-29.md`, and `audit/wave1_variance_estimator_decision_matrix_2026-10-29.md`. Official text sources are the 2011 baseline questionnaire/Codebook and Blood User Guide in `sources_official/`.
