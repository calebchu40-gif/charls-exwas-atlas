# Wave 1 post-pilot scale-up implementation gap (2026-10-27)

## Finding

The current protected script `scripts/run_2011_household_environment_blood_extension.py` is an exploratory K=105 runner for `i017` running-water status plus the six `i022` cooking-fuel contrasts across 15 non-cystatin-C blood phenotypes. Its separate M1/M2 q-values are within that exploratory family only. The associated gate in `scripts/require_verified_wave1_frame.py` and `audit/templates/wave1_household_environment_readiness.template.json` is keyed to `#household-environment-K105` and requires pilot success review.

The approved scale-up route in `audit/pilot_followup_execution_plan_2026-10-26.md` is larger and is not implemented by that script:

- **K=150 primary block:** 10 coefficients (running water `i017`: 1; main cooking fuel `i022`: 6; electricity availability `i016`: 1; gas supply `i019`: 1; heating availability `i020`: 1) × 15 blood phenotypes.
- **K=90 routed heating subdomain:** 6 `i021` fuel contrasts × 15 phenotypes among respondents routed to that item after `i020=No`; this is a separate target domain.

The three additional household fields `i016`, `i019`, and `i020` are not present in the existing K=105 runner. The readiness template is an empty planning template only and is not an approval.

## Required implementation before scale-up

1. Authenticate/rebuild the exact official Wave 1 frame and close the source, denominator, age-domain, weight, final-PSU, and variance review gates.
2. Against the authenticated release, review the value storage, response codes, household-to-person linkage, routed denominator, structural missingness and valid target weight for `i016`, `i019`, `i020`, and `i021`. Do not infer category codes or convert structural skips into a reference category.
3. Freeze one primary model and covariate set after estimand/DAG review. Preserve M0 and alternative adjustments as sensitivity/descriptive outputs, not separate discovery opportunities by default.
4. Implement a dedicated protected local scale-up runner with distinct K=150 and K=90 complete hypothesis registers. Include every planned contrast, mark non-estimable pairs instead of dropping them, and retain the K=90 route condition as an explicit domain.
5. Add an analysis-plan gate for `charls_2011_household_environment_scaleup_v1_K150_K90`, bound to current source manifest ID, prepared-table hash, the pilot success/reproducibility review, and exact hashes of the frozen plan documents. Do not point the K=150/K=90 template at the existing K=105 script.
6. Treat batch-level adjustments as provisional. Once the complete atlas primary test set is frozen and run, recompute the final global BY/Bonferroni family; then conduct independent methods and CHARLS disclosure reviews before any website release.

## Current status

No new data were read, no K=150/K=90 model was run, and no script was presented as a completed scale-up. The protected Wave 1 readiness validator now recognizes `household_environment_scaleup` as a distinct plan and binds approval to the scale-up template, DAG, 240-row hypothesis register, scale-up gap record, source/design plans, and multiplicity decisions. This closes the approval-routing gap only; there is still no K=150/K=90 runner, no approved analysis model, and no scale-up approval record. With official inputs still missing, release-specific coding, denominators, and actual fitting must wait for the authorized Wave 1 files and passed gates.
