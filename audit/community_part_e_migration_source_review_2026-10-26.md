# CHARLS 2011 Community Questionnaire Part E migration source review

## Inventory reconciliation

Reviewed Part E, “Migration” (printed pp. 19–20; PDF pp. 22–23), against the official 2011 Community Questionnaire, official Codebook field labels, and metadata-only `audit/raw_variable_catalog_v1.csv`. The raw inventory contains 46 JE-prefixed fields. Forty-four questionnaire-anchored fields are mapped to eight provisional community-context E concepts. `JE014` is retained as C-only informant metadata, and `JE016` is retained as C-only unresolved source metadata because it appears in the Codebook but the questionnaire section ends at JE015 and contains no corresponding item. Questionnaire prompts for respondent name (JE013) and telephone number (JE015) are direct identifiers and are absent from the raw inventory/public catalog; no responses or open text are processed.

## Candidate concepts

| Concept | Fields | Definition and boundary |
|---|---|---|
| `community_outmigration_workforce_profile` | JE001–JE002 | Village-only counts of people working outside the village for more than three months in 2010 and the female percentage among them. Keep the person count and reported share distinct. |
| `community_outmigration_geographic_distribution` | JE003–JE006 | Five-band reported shares working in other townships in the county, other counties in the prefecture/city, other prefectures/cities in the province, or other provinces. Keep geographic levels separate; bands are ordinal, not exact percentages. |
| `community_outmigration_destination_provinces` | JE007S1–JE007S33 | Main provincial destinations, recorded as multiple-response source slots. Thirty-two slots have Codebook province labels; JE007S33 is marked “No Observations” with no label and remains unresolved. Do not infer an unselected response as No without release-specific coding evidence. |
| `community_male_migrant_occupation_profile` | JE008 | Codebook-coded nominal category for the main occupation sought by male migrants. Categories are retained without frequencies and are not ordered. |
| `community_male_migrant_average_wage` | JE009 | Community estimate of male migrants’ average monthly wage; Yuan/month. |
| `community_female_migrant_occupation_profile` | JE010 | Codebook-coded nominal category for the main occupation sought by female migrants. Categories are retained without frequencies and are not ordered. |
| `community_female_migrant_average_wage` | JE011 | Community estimate of female migrants’ average monthly wage; Yuan/month. |
| `community_permanent_household_outmigration` | JE012 | Community count of households said to have permanently moved out since 2000; the questionnaire defines this via household-registration transfer. |

All mapped items are village-only reports about community-level migrants, not migration, occupation, or wages of sampled CHARLS respondents. The migration-work measures refer to 2010; JE012 has a separate retrospective period beginning in 2000. Do not derive exact shares, combine destination levels, derive a sex wage gap, infer individual destinations, or treat the aggregate as an individual exposure without an explicitly justified linkage and estimand.

## C-only and unresolved source fields

- `JE014` is the identity/position of the Part E community informant, not a sampled participant covariate. The questionnaire labels it Part E; the Codebook title says Part D. The source conflict is retained.
- `JE016` is titled “Num. of Households Moved in Since 2000” in the Codebook but has no corresponding item in the official Part E questionnaire. Its direction and meaning cannot be reconciled from the available sources, so it is not assigned an E/P construct.
- JE013 respondent name and JE015 telephone are direct-identification prompts. They are excluded and not processed. The questionnaire’s JE014_1 “Other, specify” follow-up does not appear as a raw inventory variable; no text is inferred or published.

## Labels, analysis limits and provenance

JE003–JE006 questionnaire percentage bands and Codebook occupation/province labels are recorded without frequency counts. The label builder previously skipped all `JE` Codebook fields; its prefix allowlist now includes `je`, and the explicit percentage bands plus the unresolved JE007S33 status are maintained in `community_questionnaire_label_overrides_v1.csv`. The crosswalk builder verifies each candidate source code in both official questionnaire text and Codebook, normalizing JE007S1–S33 to the JE007 questionnaire anchor.

These additions are metadata candidates only. They do not establish valid special/missing codes, release storage, an appropriate community-to-person linkage, cross-wave comparability, sample denominators, survey-weight eligibility, or any association result. No participant-level values, Codebook frequencies, extrema or response distributions were used.

Sources: `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt` (Part E); `audit/CHARLS_2011_Codebook_extracted.txt` (JE fields); `audit/raw_variable_catalog_v1.csv` (metadata-only inventory). Generated outputs: `audit/community_exposure_crosswalk_v1.csv`, `audit/community_exposure_value_labels_v1.csv`, and `site-prototype/dist/community_exposures_v1.json`.
