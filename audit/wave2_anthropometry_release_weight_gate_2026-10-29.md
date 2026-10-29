# Wave 2 anthropometry release and biomarker-weight gate review

**Date:** 2026-10-29  
**Status:** official documentation supports the Wave 2 module and a cross-sectional weight candidate; individual-release provenance, pair eligibility, age domain and variance remain open. This memo does not authorize association fitting.

## Evidence reviewed

- CHARLS Wave 2 Release Note, VersionID 20151118: its released-module table identifies `Biomarker.dta` as anthropometric measurements. The note separately says `Biomarker_weight` is cross-sectional and adjusts for household/individual nonresponse through an inverse predicted probability of responding in the Biomarker module, capped at the 99th percentile. It explicitly offers no longitudinal biomarker weight.
- Official Wave 2 Biomarker Questionnaire and Codebook document these anthropometric measurement fields: `qi002` standing height (cm), `qj002` arm length (cm), `qk002` knee height (cm), `ql002` body weight (kg), and `qm002` waist circumference (cm). These are metadata and instrument fields, not participant-level coverage or eligibility evidence. Route, measurement-context and noncompletion fields remain separate; do not treat routed/noncompletion codes as measured values.
- The protected Wave 2 intake currently contains the official PSU and Weights releases, but no Wave 2 All Data archive was found in that designated intake. A previously prepared person-level table exists in protected local storage, but its current manifest does not bind it to an authenticated official All Data archive hash/version. It therefore does not close source provenance or released-file-header review. No participant values, IDs or estimates were read for this memo.

## Analysis implication

For a **Wave 2 cross-sectional** candidate pair where a source field is confirmed to come from `Biomarker.dta`, `Biomarker_weight` is the source-grounded starting weight because it accounts for response to that module. The analysis frame must also apply the official `crosssection` flag, confirm the field's actual release/module placement and valid route, and define pair-specific eligibility and missingness. This weight only documents the Biomarker response adjustment; it does not automatically correct nonresponse in a separate exposure module or establish complete pair coverage. Do not substitute `INDV_weight_ad2` without a target-specific rationale.

Do not use `Biomarker_weight` for a longitudinal/within-person estimand: the Wave 2 release explicitly provides no longitudinal biomarker weight. Baseline-to-Wave-2 identifier transformation is needed only for actual baseline linkage/panel estimands; a wave-specific cross-sectional analysis should use the Wave 2 identifiers and sample definition.

## Still required before a Wave 2 model

1. Intake the authorized Wave 2 All Data release (or locate its existing official original in the designated protected intake), then verify source identity, release version, checksums, archive members and the relevant Stata headers without reading participant values.
2. Bind the actual Biomarker fields, PSU/Weights files and `crosssection` membership to the source-authenticated frame; reconcile module response, all pair components, age-domain and target definition.
3. Resolve the Wave 2 variance specification, including the proper PSU/strata representation, singleton policy and whether any approximation is acceptable, with independent survey-methods review. The Wave 2 PSU release currently documents geography/community descriptors but no explicit county-stage or variance-stratum key.
4. Freeze the Wave 2 estimand, adjustment set, outcome validity/transform rules and complete hypothesis family before fitting. Include the family-wide multiplicity plan and a disclosure review before any public aggregate is released.

## Official sources

- [CHARLS Wave 2 Release Note, VersionID 20151118](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2013-charls-wave2/application/CHARLS_Wave2_Release_Note.pdf)
- [CHARLS Wave 2 official release page](https://charls.charlsdata.com/pages/Data/2013-charls-wave2/en.html)
- Wave 2 Biomarker Questionnaire and Codebook are the official archived project sources under `sources_official/`; the questionnaire/source crosswalk and measurement status are summarized in [`objective_measurement_crosswalk_v1.csv`](objective_measurement_crosswalk_v1.csv).
