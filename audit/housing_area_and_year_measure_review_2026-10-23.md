# CHARLS dwelling area and timing fields

Official questionnaires and Codebooks were checked for eight fields before assigning units in the atlas:

| Wave / field | Measure and unit | Scope/interpretation |
|---|---|---|
| 2011 `i001` | Current-residence construction area, square metres | Main-respondent housing section; questionnaire soft-checks below 10 or above 500. |
| 2013 `i001` | Current-residence construction area, square metres | Main-respondent housing section; same soft-check wording. |
| 2020 `i028` | House size, square metres | Household Financial Respondent's house; positive real response with questionnaire soft check outside 10–500. |
| 2011/2013/2015/2018 `i005` | Calendar year built | Exact-year entry; separate `i005_1` interval is offered if the exact year is unclear. |
| 2020 `i002` | Calendar year moved into current housing | Applies to Household Financial Respondent; questionnaire gives range 1900–2020 and interviewer instruction to enter -1 if unknown. This is not building construction year. |

Soft checks and the 2020 interviewer instruction are documented as questionnaire behavior, not as a complete analytic-file missing-value specification or a validated data-cleaning range. Exact years and fallback intervals remain separate; Codebook extrema are not used as valid ranges. Residence wording, release-specific special values, eligibility, and household-to-person linkage require authorized-release QA before modeling. The 2020 fallback `i003` intervals are catalogued separately with their questionnaire categories and are not converted into a guessed year.

Sources: official 2011 baseline household questionnaire; 2013, 2015, and 2018 questionnaires; 2020 English questionnaire; wave-specific Codebook extracts. No participant-level observations or frequencies were used. The reproducible metadata application is `scripts/apply_housing_area_year_review.py`.
