# Wave 4/5 candidate-field header match review

**Date:** 2026-10-30  
**Method:** Compared public candidate catalog source-code names with the protected Wave 4/5 prepared-table Stata headers. The audit used header metadata only; it did not inspect respondent values, IDs, missingness, pairwise sample sizes, or associations. Outputs with detailed field names are kept in `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\wave4_wave5_catalog_header_audit_20261030`.

## Results

| Wave | Candidate role | Distinct catalog source codes | Present by exact name | Disposition |
| --- | --- | ---: | ---: | --- |
| 2018 | Exposure (E) | 1,716 | 1,716 | All names found in the prepared-table header |
| 2018 | Phenotype (P) | 468 | 468 | All names found in the prepared-table header |
| 2018 | Context/covariate (C) | 196 | 196 | All names found; one source code maps to more than one catalog field/module key |
| 2020 | Exposure (E) | 306 | 306 | All names found in the prepared-table header |
| 2020 | Phenotype (P) | 191 | 185 | The six omitted names are all from `Exit_Module` |
| 2020 | Context/covariate (C) | 47 | 46 | The one omitted name is from `Exit_Module` |

The 2020 omissions are expected: the builder deliberately keeps the decedent/proxy `Exit_Module` outside the one-row-per-respondent analytic table. The official Wave 5 User Guide lists Exit_Module as deceased-respondent information. Those fields require a mortality-specific denominator, time origin, follow-up/censoring rules, proxy-response interpretation, and survey design; they must not be paired as ordinary cross-sectional outcomes. Updated the metadata audit so these rows are labeled as a separate mortality estimand rather than a generic missing-field problem.

## Interpretation and next step

These are **code-name matches against prepared table headers**, not counts of measured or eligible people, observed exposure–phenotype pairs, or analyzable variables. Name presence does not prove the right module was merged, a question was asked, a field is nonmissing, its response is valid, or a weight/design applies. Wave-specific routes, valid-value rules, age/estimand, field target, weights, and PSU/variance must be reviewed before any pair is released for analysis.

The released official [2020 Wave 5 User Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_User_Guide_English.pdf) describes Exit_Module as deceased-respondent information (section 6). The separately sourced candidate crosswalk already marks death-date and circumstance items as decedent/proxy-only and unsuitable as a general cohort outcome or survival denominator.
