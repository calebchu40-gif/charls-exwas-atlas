# Wave 1 pilot pair-availability audit

**Date:** 2026-10-30  
**Status:** Protected aggregate QA completed; this is not a model run or methods approval.

## Scope

The audit reconciles the registered 105-coefficient tranche (`i017` Yes/No and six `i022` fuel-versus-electricity contrasts across the 15 conventional Wave 1 blood outcomes) against the source-verified person table, official Blood file, positive `bloodweight`, and hash-bound provisional age intervals. It evaluates the complete blood target, the user-selected lower-bound 45+ domain, and the upper-bound 45+ age sensitivity.

For each coefficient/domain, the private report records the exposure and reference group availability, outcome nonmissingness, parent-community key coverage, and whether the fasting-code gate is unresolved. It does not write respondent IDs or outcome values. The exact pair-level counts and all file fingerprints remain only in the owner-only server QA directory at `private/qa_outputs/wave1_pilot_pair_eligibility_20261030_private.json`.

## Interpretation limits

- A positive bloodweight, nonmissing outcome, and observed community key establish only data availability. They do not establish eligibility, valid measurement, a final model N, or valid design-based inference.
- No analyte-specific valid-value cutoff was applied. The Blood Users' Guide assay ranges are not used as sample filters, and no sample-distribution-derived trimming or transformation was performed.
- Glucose and triglyceride coefficients remain blocked because the Wave 1 `qc1_va003` numeric fasting mapping remains unresolved in the reviewed official documentation.
- The age intervals are still method-unreviewed candidates. Domain counts are diagnostic only and do not approve the 45+ estimand.
- The parent `communityID` key is not a reconstruction of split final PSUs or the full CHARLS stratified multistage variance. The user-selected Taylor option remains approximate and subject to the independent methods-review gate.

## Reproducibility and release boundary

The script verifies current source provenance and age-candidate SHA-256 before reading the selected fields. It binds the report to the prepared table, Blood file, age candidate, registry, and biomarker crosswalk hashes. The report is mode `600` on the private server. The public repository contains only the audit implementation and this method note; it contains no participant-level input, pair counts, coefficients, or results. No association model was fitted.
