# Wave 3 blood outcome handling candidates

**Date:** 2026-10-30  
**Status:** Source-based candidate rules for later review; no rule is frozen and no Wave 3 model is authorized.  
**Scope:** Public CHARLS 2015 Blood Release Note, official Codebook/crosswalk metadata, and the existing metadata-only intake record. No respondent records, assay values, weights, IDs, or private QA were read in this review.

## Source findings

The official Wave 3 Blood Release Note lists 16 analytes and identifies two measurement fields that affect interpretation: `bl_fasting` and `bl_top_coding_tg`. The released `bl_tg` field is top-coded at 500 mg/dL when original triglycerides exceed 500, with `bl_top_coding_tg` marking that condition. Therefore, the released value is not the uncapped original TG for flagged records. Do not reconstruct original TG values from the flag, treat capped values as uncensored original measurements, or drop flagged observations after looking at results.

The 2015 `bl_fasting` metadata labels are 1=Yes and 2=No. This mapping applies to Wave 3 only and must not be transferred to Wave 1 `qc1_va003`. A Wave 3 glucose analysis must retain and use the fasting-status field under a prespecified measurement plan; any full-sample adjustment or fasting-only domain must be chosen before inspecting associations.

The separate Wave 3 `Blood_weight` is a cross-sectional blood-response weight. It does not itself resolve additional assay subsampling (notably cystatin C), design variance, or pair-specific missingness. The exact supported target for each analyte still needs source and methods review.

## Candidate rules

The accompanying CSV registers all 16 analytes at their released units. For outcomes without a documented finite special-code rule, the conservative candidate is to exclude Stata missing values, retain other finite released values, and avoid assay-range filtering; this remains subject to independent approval and must not be interpreted as proof that finite sentinel codes cannot exist. Identity-scale analysis is the candidate default; no transformation is frozen.

`bl_tg` is specifically marked blocked pending a decision on whether the estimand is the association with the **released capped measure** or whether a reviewed censored-data method is warranted. The analysis must disclose this release limitation and must not claim an association with original uncapped TG unless an appropriate source-backed method is approved. `bl_glu` is not blocked for missing fasting-code mapping, but its fasting-handling model remains unfrozen. Cystatin C requires confirmation of any assay-subsampling and weight coverage.

## Intake and design boundary

The protected Wave 3 Blood archive has passed the existing official SHA-1 and metadata-only header gate. The official note distinguishes 13,420 total blood responders from 13,013 cross-sectional responders; neither total is a pairwise model denominator. Wave 3 design documentation does not provide the full respondent-to-final-PSU / stratum mapping. No variance candidate is approved for Wave 3, and the Wave 1 Option A choice does not carry over automatically.

All 16 rows remain candidate-only. Before any association fitting, freeze the cross-sectional target and sample flag, `Blood_weight` applicability, age domain, fasting/TG/cystatin-C handling, covariates, missingness, variance method, full hypothesis family, and independent review. Formal Wave 3 association count remains zero.

## Official sources

- [2015 CHARLS Wave 3 data page](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html)
- [2015 CHARLS Blood Data Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf), especially sections 4–5 and Table 1.
- [`audit/blood_biomarker_crosswalk_v1.csv`](blood_biomarker_crosswalk_v1.csv)
- [`audit/wave3_blood_weight_estimand_review_2026-10-30.md`](wave3_blood_weight_estimand_review_2026-10-30.md)
- [`audit/charls_wave3_psu_variance_release_review_2026-10-30.md`](charls_wave3_psu_variance_release_review_2026-10-30.md)
