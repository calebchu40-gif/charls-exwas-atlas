# Wave 1 blood-analyte codebook scope audit

**Checked:** 2026-10-30  
**Status:** Source scope clarified; finite numeric sentinel handling for blood analytes remains unresolved. No participant-level blood values were read and no association was fitted.

## Source distinction

The official CHARLS Wave 1 page lists the National Baseline Codebook and the Blood Data Users' Guide as separate documentation items. The official Peking University Open Research Data Platform likewise lists the 2011 codebook archive (file 120) separately from the Blood data package (file 201) and its Blood Users' Guide. See:

- [Official CHARLS Wave 1 documentation and data page](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)
- [Official CHARLS Wave 1 baseline dataset, version 1.1](https://opendata.pku.edu.cn/dataset.xhtml?persistentId=doi%3A10.18170%2FDVN%2FIZU8OF&version=1.1)

The archived 2011 National Baseline Codebook has a “Biomarkers” questionnaire section, but its entries concern questionnaire/physical-measurement variables (for example, completion reasons and measurement timing). Some entries show Stata extended missing categories such as `.D`, `.E`, and `.R`. The reviewed codebook text does not contain the 15 registered blood-analyte field names (`qc1_vb002`, `qc1_vb004`, `qc1_vb005`, `qc1_vb006`, `qc1_vb009`, `newcho`, `newhdl`, `newldl`, `newtg`, `newglu`, `newhba1c`, `newcrp`, `newbun`, `newcrea`, `newua`) or `bloodweight`.

Therefore, missing-value conventions documented for questionnaire/physical-measurement fields are **not evidence** for finite numeric sentinel codes in the separate Blood release. Do not project negative questionnaire response codes, `.D/.E/.R` label conventions, or harmonized-data conventions onto assay values. For the 15 blood outcomes, the Blood Users' Guide and Blood-file-specific release metadata are the relevant sources. The guide documents assay methods, units, detection information, missingness/participation context, and descriptive summaries, but the reviewed sources do not provide a reproducible field-specific finite-sentinel map or universal valid-value bounds for this outcome set.

## Analytic consequence

- Stata system and extended missing values remain missing.
- No finite Blood outcome value is recoded or excluded based only on a generic Codebook convention, assay detection range, clinical cutoff, or observed distribution.
- This is not a claim that all finite values are valid. The field-specific finite-code/validity rule must remain `unresolved` until an authoritative Blood-specific source or independent, documented review resolves it.
- Keep all 15 outcomes and their registered coefficients in the planned family. Do not fit any of them until the outcome rule, estimand, design, frozen configuration, and independent methods-review gates are complete.

## Reproducibility note

The local official Codebook extract was searched for the 15 field names and `bloodweight`; none were found. The private server copy of the same official 2011 codebook archive was also previously checksum-matched to the Peking University file-120 record. This note records source scope only; it contains no participant records, respondent IDs, restricted QA counts, or estimates.
