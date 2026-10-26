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
4. **Implemented:** a dedicated protected local scale-up runner and complete K=150/K=90 hypothesis register. The runner retains the K=90 route condition as an explicit survey domain and outputs all planned contrasts, including non-estimable pairs.
5. **Implemented:** an analysis-plan gate for `charls_2011_household_environment_scaleup_v1_K150_K90`, bound to current source manifest ID, prepared-table hash, pilot success/reproducibility review, frozen configuration hash, and exact hashes of the plan/runner documents. It is separate from the K=105 route.
6. Treat batch-level adjustments as provisional. Once the complete atlas primary test set is frozen and run, recompute the final global BY/Bonferroni family; then conduct independent methods and CHARLS disclosure reviews before any website release.

## Current status

No new data were read and no K=150/K=90 model was run. The protected Wave 1 readiness validator recognizes `household_environment_scaleup` as a distinct plan and binds approval to the scale-up template, DAG, 240-row hypothesis register, metadata audit, runner source, source/design plans, and multiplicity decisions. A dedicated runner and protected model-configuration template now exist; the runner checks exact source/frame hashes, frozen target/frame/design/model/outcome transformations, and the passed pilot/reproducibility gate before importing data-reading dependencies. It preserves the full survey design and expresses age/route restrictions through the survey engine's domain mechanism. It supports the pinned `svy==0.35.0` Taylor path only and explicitly rejects unsupported replicate-weight designs. Both full-sample lonely-PSU handling and domain-singleton handling/reporting must be selected in the frozen configuration; the runner records the number of domain-singleton strata for each private pair diagnostic. These are software controls, not a scientific/methods approval. Official Wave 1 inputs are still missing, and no private configuration or scale-up approval record exists. Thus release-specific coding, denominators, design settings, fitting, and any public release remain blocked on authorized Wave 1 files and independent review.

## Metadata-only implementation progress (2026-10-27)

Added `scripts/audit_wave1_scaleup_metadata_readiness.py` and wired it into the repository validation workflow. It cross-checks all planned K=150/K=90 exposure-code/label contrasts against the tracked 2011 Codebook extraction, all 15 outcome field/unit candidates against the biomarker crosswalk, and the `i020=No` route restriction against the reviewed questionnaire-routing note. It also enforces that the model and every planned hypothesis remain unapproved. This closes a metadata consistency check before any future implementation; it does **not** authenticate an exact authorized release, validate respondent-level household linkage, freeze a model, estimate associations, or satisfy source/design gates. The script uses public/tracked metadata only.
