# 2014 EDUCATIONHISTORY continuation review — 2026-10-26

## Scope and sources

This continuation compares the official Life History questionnaire (items E012–E034c) with all corresponding EDUCATIONHISTORY Codebook field identities. It extends the earlier E000–E011 review; it is not a full review of the remaining 1,105-field module.

## Newly mapped candidate groups

| Concept | Questionnaire items | Fields | Interpretation / route |
|---|---|---:|---|
| Primary-school attainment context | E013, E020–E022 | 5 | Last primary school's nominal duration, graduation, highest completed grade, recalled peer transition category. E021 is conditional on not graduating; E022 is peer context. |
| Primary-school interruption detail | E018–E019 | 14 | Interrupted semesters plus 13 reason selectors. Routed by E005 primary-stage interruption; reason items are multi-select. |
| Middle-school attainment context | E024a, E031–E034c | 7 | Number of middle schools, graduation, completed grade, peer progression and high-school entrance exam pathway. Retain skips and conditional examination routes. |
| Middle-school interruption detail | E029–E030 | 14 | Interrupted semesters plus 13 reason selectors. Routed by E005 middle-stage interruption; reason items are multi-select. |

This adds 40 field mappings to the prior 33, yielding 73 mapped fields / 9 candidate concepts within EDUCATIONHISTORY. The complete 1,105-field ledger remains explicit: 1,028 mapped, 73 still `deferred_source_review`, three linkage keys excluded and one version field excluded. The counts should be regenerated from the ledger if future mappings change.

## Interpretation and data safeguards

- Do not turn Codebook `No %` / `OBS` summaries into released values or descriptions of the participant-level dataset.
- Questionnaire routing defines denominators: grade achieved follows non-graduation; interruption details are routed by affected stage; high-school examination items are conditional.
- E013 describes the last primary school's nominal duration, not a harmonized years-of-education measure. E022/E033 are recalled classmate progression categories, not individual attainment or school-quality measures.
- Multi-select reasons are not independent causal estimates; unchecked or absent options are not automatically No. Free-text responses and school names/addresses remain out of the public atlas.
- Codebook summaries show unusual grade values in E013_1/E021/E032; those need authorized-data QA before any analysis and are not recoded here.
- Life History is a special retrospective survey without its own weight per the official release note. Keep it outside routine-wave weighted ExWAS until a defensible target population, linkage, and design strategy is specified.

## Files and build state

- Updated catalog: `site-prototype/dist/life_history_exposures_v1.json` (77 concepts / 1,842 mappings overall; E 1,796, P 46).
- Updated complete source ledger: `audit/life_history_education_history_coverage_2014_v1.csv`.
- Source questionnaire: `sources_official/CHARLS_Life_History_Questionnaire.pdf`, pp. 71–75; Codebook: `sources_official/CHARLS_Life_History_codebook.pdf`, EDUCATIONHISTORY section (field identities and summaries only; summary frequencies not used).
- The expanded candidate list is metadata only; no participant-level data or association estimates are included.
