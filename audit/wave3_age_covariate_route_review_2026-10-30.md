# Wave 3 age and covariate routing review (2026-10-30)

## Scope

This is a source-based preparation note for the CHARLS 2015 Sample_Infor/Blood frame. It does not derive respondent ages, select an analytic domain, inspect participant birth dates, or authorize an association model.

## Official field map

The 2015 Codebook describes the Sample Information module as the released sample frame and lists `ID`, `householdID`, `communityID`, `crosssection`, `died`, `iyear`, and `imonth`. `crosssection` identifies the cross-sectional sample. `iyear` and `imonth` are string interview-timing fields; they provide year and month, not interview day.

The Codebook's Demographic Background section lists:

- `ba004_w3` and components `ba004_w3_1`–`ba004_w3_3`: birth date on the respondent's ID card or household registration (year/month/day).
- `ba002` and components `ba002_1`–`ba002_3`: reported birth date route; `ba002` distinguishes a date matching the civil document from a separately reported date.
- `ba003`: whether the separately reported date uses the solar or lunar calendar.

These fields are in a different module from Sample_Infor. Therefore the frame-first preparation may retain a sampled person whose demographic row is absent; the age inputs for that person must remain missing. Do not infer eligibility, spouse status, or age from household rosters, adjacent waves, interview status, or ID patterns.

## Safe derivation sequence to review before implementation

1. Preserve Sample_Infor as the Wave 3 frame and `crosssection` as the published domain flag. Establish the blood-weight target separately from age derivation; do not substitute `INDV_weight_ad2` or a later-wave weight.
2. Apply the questionnaire route: `ba002=1` means the actual date matches the ID/household-register date, so the source date is `ba004_w3_*`; `ba002=2` supplies a separate actual date in `ba002_*`. `ba003` records whether the `ba002` answer uses the solar or lunar calendar, and the questionnaire skips `ba003` when `ba002` is `.d` or `.r`. Retain route and calendar status; do not silently substitute the other date source.
3. Validate the month/day codes, partial dates, invalid calendar dates, missing route responses, and agreement/disagreement between the two reported dates using official labels and questionnaire instructions. Never infer a missing month/day as January or mid-month.
4. Convert lunar dates only with the pinned CHARLS-maintained `lunar2solar` implementation. The repository's parity workflow requires Stata and compares only synthetic dates with the official Mata table; no Stata runtime has yet been available, so lunar conversion parity remains open.
5. Because the interview source has year/month but no day, calculate a conservative age interval from the valid birth-date route rather than a falsely exact age. Keep unresolved, incomplete, or contradictory records unclassified. Any threshold/domain assignment must be stable across the interval or remain unresolved.
6. Freeze the target population and age-domain rule with the blood-response weight, cross-sectional flag, and survey design before building complete-case models. Define covariate adjustment from the estimand/DAG, not from whichever columns happen to be present. Report module-specific missingness in private QA and retain missingness rather than imputing from other modules.

## Current gate

The Wave 3 frame-to-Blood join has passed protected ID-only linkage and weight-domain checks. This note maps the age-source fields from the official Codebook but does not claim that age inputs, route validity, age eligibility, or covariate completeness have passed on the analytic records. Age, weight target, PSU/variance, estimand freeze, and independent methods review remain open. Formal association models remain zero.

## Sources

- `sources_official/CHARLS_2015_Codebook.pdf` and its locally extracted text, sections “Demographic Background” and “Sample Information”.
- `sources_official/CHARLS_2015_Questionnaire.pdf` for routing and date-source rules; the exact route remains to be checked against the applicable pages before coding.
- `audit/charls_lunar2solar_pinned_reference_2026-10-27.md` and `audit/lunar_official_stata_parity_workflow_2026-10-30.md` for the pinned conversion source and parity limitation.
- [CHARLS 2015 data page](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html).
