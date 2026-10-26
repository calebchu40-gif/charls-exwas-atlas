# 2014 Life History WORKHISTORY initial source review — 2026-10-26

## Scope and sources

This first pass inspected the official CHARLS Life History Questionnaire WORK HISTORY section and the matching Codebook module. It intentionally maps only one fully identified questionnaire item; the complete module inventory is recorded in `life_history_work_history_coverage_2014_v1.csv`. The special 2014 Life History sample remains separate from regular 2011–2020 waves: official release notes state it has no survey weight. No participant-level records, Codebook frequencies, free-text responses or job names are used.

The questionnaire defines a job as livelihood-oriented work lasting at least six months and distinguishes own agricultural production/business, agricultural employment, non-agricultural employment, non-agricultural self-employment, unpaid work in a household business and army service. It excludes housework, volunteering and school-year part-time work/internships. These boundaries matter for interpreting the later repeated-job records and must not be collapsed into a generic occupation or exposure measure.

## F001: status at age 16

Mapped the 13 Codebook option fields `f001s1`–`f001s13` to `life_history_status_at_age_16`: work; unemployment while seeking work; unemployment without seeking; illness; childbirth; care of children, elderly people or other family; leisure/travel; training; prison; schooling; and other. The questionnaire marks this as select-all-that-apply. It is a retrospective adolescent life-course context item, not a contemporaneous record or complete time-use measure. An unselected/missing option must not be treated as No until authorized-release storage and denominator semantics are verified.

## F_3: type of each repeated job

Mapped the 19 repeated Codebook fields `f_3_0_` through `f_3_18_` to `life_history_repeated_job_type`. Each asks which of six job categories applies to that episode: own agricultural production/business, agricultural employment, non-agricultural employment, non-agricultural self-employment, unpaid household-business help, or army service. The 0–18 slot index is retained. The questionnaire's job definition (livelihood work for at least six months) applies; this category does not identify occupation, industry, pesticide use, dust exposure or chemical dose. Blank/skipped slots do not establish a negative job history or complete lifetime count.

## F_2: repeated job timing

Mapped 171 year/month/season/half-year/end-status components across 19 repeated job records. The questionnaire permits a recalled year range and instructs interviewers to record its midpoint when the exact year is unknown. The month, season and half-year fields are alternative precision. These fields establish reported chronology, not exact duration; do not subtract dates until precision, special values, ongoing jobs and episode linkage are validated. The 19 `f_2_add_*` main-workplace fields are excluded because they can identify worksites/localities; no geocoding or linkage is performed.

## F_1: lifetime work status and routed never-work reason (follow-up review)

The official questionnaire and Codebook define `F_1` as lifetime ever-worked status. Its work construct follows the questionnaire's livelihood-work definition and is distinct from current employment, exact duration or occupation. `F_1_0` and `F_1_1` are prior-wave consistency/interviewer confirmation items that route the interviewer back to correct `F_1`; they are excluded as independent E/P variables. The candidate map therefore uses only the final corrected `F_1` response.

`F_1_2` asks the main reason among respondents whose corrected `F_1` indicates they never worked. It is retained as a separate conditional candidate, not as a disability/caregiving diagnosis or a category interchangeable with work history. The `other` response's open text is not in the Codebook mapping and is not published. Skip/missing values must not be interpreted as No; the denominator and value coding require authorized-release QA.

## F104/F105/F105a: nested employer context (follow-up review)

Mapped 19 repeated F104 employer-type fields, 15 F105 firm-ownership fields and 13 F105a official-staff status fields as three separate socioeconomic-context candidates. Questionnaire routing is retained: F104 follows agricultural/non-agricultural employment categories (F_3=2/3); F105 follows firm employer type; F105a follows government/public-institution employer type. Codebook job-slot suffixes are preserved. These constructs can describe work context but are not direct environmental exposures, occupation codes, industry-specific agents or dose measures. Skipped fields outside each route are not No. “Other” write-in text is not mapped.

## F101c/F101c_a, F112b/F112b_a, F115a/F115a_a: repeated job intensity (follow-up review)

Mapped 207 month/year, days/month and hours/day components into separate agricultural, employee and self-employed work-intensity candidates. The exact subtype routes are retained (F_3=1; F_3=2/3; F_3=4/5). For agricultural work, the beginning-period items are routed after the preceding duration screen: jobs lasting at least five years continue, and the first job continues regardless of duration; the middle-period items are asked only where job duration is at least 20 years. For the other groups, starting-period and middle-period measurements are retained under the same construct but can be distinguished from their official field codes. Slot and phase must not be collapsed before authorized-release data QA. These are recalled work-intensity measures; they do not directly measure pesticides, fertilizer, dust or any other occupational agent. The questionnaire itself mentions pesticides as an example of agricultural input costs in a net-income definition, but that does not establish respondent exposure and those income fields are not mapped here.

