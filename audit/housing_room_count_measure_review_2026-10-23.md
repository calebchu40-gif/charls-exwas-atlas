# CHARLS housing room and toilet count measures

Reviewed the bedroom, living-room and toilet counts in the official household questionnaires and wave Codebooks for 2011, 2013, 2015, 2018 and 2020. The review covers 15 wave-field entries. These are numeric counts, so a blank discrete-category list is appropriate.

| Wave | Fields | Questionnaire scope | Measurement and limits |
|---|---|---|---|
| 2011 | `i012_1`, `i012_2`, `i012_3` | Counts in the respondent household's current residence | Count; the bundled item applies a soft check above 20. |
| 2013 | `i012_1`, `i012_2`, `i012_3` | Counts in the respondent household's residence | Count; questionnaire soft check above 20. |
| 2015 | `i012_1`, `i012_2`, `i012_3` | Counts in the respondent household's residence | Count; questionnaire soft check above 20. |
| 2018 | `i012_1`, `i012_2`, `i012_3` | Counts in the currently occupied residence | Count; questionnaire soft check above 20. |
| 2020 | `i011_1`, `i011_2`, `i011_3` | Household Financial Respondent's house | Integer count; questionnaire distinguishes a hard nonnegative integer constraint from a soft check above 20. |

The 2020 question names the Household Financial Respondent's home, while earlier waves use the respondent/household residence wording. Preserve this difference in target-residence metadata. The measures are residence/household attributes, not individual-level housing exposure doses. Do not combine counts into a crowding score without a prespecified household-composition denominator and validation. Do not treat Codebook extrema as valid ranges, infer special-value handling from extrema, or assume field definitions and response processes are identical across waves. Authorized-release QA must establish special values, eligible records, missingness, and the household-to-respondent linkage before analysis.

Official source extracts checked: `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` and wave-specific questionnaire/Codebook extracts for 2013, 2015, 2018 and 2020. The 2020 questionnaire field constraint is recorded as a design/soft-check description, not as a verified data-cleaning rule. No participant-level data or Codebook frequencies were read into this review.
