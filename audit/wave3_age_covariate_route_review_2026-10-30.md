# Wave 3 age and covariate routing review (2026-10-30)

## Scope

This is a preparation and restricted aggregate-QA note for the CHARLS 2015 Sample_Infor/Blood frame. The protected audit processed only the birth-route/date fields needed for aggregate completeness flags; it emitted no IDs or exact dates, derived no respondent ages, selected no analytic domain, and authorized no association model.

## Official field map

The 2015 Codebook describes the Sample Information module as the released sample frame and lists `ID`, `householdID`, `communityID`, `crosssection`, `died`, `iyear`, and `imonth`. `crosssection` identifies the cross-sectional sample. `iyear` and `imonth` are string interview-timing fields; they provide year and month, not interview day.

The Codebook's Demographic Background section lists:

- `ba004_w3` and components `ba004_w3_1`–`ba004_w3_3`: birth date on the respondent's ID card or household registration (year/month/day).
- `ba002` and components `ba002_1`–`ba002_3`: the questionnaire asks whether actual birth date is the same as the civil-document date (`1`) or a separate reported date (`2`); only route 2 supplies the separate date components.
- `ba003`: whether the separately reported actual date (`ba002=2`) uses the solar (`1`) or lunar (`2`) calendar. The 2015 Codebook frequency table reports BA003 observations at approximately the size of the BA002=2 route, while BA002=1 is the much larger same-as-document route. The audit therefore requires BA003 only for BA002=2; it does not treat an unasked calendar field on BA002=1 as missing. The questionnaire also says to skip BA003 when the respondent does not know the date (`ba002=.d` or `.r`). This route interpretation remains explicit for independent methods review.

These fields are in a different module from Sample_Infor. Therefore the frame-first preparation may retain a sampled person whose demographic row is absent; the age inputs for that person must remain missing. Do not infer eligibility, spouse status, or age from household rosters, adjacent waves, interview status, or ID patterns.

## Safe derivation sequence to review before implementation

1. Preserve Sample_Infor as the Wave 3 frame and `crosssection` as the published domain flag. Establish the blood-weight target separately from age derivation; do not substitute `INDV_weight_ad2` or a later-wave weight.
2. Apply the questionnaire route: `ba002=1` means the actual date matches the ID/household-register date, so the source date is `ba004_w3_*`; `ba002=2` supplies a separate actual date in `ba002_*`. Require `ba003` only for the separate actual-date route (`ba002=2`); do not treat its absence on the same-as-document route as missingness. The questionnaire skips `ba003` when the respondent does not know the birth date (`ba002=.d` or `.r`). Retain route and calendar status; do not silently substitute the other date source.
3. Validate the month/day codes, partial dates, invalid calendar dates, missing route responses, and agreement/disagreement between the two reported dates using official labels and questionnaire instructions. Never infer a missing month/day as January or mid-month.
4. Convert lunar dates only with the pinned CHARLS-maintained `lunar2solar` mapping. A source-only parser has compared every row in the official ordinary and leap `.mmat` tables with pinned Python 0.1.4 and found zero differences. This closes mapping parity; Wave 3 route handling, interval construction, and independent age review remain open. The optional Stata workflow is no longer a prerequisite.
5. Because the interview source has year/month but no day, calculate a conservative age interval from the valid birth-date route rather than a falsely exact age. Keep unresolved, incomplete, or contradictory records unclassified. Any threshold/domain assignment must be stable across the interval or remain unresolved.
6. Freeze the target population and age-domain rule with the blood-response weight, cross-sectional flag, and survey design before building complete-case models. Define covariate adjustment from the estimand/DAG, not from whichever columns happen to be present. Report module-specific missingness in private QA and retain missingness rather than imputing from other modules.

The questionnaire instructs interviewers to record month/day as `0` when unknown and gives 1900–2015 as the birth-year range. The private audit therefore treats zero month/day as unknown, never as January or the first day.
## Current gate

The Wave 3 frame-to-Blood join has passed protected ID-only linkage and weight-domain checks. On 2026-10-30, the source-bound preparation was repeated locally from the official All Data archive into a separate protected output directory, then joined to the official Blood artifact. Both archive hashes matched the pinned CHARLS release values, the `Sample_Infor` spine and output hashes were bound in the private manifest, and the one-to-one left merge retained the released frame. A hash-bound private aggregate audit confirms the required age-source fields and interview timing are present. The first version incorrectly required BA003 for both BA002 routes; review of the official questionnaire sequence and Codebook frequencies showed that calendar applicability should be checked on the separate actual-date route (BA002=2), while BA002=1 uses the civil-document date. The private audit was corrected and rerun. It still flags unresolved/missing date routes, missing/unrecognized BA003 values on BA002=2, and zero month/day inputs (explicitly treated as unknown). It found missing birth-year/month/day inputs, but no nonmissing date components outside the questionnaire basic numeric ranges and no incomplete interview year/month fields. The questionnaire says BA003 is skipped when the respondent does not know the birth date (`BA002=.d` or `.r`); these cases must remain distinct from a missing demographic-module record in the Sample_Infor frame. No exact counts or participant-level data are in this repository; protected QA is stored only under the local private root. This does not establish valid ages or an analytic domain. Age intervals, route/code adjudication, covariate completeness, blood-weight target, PSU/variance, estimand freeze, and independent methods review remain open. Formal association models remain zero.

## Sources

- `sources_official/CHARLS_2015_Codebook.pdf` and its locally extracted text, sections “Demographic Background” and “Sample Information”.
- `sources_official/CHARLS_2015_Questionnaire.pdf` and the extracted pages around BA004_W3/BA002/BA003 for routing and date-source rules.
- `audit/charls_lunar2solar_pinned_reference_2026-10-27.md`, `scripts/verify_official_lunar_table_parity.py`, and `audit/wave1_age_interval_candidate_review_2026-10-29.md` for the pinned source and completed table parity check.
- [CHARLS 2015 data page](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html).
