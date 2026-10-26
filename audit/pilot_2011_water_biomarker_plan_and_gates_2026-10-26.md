# 2011 CHARLS water-access × blood-biomarker pilot: plan and release gates

Date: 2026-10-26. This file records the pilot specification and execution state. It contains no participant-level records, pairwise sample counts, coefficients, or p-values. The actual private outputs stay under `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\pilot_2011_water_blood` and are not copied into the repository, GitHub, or Pages.

## Why this is a pilot

The public atlas remains a metadata catalogue; catalogue co-availability is not an analysis N. This first model run is a protected local workflow pilot intended to check that CHARLS fields, the blood-response weight, a candidate PSU, covariate handling, survey-engine output, and multiplicity correction can be connected end to end. It is not a formal, release-ready atlas result and is not displayed on the public site.

The pilot was chosen from the existing CHARLS field audits: Wave 1 has a baseline household running-water item (`i017`) and the separate blood-assay module, while the prepared Wave 1 table has a blood weight. Wave 3 blood assays are a separate official file that is not currently present locally; Wave 2 lacks its official sample flags in the prepared table. The 2011 pilot therefore avoids pooling waves or substituting a general interview weight for the blood-response weight.

## Frozen primary pilot specification

- **Wave and target:** 2011 baseline household-resident respondents aged 45 or older, with a valid `i017` response and positive `bloodweight`. This is a single-wave cross-sectional target, not a longitudinal estimate.
- **Exposure:** `i017`, “Does your residence have running water?”; code 1 = Yes and 2 = No. The contrast is Yes versus No. This is a household access proxy, not an individual water-quality or contaminant measurement.
- **Phenotypes:** the 15 Wave 1 blood analytes in the project crosswalk except cystatin C. Cystatin C is excluded because its age-stratified assay selection and corresponding selection-weight applicability have not been established. Collection/processing metadata are not treated as analytes.
- **M0:** exposure-only descriptive model.
- **M1 primary:** exposure + centered age + centered age squared + sex. Age is the existing provisional Harmonized CHARLS D-derived covariate; it is explicitly not represented as a raw CHARLS field or a fully re-derived official age value. The model uses an outcome-specific bloodweight-weighted SD scale and retains estimates on the reported assay unit scale.
- **M1 multiplicity:** the 15 exposure–phenotype hypotheses form a fixed family (`K=15`); report Benjamini–Yekutieli and Bonferroni adjustments. M0 is descriptive and is not a discovery family.
- **M2 sensitivity:** an additional model adds NBS urban/rural context and grouped 2011 education. It is a sensitivity analysis, not a second primary discovery family. The detailed grouping was set for this exploratory sensitivity after the initial M1 run and is not a preregistered confirmatory specification.
- **Missingness:** only the documented `i017` response codes 1/2 are valid. Structural nonresponse is not recoded as No. Negative assay values are treated as invalid; no distribution-based trimming or winsorization is used. Pair-specific complete cases are selected by the survey engine while retaining the full design frame.

## Survey design status and limits

- **Weight:** `bloodweight` is the Wave 1 blood-response weight candidate described in the CHARLS blood documentation. The current prepared table has a recorded SHA-256, but its original official archive identity/checksum is not present in the current local protected workspace. Weight provenance must be re-verified against the exact official source release before a result can be promoted.
- **PSU:** the protected local `psu.dta` has a unique `communityID` key, and every Wave 1 respondent community key maps to it. The pilot now checks this mapping on every run and records the local PSU-map checksum. This verifies local key integrity, not the archive's release identity. The official sample description notes 30 large communities split into subareas; the local community questionnaire includes a separate `sub_commuID` for some rows, but respondent records do not carry that key. Whether the released `communityID` already represents the final sampled PSU in every split case remains to be confirmed against the exact release/source documentation.
- **Variance:** the pilot uses an explicitly labelled with-replacement, unstratified PSU Taylor approximation with the blood-response weight. It does not represent CHARLS implicit stratification or prove full design-adjusted variance. `province`, `city`, `urban_nbs`, and `areatype` are not fabricated into a stratum; `urban_nbs` in M2 is only a contextual adjustment covariate.
- **Interpretation:** all estimates are exploratory, cross-sectional associations. A finite estimate, small p-value, or engine completion does not close the source/design gate, complete the pair-level estimability review, establish causality, or authorize public release.

## Execution state

`scripts/run_2011_water_blood_pilot.py` reads only the necessary fields from the private prepared Wave 1 table and private age candidate. It removes participant IDs before constructing the analysis frame, uses the pinned `svy` engine, and writes all outputs only to the protected local directory. The run produced M0, M1, and M2 rows for the 15-analyte pilot; the M1 family returned finite model statistics for all predeclared pairs. A manual weighted least-squares/PSU-score calculation was compared with the survey engine for the M1 pairs. These facts validate the local software path only; they do not make any estimate release-ready.

The private result file includes raw and outcome-SD scales, model N, approximate design degrees of freedom, Kish effective N, model warnings, and multiplicity adjustments. The protected pair QA file contains pair-specific support diagnostics. Neither private output is tracked by Git.

## Next steps

1. Recover or reacquire the exact official Wave 1 source package in the authorized account, verify its release identity/checksum, and reproduce the prepared table and blood-weight mapping. The local `psu.dta` key now passes the respondent-key integrity check, but this does not authenticate the archive/version.
2. Confirm from the exact release or CHARLS support documentation whether `communityID` in the respondent file identifies the final sampled PSU for the 30 split-community cases, and obtain a documented CHARLS variance recommendation. If no variance strata/replicate weights exist for the public release, retain the approximation label, obtain an independent survey-methods review, and keep any national inference appropriately qualified.
3. Complete pair-level estimability review and assess robustness to the M2 covariates, weight diagnostics, missingness, and outcome distributions. Do not select pairs based only on the p-values.
4. If the gates and pilot diagnostics pass, implement a wave-specific analysis configuration and sample-flow builder. Add further Wave 1 exposure families in batches, keeping the predeclared test family complete and applying BY/Bonferroni to the full primary family.
5. Then test a non-blood Wave 3/4 exposure–objective-phenotype family. Rebuild Wave 2 after recovering its official `crosssection`/`longitudinal` weight flags. Add 2015 blood markers only after the separate official Blood Data file and `Blood_weight` pass the protected intake gate.
6. Publish only reviewed, disclosure-approved aggregate results. Do not place CHARLS respondent-level data, row-level outputs, or private QA files in the website or repository.

## Sources

- CHARLS 2011 baseline user guide and official Wave 1 data page: [User's Guide](https://charls.pku.edu.cn/en/data/User2011.pdf), [Wave 1 release page](https://charls.pku.edu.cn/en/Data/a2011_CHARLS_Wave1__Baseline_.htm).
- CHARLS official sample design: [Sampling](https://charls.pku.edu.cn/en/About/Sample.htm).
- CHARLS 2011 blood collection and biomarker guidance: `sources_official/CHARLS_2011_Blood_User_Guide.pdf` in the project source inventory.
- Project-specific boundaries: [`survey_design_weight_review_v1.md`](survey_design_weight_review_v1.md), [`blood_biomarker_definition_review_v1.md`](blood_biomarker_definition_review_v1.md), [`data_preparation_plan_and_controls.md`](data_preparation_plan_and_controls.md), and [`nhanes_to_charls_implementation_contract_v1.md`](nhanes_to_charls_implementation_contract_v1.md).
