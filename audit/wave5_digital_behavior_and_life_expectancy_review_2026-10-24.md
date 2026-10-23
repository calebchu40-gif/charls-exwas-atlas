# Wave 5 digital-behavior and subjective life-expectancy review

Review date: 2026-10-24. Scope: public CHARLS 2020 questionnaire and Codebook metadata only. No participant records, response frequencies, or summary statistics were used in the catalogue update.

## Decision

Fifteen Wave 5 fields from the internet-use module are E candidates: DA040 (past-month internet use); DA041_s1–s5 (access devices); DA042_s1–s6 (internet activities); DA043 (mobile payment); DA044 (WeChat use); and DA045 (WeChat Moments posting). Their item labels and response categories are transcribed into `audit/behavior_exposure_variable_mapping_v1.csv`; the site groups them under “internet and digital technology use.” These are candidate self-reported behaviors, not validated exposures or causal variables.

DA029 is a single-wave P candidate: subjective likelihood of reaching a target age. The questionnaire calls it subjective life expectancy and says it reflects anticipation about one’s own health. The target age is `XFAgePossibility`, derived from the respondent’s age band. The target is 75 for age below 65; 80 for ages 65–69; then 85, 90, 95, 100, 105, and 110 for successive five-year bands from 70–74 through 95–99; and 115 for age 100 or older. The DA029 ordinal categories are 1=Almost impossible, 2=Not very likely, 3=Maybe, 4=Very likely, 5=Almost certain, and 997=Don’t know.

Because respondents are asked about different target ages, the same DA029 response category does not represent the same event for every respondent. Any future analysis must retain the target age and model it explicitly or stratify appropriately. DA029 is not observed survival, mortality, a clinical endpoint, or interchangeable with earlier-wave DA029, which refers to prostate illness.

## Route and missingness

DA040 asks whether the respondent used the internet in the past month. DA041 and DA042 are multi-select follow-up items, and DA043–DA044 occur within the digital-use sequence; DA045 follows the WeChat-use item. Preserve each source field and its route. A skipped or structurally missing follow-up response is not “No.” The Codebook’s descriptive frequencies were not copied into the site and must not be used as analysis denominators. Confirm item eligibility and the denominator in the authorized release before any statistical work.

The “other device” and “other internet activity” options are retained only as selected categories. Their accompanying open text is not a standardized measure and is excluded from public metadata and any proposed analysis until separately reviewed.

## C metadata decisions

`XFAgePossibility` is a generated question target, not a second respondent outcome or ordinary age covariate. `DC030` records the interviewer-observed language used during the interview (Mandarin, local dialect, or other dialect); it is measurement context, not the respondent’s native language or an environmental exposure. Both are classified as measurement metadata rather than as reviewed adjustment covariates. The site continues to describe C fields as source/design metadata, not a preselected adjustment set.

The automatically discovered C row for `DA042_s5` was a keyword hit on “money management.” It is now represented once as an E behavior candidate and removed from C for Wave 5; no unrelated-wave row was removed.

## Implementation and verification

- Source crosswalks: `audit/behavior_exposure_variable_mapping_v1.csv` and `audit/health_symptom_variable_mapping_v1.csv`.
- Reproducible propagation: `scripts/apply_wave5_digital_behavior_review.py`, `scripts/apply_wave5_core_demographic_review.py`, and `scripts/build_charls_atlas_metadata.py` (the metadata pipeline invokes both review scripts).
- Official extracted sources: `sources_official/CHARLS_2020_Questionnaire_English_extracted.txt` (DA029 and DA040–DA045 around questionnaire pages 32–34; DC030 and the auxiliary target-age formula in the interview/auxiliary sections) and `sources_official/CHARLS_2020_Codebook_extracted.txt` (DA029, DA040–DA045, DC030 and XFAgePossibility labels).
- Site metadata after rebuild: E 4,738; P 2,068; C 978 source-field/wave rows. The candidate-pair browser reports metadata co-availability only; actual pairwise complete sample sizes and association models remain uncomputed (formal models: 0).
- Validation: all 153 Python tests pass; `node --check site-prototype/dist/app.js` and `git diff --check` pass. Tests verify the 15-field scope, routing caveats, outcome interpretation, age-target metadata, exact removal of the Wave 5 E/C duplicate, and stable catalogue ordering.

Official questionnaire PDF: [CHARLS 2020 Questionnaire (English)](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_Questionnaire_English.pdf).
