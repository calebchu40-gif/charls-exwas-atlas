# 2014 Life History WORKHISTORY initial source review — 2026-10-26

## Scope and sources

This first pass inspected the official CHARLS Life History Questionnaire WORK HISTORY section and the matching Codebook module. It intentionally maps only one fully identified questionnaire item; the complete module inventory is recorded in `life_history_work_history_coverage_2014_v1.csv`. The special 2014 Life History sample remains separate from regular 2011–2020 waves: official release notes state it has no survey weight. No participant-level records, Codebook frequencies, free-text responses or job names are used.

The questionnaire defines a job as livelihood-oriented work lasting at least six months and distinguishes own agricultural production/business, agricultural employment, non-agricultural employment, non-agricultural self-employment, unpaid work in a household business and army service. It excludes housework, volunteering and school-year part-time work/internships. These boundaries matter for interpreting the later repeated-job records and must not be collapsed into a generic occupation or exposure measure.

## F001: status at age 16

Mapped the 13 Codebook option fields `f001s1`–`f001s13` to `life_history_status_at_age_16`: work; unemployment while seeking work; unemployment without seeking; illness; childbirth; care of children, elderly people or other family; leisure/travel; training; prison; schooling; and other. The questionnaire marks this as select-all-that-apply. It is a retrospective adolescent life-course context item, not a contemporaneous record or complete time-use measure. An unselected/missing option must not be treated as No until authorized-release storage and denominator semantics are verified.

## F_3: type of each repeated job

Mapped the 19 repeated Codebook fields `f_3_0_` through `f_3_18_` to `life_history_repeated_job_type`. Each asks which of six job categories applies to that episode: own agricultural production/business, agricultural employment, non-agricultural employment, non-agricultural self-employment, unpaid household-business help, or army service. The 0–18 slot index is retained. The questionnaire's job definition (livelihood work for at least six months) applies; this category does not identify occupation, industry, pesticide use, dust exposure or chemical dose. Blank/skipped slots do not establish a negative job history or complete lifetime count.

## Exhaustive field disposition

The Codebook lists 2,024 WORKHISTORY fields. The generated ledger assigns 32 fields to reviewed F001 and F_3 candidate concepts, three person/household/community keys to linkage exclusions, one version field to release-metadata exclusion, and the remaining 1,988 substantive fields to `deferred_source_review`. Those fields are not published as candidates and are not approved for analysis. Follow-up review must inspect each job family and repeated episode slot against questionnaire routing, reference period, respondent role, open-text identity, geographic/privacy sensitivity, monetary/workpoint units and measurement semantics before mapping.

The remaining F-series includes repeated job types and episode details, including employer/industry/occupation, work intensity, income/benefits, job transitions and reasons for stopping. These are not automatically environmental exposures; work history may support life-course context only when the exact construct and referent are verified.

## Reproducibility

`build_life_history_exposure_crosswalk.py` generates the candidate map, Life History JSON and exhaustive module ledger. The local build reports 108 concepts / 2,854 mappings overall (E 2,808, P 46), with 32 mapped WORKHISTORY source rows. Validation and deployment are pending for this local batch.
