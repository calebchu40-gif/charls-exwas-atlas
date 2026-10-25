# CHARLS 2011 Community Questionnaire Part F mortality-context source review

## Source coverage

Reviewed Part F JF017–JF021 (questionnaire printed pp. 23–24; PDF pp. 26–27), official Codebook field labels, and the metadata-only 2011 community inventory. The question defines a three-year retrospective period beginning in 2008 and asks community/village informants for aggregate death counts. These are not linked CHARLS participant outcomes.

## Provisional community-context E candidates

| Concept | Field | Source definition |
|---|---|---|
| `community_total_deaths_3y` | `jf017_1` | Total deaths in the village/community in the past three years (since 2008), in persons. |
| `community_suicide_deaths_3y` | `jf017_2` | Deaths attributed to suicide in the village/community during the same period, in persons. |

Neither item supplies a population denominator in this question. Do not calculate a mortality rate, infer participant deaths, or treat the aggregate as an individual's outcome. Small-community counts may be sensitive; public data contain only field metadata and no response values. Candidate status does not establish analytic eligibility.

## C-only dispositions

- `jf018_1_1_`–`jf018_1_3_`: open-text names of the three major diseases affecting older people's health. They are not standardized disease codes; no text response is published.
- `jf018_2_1_`–`jf018_2_3_`: slot-specific death counts paired to the unstandardized disease names. Kept as C metadata until disease identity, release coding, small-cell disclosure, and denominator are resolved.
- `jf020`: informant identity/role. The questionnaire calls it Part F, while the Codebook field label says “Part D”; retain this source conflict, withhold categories and exclude it from participant covariates.
- JF019 name and JF021 telephone-number questions are direct identifiers and are excluded from the candidate/public catalogue. No response values are present in the raw field inventory used here.

## Harmonization and analysis limits

JF017 counts and JF018 cause-specific slots have different definitions and must not be combined. No denominator, age-standardization, time-at-risk, individual linkage, or complete mortality ascertainment is established. Verify release-specific missing/special codes, community linkage, and disclosure risk before any use. No Codebook frequencies, extrema, response distributions, or participant-level data were used.

Source: `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt` (JF017–JF021) and `audit/CHARLS_2011_Codebook_extracted.txt` (field labels only). Generated mappings: `audit/community_exposure_crosswalk_v1.csv`; public metadata: `site-prototype/dist/community_exposures_v1.json`.
