# Child schooling metadata review

This review uses only official questionnaires, Codebooks, and the public raw variable inventory. It does not read participant values or publish response frequencies.

## E candidates

`child_education_context_crosswalk_v1.csv` records four child schooling candidates. Three are 2013 Child-module candidates: current school attendance (`cb058`), years spent in primary school (`cb061`), and additional schooling years after the selected education category (`cb062`). A fourth field, years spent in sishu/home school (`cb060_w2_1`), is listed under the 2013 `Family_Information` module, despite the questionnaire asking the item for a named child. The questionnaire routes it only after the highest-education item selects sishu/home school. Keep numeric years separate from attainment categories, preserve the exact route, and verify the wide-field slot/child-record mapping, special values, and eligible denominator in the authorized release.

## C-only source conflicts

`child_education_source_conflict_crosswalk_v1.csv` keeps two fields out of E/P while sources disagree:

- 2013 `cb059`: the questionnaire asks current enrolled grade/level, while extracted Codebook slot labels assign value 4 to both primary grade 3 and grade 4.
- 2015 `cb052_w3_1`: the questionnaire asks whether the child is literate (Yes/No), while the Codebook slot label describes highest education attainment and an eleven-category menu.

Do not infer categories or run associations for these fields until an official field-level mapping resolves the discrepancies. The Codebook and questionnaire refer to numbered child slots; neither supplies a one-to-one link to the record-level Child field. Preserve childID linkage and account for within-respondent clustering if any later analysis is approved.

## Official sources checked

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`
- `sources_official/CHARLS_2013_Codebook_extracted.txt`
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`
- `sources_official/CHARLS_2015_Codebook_extracted.txt`
- `audit/raw_variable_catalog_v1.csv`
