# Child hukou and location-history source review

This metadata-only review adds candidate social-context fields from the 2013 and 2015 Child modules. It does not analyze respondent or child records.

## Candidate family

`child_hukou_lifecourse_crosswalk_v1.csv` records 13 wave-field candidates across 10 concepts: current hukou location, birthplace category, whether current hukou matches residence or first hukou, type of hukou change, first hukou status/location, pre-unification hukou status, and year of unified-residency hukou registration. These describe a linked child's social and residential history. They are not geocoded exposures, precise environmental doses, or automatically selected covariates.

## Field-linkage boundary

The official raw variable inventory contains the listed field stems in the 2013 and/or 2015 `Child` modules, alongside `ID`, `childID`, and `HHmemberID`. The extracted questionnaire and Codebook document corresponding `Childn`/numbered Family Information items, but do not provide an official one-to-one crosswalk from each numbered slot field to the record-level `Child` field. The Atlas therefore lists candidate item meaning and response menus while keeping direct field identity/coding alignment pending. An authorized release must verify the exact field correspondence, key uniqueness, respondent join, eligibility, skip patterns, special values, and within-respondent clustering before analysis.

2013 and 2015 response menus remain wave-specific. In particular, current hukou-location and birthplace options differ. Address write-ins and precise geographic details are excluded; category labels are reproduced without Codebook frequencies or extrema. Conditional unified-residency follow-ups must not treat a skipped value as a negative or zero response.

## Official sources checked

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`
- `sources_official/CHARLS_2013_Codebook_extracted.txt`
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`
- `sources_official/CHARLS_2015_Codebook_extracted.txt`
- `audit/raw_variable_catalog_v1.csv`

No participant values, Codebook frequencies, or summary extrema were added to the crosswalk or public site. The mappings are discovery candidates, not approved tests, analysis-ready variables, adjustment recommendations, or evidence of association.
