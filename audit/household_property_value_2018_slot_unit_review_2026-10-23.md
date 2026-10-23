# CHARLS 2018 household property value slot/unit review

## Decision

The Wave 4 household property value fields use **measure first, property slot second**. The official Codebook names selectors `ha004_w4_1_` through `ha004_w4_7_`; amount fields are `ha004_w4_1_[slot]_` for total value (slots 1–7) and `ha004_w4_2_[slot]_` for unit value (slots 1–5). The questionnaire reports total price in 10,000 Yuan and unit price in 1,000 Yuan per square metre.

The previous classifier interpreted the two digits in the opposite order. It misclassified `ha004_w4_1_2_` and `ha004_w4_2_1_`, and omitted eight amount fields: total-value slots 3–7 and unit-value slots 3–5. The classifier now matches the official order and accepted slot ranges.

The seven selector fields are response-format metadata, not exposures. They are reclassified from E to C and carry only official category text (`1=Total Value; 2=Unit Value`); Codebook frequencies are omitted. The amount fields remain distinct E candidates by measure and slot. Total and unit-area prices are incompatible quantities and must not be pooled or converted without a verified area and selector route.

## Source and implementation

- `sources_official/CHARLS_2018_Questionnaire_extracted.txt`, HA004 current household property market-value question: total price versus unit price and their reporting units.
- `sources_official/CHARLS_2018_Codebook_extracted.txt`, HA004 selector categories and amount variable names/slot coverage.
- `scripts/build_housing_exposure_crosswalk.py` corrects classifier order and assigns questionnaire reporting units.
- `audit/catalog_role_override_review_v1.csv` moves each of the seven selectors to C metadata.
- `scripts/apply_catalog_role_overrides.py` removes selector concept mappings and applies the official response labels.
- `scripts/apply_2018_household_property_value_review.py` propagates the reviewed units and slot/routing caveats to the candidate catalog, concept-source index and housing lookup.

No respondent-level CHARLS records or Codebook frequencies were used. Codebook descriptive extrema are not treated as analytic ranges; special values, bracket semantics, and eligible denominators still require verification against the authorized analysis release.

## Validation

The full metadata pipeline completed. Regression tests verify all 12 amount fields, exact concept/unit assignment, all seven C-role selectors, and their labels. The project suite passed 108 tests; `node --check site-prototype/dist/app.js` and `git diff --check` passed. Formal association models remain at zero.
