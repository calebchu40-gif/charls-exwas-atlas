# 2014 Life History child/family section disposition review (2026-10-26)

## Scope and method

Completed source-level disposition of the remaining child/family Codebook fields in `DEMOGRAPHICBACKGROUNDS`, after separately mapping respondent pregnancy history, offspring early-care context, additional-child screen/count items, and the respondent's hukou section. The source basis is the official Life History Questionnaire and Codebook. Only questionnaire wording, routes, field names and labels were used; no participant values, child names, Codebook frequencies, or association results were accessed or published.

The reproducible ledger assigns exactly one disposition to each of the module's 1,920 unique Codebook fields. The builder now fails closed if a new field lacks an explicit rule; the generic `deferred_demographic_section_review` category is zero.

## Full module disposition

| Disposition | Fields | Decision |
| --- | ---: | --- |
| `mapped_candidate` | 1,027 | Candidate exposure/context fields with source-reviewed question, referent and route mappings. |
| `deferred_sensitive_relative_identity` | 204 | 90 spouse/partner roster political/minority/religious fields plus 114 child political/ethnicity/religion fields. Held from public E/P mapping pending data-minimization, ethics, release and disclosure review. |
| `c_only_offspring_marital_context` | 180 | Child marriage and child-spouse age/education/hukou/relationship details; relative-level family context, not participant E/P. |
| `excluded_child_date_component` | 167 | Child birth/death/adoption timing components, excluded from the candidate map to avoid publishing relative date fields or deriving chronology. |
| `c_only_offspring_historical_experience` | 125 | Child military-service and sent-down history, not the respondent's own exposure. |
| `c_only_offspring_roster_and_adoption_status` | 121 | Child roster category/sex/alive/route fields and adoption-out indicators; no child-slot values or derived counts. |
| `c_only_offspring_education_and_status` | 36 | Offspring schooling, grade, education attainment and work/school status; not the respondent's phenotype. |
| `excluded_child_parent_linkage` | 18 | Child-to-spouse roster relation/slot link. |
| `excluded_child_roster_order_key` | 12 | Biological-child order slot used by the pregnancy-history loop. |
| `excluded_relative_birth_date` | 12 | Spouse/partner date-of-birth components. |
| `c_only_partner_loop_metadata` | 5 | Spouse/partner loop continuation fields. |
| `c_only_interview_process_metadata` | 4 | Interview/proxy process fields. |
| `c_only_offspring_adoption_source` | 4 | Child/adoption-origin category; relative-level context without a defined participant estimand. |
| `excluded_linkage_key` | 3 | Person, household and community join keys. |
| `c_only_redundant_respondent_metadata` | 1 | Redundant respondent gender roster field. |
| `excluded_release_metadata` | 1 | Release/version bookkeeping field. |
| **Total** | **1,920** | Unique fields; no duplicate or unclassified disposition. |

## Candidate role and safeguards

The mapping retains respondent-level or household-context fields that may support a clearly defined CHARLS life-course ExWAS estimand. It does not relabel offspring education, health, marriage, political identity, ethnicity, religion, military service, or sent-down history as the respondent's phenotype or exposure. Sensitive relative identities are held, relative dates and parentage links are excluded, and all public content remains field/question metadata only. Questionnaire-only item C032 (child death cause) has no corresponding field in the inspected Codebook inventory; no field is invented.

The Life History module is a 2014 retrospective special survey whose release note states that no weight is provided. Even mapped fields remain candidate metadata, not analysis-ready variables; they are excluded from the regular-wave weighted pair universe until an estimand, release identity, route/missing-value behavior, authorized linkage and valid design are justified.

## Regeneration

Run `python scripts/build_life_history_exposure_crosswalk.py`. The builder ignores Codebook frequencies and verifies the 1,920 unique-field total. An unmapped new module field now raises an error instead of silently entering a generic pending bucket.
