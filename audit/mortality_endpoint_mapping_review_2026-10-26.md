# Mortality and exit-module endpoint candidate review — 2026-10-25

## Scope and source basis

This review adds field-level candidate metadata for death-date components and selected death circumstances. It uses the local CHARLS field inventory for field presence/labels and official source documents for interpretation. The inventory is protected local metadata and is not added to the repository. No participant values, counts, or codebook frequency summaries are used.

- 2013: `Exit_Interview` fields `exb001_1`, `exb001_2`, `exb002`, and `exb009`, with official field labels from `sources_official/CHARLS_2013_Codebook_extracted.txt`.
- 2020: `Exit_Module` fields `exb001_1`–`exb001_3`, `exb002`, `exb007`, `exb008`, and `exb008_1`, checked against the official English questionnaire's EXB section. The questionnaire defines year/month/day; solar/lunar calendar; expectedness; a categorical final-illness interval; and a conditional years detail when the interval exceeds one year.
- 2018: the questionnaire cover screen records whether listed respondents are alive and routes to exit/death-cause instruments. This is household screening/routing information, not interchangeable with the detailed exit-module records above. It is intentionally not added as a harmonized mortality endpoint in this batch.
- 2015: no reviewed EXB source-field set was established in this pass; it is not inferred from adjacent waves.

## Classification

`mortality_event_date_component`, `mortality_expectedness`, and `mortality_final_illness_to_death_interval` are provisional P candidates. `mortality_date_calendar` is C metadata because it is required to interpret the date components. The calendar selector must not be treated as an exposure. Death-place and death-certificate fields are not included as phenotypes in this pass.

## Analysis and harmonization restrictions

Exit-module information is collected through a decedent/proxy pathway. Its existence cannot define non-deaths as zero, provide the at-risk denominator, or alone establish complete follow-up. A survival analysis would require respondent-level linkage, a verified regular-wave follow-up/censoring definition, official survey design/weights for the target population, and release-specific missing/special-value validation. The 2013 fields provide year/month while the 2020 questionnaire includes a day component; solar/lunar basis further prevents naive date pooling. The 2020 final-illness interval is categorical, and `exb008_1` is conditional detail, not an unconditional continuous duration.

These mappings are discoverable metadata candidates only. They do not authorize mortality modeling or assert that all fields have comparable wave coverage.


## Release record

The v127 catalog was published at commit `7b00491`. GitHub Validate run `40213942542` and GitHub Pages Deploy run `40213942548` succeeded. The live site returned app v127 and pair index v5, with nine mortality P source rows and two C calendar rows.
