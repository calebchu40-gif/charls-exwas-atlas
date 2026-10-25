# Hukou life-course C/E overlap review (2026-10-25)

This review connects exact 2011/2013 field-wave records already present in the E and C roles. The links preserve a historical/social-context candidate for search; they do not identify environmental pollutant dose, establish an analytic denominator, or recommend a fixed covariate set. A focal field cannot adjust for itself. Numeric response codes are wave-specific and must not be pooled as if categories were identical.

| Wave | Field | Candidate concept | Official sources |
|---|---|---|---|
| 2011 | `bc007` | `hukou_first_current_same` | CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; CHARLS_2011_Codebook_extracted.txt |
| 2013 | `bc007` | `hukou_first_current_same` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2011 | `bc008` | `intermediate_hukou_existence` | CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; CHARLS_2011_Codebook_extracted.txt |
| 2013 | `bc008` | `intermediate_hukou_existence` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2011 | `bc009` | `hukou_type_place_change` | CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; CHARLS_2011_Codebook_extracted.txt |
| 2013 | `bc009` | `hukou_type_place_change` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2011 | `bc010` | `first_hukou_type` | CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; CHARLS_2011_Codebook_extracted.txt |
| 2013 | `bc010` | `first_hukou_type` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2011 | `bc012` | `hukou_last_location_reason` | CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; CHARLS_2011_Codebook_extracted.txt |
| 2013 | `bc012` | `hukou_last_location_reason` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2011 | `bc015` | `nonagricultural_hukou_reason` | CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; CHARLS_2011_Codebook_extracted.txt |
| 2013 | `bc015` | `nonagricultural_hukou_reason` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2011 | `bc017` | `agricultural_hukou_reason` | CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; CHARLS_2011_Codebook_extracted.txt |
| 2013 | `bc017` | `agricultural_hukou_reason` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2011 | `bc002` | `hukou_status_before_unification` | CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; CHARLS_2011_Codebook_extracted.txt |
| 2013 | `bc002` | `hukou_status_before_unification` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |

The source crosswalk provides the reviewed response labels and conditional-route caveats. `BC007`/`BC008`/`BC009` and downstream historical items have different skip paths; `BC010`, `BC012`, `BC015`, and `BC017` are conditional history details; `BC002` is asked only of respondents currently classified in the unified residence-hukou category. These are retrospective, self-reported hukou constructs, not geocoded migration histories or current residence exposures. Eligibility and release-specific missing/skip codes remain to be checked before any analysis.

The updater checks exact wave, field, module, and both E/C roles. It requires the same field code in an official Questionnaire and Codebook file, retains source labels and route caveats, and leaves rows in C metadata. The regression test confirms all 16 exact links survive both metadata pipelines and are present in the public C shard. No participant records or Codebook descriptive frequencies were used.
