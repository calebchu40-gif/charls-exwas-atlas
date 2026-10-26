# 2014 Life History HEALTHHISTORY full-field review (2026-10-26)

## Scope and source review

Compared all 86 HEALTHHISTORY Codebook fields with the official 2014 Life History questionnaire, sections HEALTH HISTORY and HEALTH CARE HISTORY (questionnaire pages 101–109). The review uses item wording, age thresholds, question routes and Codebook variable names/labels only; it does not use Codebook frequency distributions or participant records. Every Codebook field has exactly one disposition in `life_history_health_history_full_coverage_2014_v1.csv`.

## Newly mapped candidate concepts

| Concept | Fields | Role | Interpretation and key limits |
|---|---:|---|---|
| Age at first menstrual period | 1 | P | Female-only five-band recalled age; do not impute exact age from band midpoint. |
| Adult physical injury with lasting disability/limitation | 5 | P | Injury gate, work-related status, first event year, disability certificate and conditional disability category. The detailed injury type/body-part response is questionnaire-only free text and excluded. |
| Workplace consequences attributed to ill health after age 16 | 7 | P | Multi-select reports of denied promotion, reduced responsibility, underqualification, harassment, pay cut, dismissal or none. These are self-attributed outcomes, not objective employment records. |
| Adult illness-related confinement, hospitalization and work absence | 4 | P | Distinct one-month bed/home, hospitalization, repeated hospitalization and job-leave outcomes; not a current clinical measurement or validated composite. |
| Any vaccination before age 16 | 1 | E | Broad preventive-care marker; examples include smallpox vaccination and oral polio-prevention pills. Not vaccine-specific or a complete immunization record. |
| Usual source of care and periods without convenient care | 9 | E | HC002 defines a usual care source within two hours; conditional HC004 age-period durations and HC004a first remembered doctor type are retained separately. Age bands differ in width; HC004a is not automatically the usual source. |
| Adult blood-pressure screening | 2 | E | Ever checked after age 16 and first year; not blood pressure or hypertension status. |
| Adult blood testing | 2 | E | Any post-16 blood test (e.g., cholesterol/glucose), excluding tests at prior CHARLS visits, and first year; not a lab result. |
| Breast examination | 2 | E | Female-routed examination history and first year; separate from diagnosis and prostate testing. |
| Prostate cancer testing | 2 | E | Male/female questionnaire route, with heterogeneous tests (DRE, PSA, biopsy examples) pooled in the item; not prostate cancer status. |
| Vision testing | 2 | E | Ever tested after age 16 and first year; not visual acuity. |
| Dental examinations | 2 | E | Ever examined after age 16 and first year; not oral-health status. |
| Physical activity increase, diet change, smoking cessation, alcohol reduction | 8 each; 32 total | E | Four separate behavior-change histories. HC023 requires a change maintained for at least a year; HC024 marks age periods (0–15, 16–25, 26–40, 41–55, 56–65, 66–75, >75). These fields do not measure behavior level, intensity, amount or relapse. The shared `hc023s96` none option is separately excluded as metadata. |
| Medical insurance status and first post-16 coverage year | 2 | E | Questionnaire examples retained. English wording asks current coverage but its negative category says never insured; coverage continuity/type are not inferred. |

These E/P labels are discovery-catalog roles, not an analysis plan. The 2014 special survey is retrospective, has no released sampling weight, and stays separate from the regular five-wave weighted co-availability matrix. No participant values, responses or frequencies are placed in the public atlas. Actual release coding, conditional missingness and respondent/proxy handling still require controlled-release QA before any model is defined.

## Full-field disposition

| Disposition | Fields |
|---|---:|
| Mapped E/P candidate metadata, including existing HS002–HS006 | 78 |
| Excluded HC023 shared “none of these” option (not an independent exposure) | 1 |
| Excluded person/household/community linkage keys | 3 |
| Excluded section respondent/proxy metadata | 3 |
| Excluded release/version metadata | 1 |
| **Total** | **86** |

## Reproducibility

`scripts/build_life_history_exposure_crosswalk.py` generates the candidate crosswalk, public JSON and the 86-row full-module ledger. Tests enforce exact concept field counts and one explicit disposition per Codebook variable. Candidate field count is not participant count, analytical sample size or result count.