## F107/F108 and F110/F110_a: employer benefits and reported position (follow-up review)

Mapped 15 repeated F107 employer pension-eligibility fields and 15 F108 employer medical-reimbursement fields as separate candidates, plus 24 F110/F110_a beginning/middle position-category fields. F107 is eligibility to receive pension from the work unit, not pension receipt or enrollment; F108 is employer reimbursement availability, not medical utilization or reimbursement actually received. F110/F110_a preserve position phase and the employment route (F_3=2/3); these broad position categories are not a harmonized occupation/industry code. Routed skips are not No. The position “other” write-in and employer/work-unit descriptions remain unmapped.

## F112a/F112a_a: employer benefits and workplace childcare (follow-up review)

All 357 Codebook fields are assigned uniquely using six explicit patterns: 264 select-all employer benefit categories at job start/middle; 21 monthly monetary value of selected benefits; and 72 employer-affiliated nursery/kindergarten/neither fields at job start/middle. The questionnaire routes F112a after the employee-job section and explicitly skips the benefit amount after “None”; the childcare item asks whether children/grandchildren could attend employer-affiliated facilities. Repeated job slot and timing phase remain identifiable. “None” and “Neither” are explicit responses; blanks/skips cannot be recoded to these values. Monetary benefit value is distinct from wage/salary and must not be pooled across periods without validated currency adjustment. These are employer socioeconomic/family context measures, not environmental exposures.

## F120/F120a: reasons for ending nonmilitary and military jobs (follow-up review)

Mapped 238 repeated F120 select-all reason fields across 14 Codebook job slots and eight F120a military-cessation fields. F120 is asked only when F118 says the respondent no longer does the job, and only for F_3=1–5; F_3=6 military service uses F120a. F120 includes organizational, land-taking, health, family, migration, retirement and voluntary-departure reasons; it does not record a unique primary reason. Preserve the episode suffix, multi-select structure, upstream route and the distinction from military F120a. Neither item is a specific environmental-agent exposure; health reasons for stopping must not be recoded as a disease diagnosis. Other write-in text is unmapped, and skipped fields are not No.

## F118/F123c/F126a/F126b/F127b: current status, final-year work intensity and benefits (follow-up review)

Added 15 F118 yes/no fields (“still doing this work?”), keeping this separate from overall current-employment status. Extended the three work-intensity concepts with 39 F123c agricultural, 45 F126b employee, and 36 F127b self-employment current/last-year month/year, days/month and hours/day fields. Extended F112a benefit concepts with 165 F126a benefit-category indicators, 13 monthly benefit-value fields and 39 childcare-facility indicators for the current/last year. All repeated job slots remain distinct. F123c follows the five-year screen and F_3=1; F126b/F126a follow F_3=2/3; F127b follows F_3=4/5. `None`/`Neither` remain explicit categories, and blank/skip is not absence. Last-year nominal benefit values remain separate from wage and require valid currency-period handling. These are work-context variables, not agent-specific environmental exposure or dose.

## Exhaustive field disposition

The Codebook lists 2,024 WORKHISTORY fields. The generated ledger assigns 1,468 fields to reviewed F001, F_3, F_2, F_1, F_1_2, F104, F105, F105a, repeated work-intensity, employee-position and employer-benefit candidate concepts; excludes 19 repeated main-workplace location/text fields for privacy, two route/quality fields, three person/household/community keys and one release-version field; and assigns the remaining 531 substantive fields to `deferred_source_review`. Those fields are not published as candidates and are not approved for analysis. Follow-up review must inspect each job family and repeated episode slot against questionnaire routing, reference period, respondent role, open-text identity, geographic/privacy sensitivity, monetary/workpoint units and measurement semantics before mapping.

The remaining F-series includes repeated job and episode details, including job task/industry/occupation, work intensity, income/benefits, job transitions and reasons for stopping. Employer type, firm ownership and official-staff status were mapped as distinct nested socioeconomic-context candidates after reviewing F104/F105/F105a and their routes. They are not direct environmental exposures; they must not be interpreted independently of job slot or the upstream F_3/F104 condition. Remaining details require source review before mapping.

## Reproducibility

`build_life_history_exposure_crosswalk.py` generates the candidate map, Life History JSON and exhaustive module ledger. The local build reports 127 concepts / 4,309 mappings overall (E 4,263, P 46), with 1,468 mapped WORKHISTORY source rows. F120/F120a was published as app v165 / JSON v32 (commit `876d576`), with live versions and remote/local JSON hash verified. The F118/F123c/F126a/F126b/F127b follow-up batch is published as app v166 / JSON v33 in commit `663eccd`; live homepage and loader tags, last-year fields, and remote/local JSON SHA-256 were verified.
