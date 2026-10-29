# Wave/module source, estimand, weight and gate crosswalk

**Date:** 2026-10-29  
**Status:** Metadata inventory for planning; not a frozen analysis specification or model authorization.

The companion CSV has one row for each wave and source module represented in `charls_atlas_candidate_fields_v0.csv`. It connects the catalog's candidate exposure, phenotype and covariate field roles to the wave-specific sample marker, a starting estimand, candidate weight fields, and open survey-design/runner gates. The reproducible builder is `scripts/build_wave_module_gate_crosswalk.py`.

## How to read it

- The generated 60 rows cover the source modules currently represented in the five-wave candidate-field catalog: 13 in 2011, 14 in 2013, 16 in 2015, 10 in 2018 and 7 in 2020.
- E/P/C counts are unique candidate source-variable names within a wave/module/role. A field can carry more than one candidate role. These counts are not eligible participants, complete-case sample sizes, tested pairs, or model counts.
- Sample markers and weights are wave-level starting points taken from the official target/weight review. They are repeated by module to make unresolved module-level decisions visible; repetition does not confirm that a particular field is eligible for that weight.
- Every module is marked as requiring module-specific weight and survey-design review. Wave 2–5 have no association runner in the repository. Wave 1's historical runner is exploratory, and the K150/K90 runner remains behind its frozen-configuration and readiness gates.
- Candidate catalog roles and concept mappings still require field-level source wording, route, valid-code, missingness and harmonization review before a pair can enter a frozen analysis.

## Rebuild

From the repository root, run:

```text
python scripts/build_wave_module_gate_crosswalk.py
```

The builder reads only the public candidate-field CSV in the repository. It does not open protected CHARLS microdata or private analysis outputs.

## Next review

Review modules against their official questionnaire routes and outcome instruments; establish which target and released weight apply to each field; then keep only compatible, source-reviewed exposure–phenotype candidates. A module enters a real-data run only after its survey design, analysis plan and independent review pass.
