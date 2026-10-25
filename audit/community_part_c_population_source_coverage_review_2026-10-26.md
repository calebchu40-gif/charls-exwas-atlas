# CHARLS 2011 Community Questionnaire Part C population-source coverage review

## Scope and inventory

Reviewed Part C, “Population, Labor” (printed pp. 14–16; PDF pp. 17–19), against the official questionnaire, Codebook, and metadata-only raw-field inventory. The section is to be answered by the person most familiar with local population and employment. The inventory contains 39 JC-prefixed fields: 24 are newly mapped to five provisional community-context E concepts; the 12 existing adult-education percentage/fallback fields remain mapped to `community_education_profile`; and three fields are kept C-only metadata.

## New E candidate mappings

| Concept | Fields | Scope and interpretation |
|---|---|---|
| `community_population_hukou_profile` | JC001–JC005, JC003_1, JC004_1, JC005_1, JC007–JC008 (10) | 2009–2010 community counts with distinct residence-duration, hukou, person/household definitions. Do not derive a rate or combine counts without validating denominator consistency. |
| `community_short_term_migrant_population` | JC006 (1) | 2010 year-end count living locally for less than half a year; distinct from JC001's more-than-half-year residents. |
| `community_age_sex_structure` | JC009–JC011 and male-count follow-ups JC009_1, JC010_1, JC011_1 (6) | Community counts for adults aged 16+, people aged 65+, and people aged 80+; preserve nested age groups and separate male counts. |
| `community_never_married_over40_population` | JC012, JC012_1 (2) | Community-informant count using the official over-40 never-married item wording, with a separate male count; not a sampled participant's marital status. |
| `community_ethnic_minority_household_profile` | JC013, JC013_1, JC015, JC017, JC018 (5) | Minority-group presence/count and household counts for the largest, second-largest and remaining groups; no population denominator is provided. |

Counts are community-level contextual candidates, not participant-level exposures, phenotypes, covariate recommendations, or analytic denominators. They are one-wave measures and do not establish an individual's residence, hukou, age, sex, marital status, or ethnicity.

## C-only dispositions

- JC014 and JC016 ask for open-text names of the largest and second-largest minority groups. They are not standardized categories and are retained only as metadata; no response text is published or analyzed.
- JC026 records the role of the community-questionnaire informant. It is not the sampled CHARLS participant's occupation or covariate.

## Harmonization and analysis limits

JC001/JC003/JC004/JC005/JC006/JC007/JC008 have different residency and hukou definitions. JC003–JC005 also distinguish person and household counts. JC009 defines adults as age 16 and above; JC010 and JC011 are nested thresholds. JC013=No routes to JC019, so subsequent minority items are structurally skipped, not negative responses. Verify special values, eligible routes, field-level release coding, community–participant linkage, cluster handling, and survey design before any analysis. No Codebook frequencies, response distributions, respondent records, or derived rates were used.

Sources: `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt` (Part C), `audit/CHARLS_2011_Codebook_extracted.txt` (JC001–JC026), and `audit/raw_variable_catalog_v1.csv`. Generated mapping: `audit/community_exposure_crosswalk_v1.csv`; public metadata: `site-prototype/dist/community_exposures_v1.json`.
