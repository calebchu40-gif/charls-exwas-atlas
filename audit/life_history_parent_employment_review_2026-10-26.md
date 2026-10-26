# 2014 Life History caregiver employment metadata review (2026-10-26)

## Scope and sources

Reviewed the official CHARLS Life History Questionnaire section C1_a1–C2_b_1 and its Codebook fields in `FAMILYINFORMATION`. The structured field family contains eight entries: C1_a1/C1_b1 work duration before respondent age 17; C1_a2/C1_b2 broad usual occupation sector; and C2_a/C2_b unemployment while actively seeking work plus C2_a_1/C2_b_1 conditional frequency. `life_history_parent_employment_coverage_2014_v1.csv` records the exact field-level mapping to the existing guardian-employment and guardian-occupation concepts. No new concept was added because these measures were already in the atlas.

## Interpretation and exclusions

- Female and male caregiver roles follow A4a/A4b and are not necessarily biological parents.
- Work status refers to all, part, or none of the respondent's childhood before age 17; it is not the respondent's employment or household income.
- Structured occupation categories distinguish farming from non-agricultural occupation. Although the questionnaire requests occupation, department, position, and job-content details, these are free-text response values and are excluded from the public atlas.
- C2 unemployment follow-up frequencies are conditional on Yes, with further occupation-based routing. Blank fields must not be treated as No.
- Codebook frequency tables are not used; authorized-release values, missing codes, field storage and routes still require QA before analysis.

## Reproducibility

`scripts/build_life_history_exposure_crosswalk.py` regenerates the eight-row coverage ledger. Unit tests assert exact structured-field coverage and that free-text occupation fields do not enter the catalog.
