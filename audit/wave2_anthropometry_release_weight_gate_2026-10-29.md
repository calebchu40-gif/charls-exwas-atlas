# Wave 2 anthropometry release and biomarker-weight gate review

**Date:** 2026-10-29  
**Status:** official documentation and the protected official All Data bundle/header support the Wave 2 module and a cross-sectional weight candidate; pair eligibility, age domain and variance remain open. This memo does not authorize association fitting.

## Evidence reviewed

- CHARLS Wave 2 Release Note, VersionID 20151118: its released-module table identifies `Biomarker.dta` as anthropometric measurements. The note separately says `Biomarker_weight` is cross-sectional and adjusts for household/individual nonresponse through an inverse predicted probability of responding in the Biomarker module, capped at the 99th percentile. It explicitly offers no longitudinal biomarker weight.
- Official Wave 2 Biomarker Questionnaire and Codebook document these anthropometric measurement fields: `qi002` standing height (cm), `qj002` arm length (cm), `qk002` knee height (cm), `ql002` body weight (kg), and `qm002` waist circumference (cm). These are metadata and instrument fields, not participant-level coverage or eligibility evidence. Route, measurement-context and noncompletion fields remain separate; do not treat routed/noncompletion codes as measured values.
- The official Wave 2 All Data package (release item 321, 2015-11-18) was found in the protected private raw intake and matched the official release checksum recorded in the verified intake manifest. A protected Wave 2-specific intake copy was created. Metadata-only archive inspection found the expected `Biomarker.dta`, `Weights.dta`, `PSU.dta` and questionnaire modules. Metadata-only Stata-header review confirmed the five documented anthropometry fields in `Biomarker.dta`, the respondent keys, and the `crosssection`, `longitudinal` and `Biomarker_weight` fields in the bundled `Weights.dta`. This verifies archive provenance and headers only; it does not establish pair coverage, value validity, sample eligibility or variance design. No participant values, IDs or estimates were read.
- The earlier prepared person-level table remains unsuitable as source evidence by itself because its own manifest does not bind it to an authenticated archive. It must be rebuilt from the now-verified release bundle (or independently reconciled to it) before use.

## Analysis implication

For a **Wave 2 cross-sectional** candidate pair where a source field is confirmed to come from `Biomarker.dta`, `Biomarker_weight` is the source-grounded starting weight because it accounts for response to that module. The analysis frame must also apply the official `crosssection` flag, confirm the field's actual release/module placement and valid route, and define pair-specific eligibility and missingness. This weight only documents the Biomarker response adjustment; it does not automatically correct nonresponse in a separate exposure module or establish complete pair coverage. Do not substitute `INDV_weight_ad2` without a target-specific rationale.

Do not use `Biomarker_weight` for a longitudinal/within-person estimand: the Wave 2 release explicitly provides no longitudinal biomarker weight. Baseline-to-Wave-2 identifier transformation is needed only for actual baseline linkage/panel estimands; a wave-specific cross-sectional analysis should use the Wave 2 identifiers and sample definition.

## Still required before a Wave 2 model

1. **Completed, metadata-only:** verify the authorized Wave 2 All Data release identity/checksum, release version, archive members and relevant Stata headers in protected storage. No participant values were read.
2. Bind the actual Biomarker fields, PSU/Weights files and `crosssection` membership to the source-authenticated frame; reconcile module response, all pair components, age-domain and target definition.
3. Resolve the Wave 2 variance specification, including the proper PSU/strata representation, singleton policy and whether any approximation is acceptable, with independent survey-methods review. The Wave 2 PSU release currently documents geography/community descriptors but no explicit county-stage or variance-stratum key.
4. Freeze the Wave 2 estimand, adjustment set, outcome validity/transform rules and complete hypothesis family before fitting. Include the family-wide multiplicity plan and a disclosure review before any public aggregate is released.

## Official sources

- [CHARLS Wave 2 Release Note, VersionID 20151118](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2013-charls-wave2/application/CHARLS_Wave2_Release_Note.pdf)
- [CHARLS Wave 2 official release page](https://charls.charlsdata.com/pages/Data/2013-charls-wave2/en.html)
- Wave 2 Biomarker Questionnaire and Codebook are the official archived project sources under `sources_official/`; the questionnaire/source crosswalk and measurement status are summarized in [`objective_measurement_crosswalk_v1.csv`](objective_measurement_crosswalk_v1.csv).
