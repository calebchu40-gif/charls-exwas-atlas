# Uric-acid specification analysis (methods only)

**Status:** exploratory, PI-delegated, not independently reviewed, and not approved for publication. All coefficient estimates, confidence intervals, p/q values, sample counts, and specification-curve outputs remain in the protected server workspace.

## Model sequence

The private analysis script is `scripts/wave1_uric_acid_specification_curve.py`. It evaluates a prespecified covariate sequence for the registered running-water and cooking-fuel contrasts against serum uric acid, under both the community-PSU and county-prefix-PSU approximations. The sequence adds age terms, sex, education, urban/rural context, smoking, alcohol, BMI, creatinine-derived eGFR, and self-reported hypertension, diabetes, and kidney disease.

Coding notes retained for review: smoking uses `da059`; alcohol uses `da067` with former drinkers grouped with non-drinkers in this exploratory specification; BMI is derived from `qi002` and `ql002`; eGFR is derived from `newcrea` using the CKD-EPI 2009 equation. These choices need source and population-applicability review. In particular, eGFR adjustment may represent confounding, mediation, or both, and the single creatinine measurement has limitations.

## Important omissions and limits

The reviewed questionnaire material did not identify a diuretic-specific medication field or a purine-intake measure for this analysis. The current specification therefore cannot claim adjustment for either. This absence should be checked against the complete official codebook before finalizing the covariate strategy. The analysis is cross-sectional, complete-case, and uses approximate variance without official strata or replicate weights. Household water and cooking-fuel measures may share causes such as urbanicity and socioeconomic context; no causal interpretation is supported.

The private output predates a frozen configuration and lacks a contemporaneous signed run manifest binding input, code, and configuration hashes. It remains exploratory. Independent methods review, independent reproduction, and disclosure review are required before any release decision.