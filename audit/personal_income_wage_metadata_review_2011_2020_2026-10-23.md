# Individual income and wage metadata review (2011–2020)

This review uses the official wave questionnaires and Codebooks in `sources_official/`. It changes only variable metadata; no respondent records, Codebook frequencies, means, minima, maxima, or analytic thresholds were copied.

The review script `scripts/apply_personal_income_metadata_review.py` updates the reviewed rows in `audit/personal_income_exposure_mapping_v1.csv`; the catalogue builder imports labels and source-backed continuous/count states.

## Field families and decisions

- Wage amounts: 2011 distinguishes annual Yuan (`ga002`) from the monthly alternative (`ga002_1`); 2013 annual wage uses `ga002_1`; 2015, 2018 and 2020 use annual `ga002`. These are not pooled as a common unit without an explicit transform and reference-period rule. The 2020 `ga006_1` and `ga006_2` are conditional COVID-period decrease/increase amounts in Yuan. Interviewer soft checks and Codebook descriptive extrema are not analytic bounds.
- Asset/finance indicators: questionnaire-defined Yes/No labels were recorded for 2011 (7 fields), 2013 (6), 2015 (8) and 2018 (6). Wave 2018 explicitly includes `999=Refused to answer`; this code is preserved. The 2015 `hc036` item is private lending during the past year, while 2011–2013 use the rotating-savings association construct; they are not assumed comparable.
- Inheritance source slots: five options each in 2011 and 2013 are check-all-that-apply. The option identity is known but unselected-slot storage and denominator are not. The website leaves value labels blank and cautions against interpreting blank/missing as No.
- Fraud: 2015 `hd005_w3` is an ever-defrauded Yes/No indicator; 2018 `hd005_w4_0` is a continuous event count of lifetime fraud experiences with property loss, not a category.
- Wage deduction scope: 2020 `ga003` records `1=Yes; 2=No; 997=Do not know; 999=Refused to answer` for whether the reported wage excludes insurance, income tax, public housing fund and other fees. It is a measurement/scope flag, not an exposure amount.

## Analysis and data limits

This metadata review does not verify the authorized-release storage type, all special values, or each respondent's eligible denominator. Routed blanks must not be recoded as No. Preserve person/couple scope, survey wave, reference period, units, and item-specific wording. Do not treat these cross-wave items as harmonized exposures until their construct and target population are reconciled.

A local verification confirmed that the reviewed statuses reach the public candidate catalogue and that the 89 existing `DO NOT ANALYZE` locks remain intact. Formal association models remain zero.
