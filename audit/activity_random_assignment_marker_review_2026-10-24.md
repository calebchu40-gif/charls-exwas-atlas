# Physical-activity randomized-module assignment marker review

## Decision

The released 2013 and 2015 `da051_random` fields are now catalogued as C-only design metadata. They are excluded from the E/P association matrix and carry no value labels. The public catalogue explicitly says that the marker's released code-to-eligibility meaning is unresolved. Do not use its 1/2 values or missingness to define respondent/household eligibility, an analysis denominator, or weight applicability.

## Official-source evidence

- The 2013 questionnaire says DA051 is presented to a random subsample of half of households and that the main respondent and spouse in selected households answer the activity block. See `sources_official/CHARLS_2013_Questionnaire_extracted.txt`, around lines 3036–3044.
- The 2015 questionnaire describes the same random-half-household routing for DA051–DA055. See `sources_official/CHARLS_2015_Questionnaire_extracted.txt`, around lines 2436–2443.
- The 2013 and 2015 Codebooks identify the released field as `da051_random : Ca052Random` / `da051_random: Ca052Random`. The Codebooks do not provide a reviewed mapping that establishes which released code means selected versus not selected. See `sources_official/CHARLS_2013_Codebook_extracted.txt` around line 16646 and `sources_official/CHARLS_2015_Codebook_extracted.txt` around line 16051.
- The official Harmonized CHARLS D Codebook also describes the Wave 1–3 activity module as a random half-household subsample and the later waves as broader coverage. The Atlas retains wave-specific routing and does not claim that the 2018/2020 route or any weight is interchangeable with the earlier module.

## Catalog implementation

`audit/catalog_role_override_review_v1.csv` registers the 2013 and 2015 rows as C metadata. `scripts/apply_catalog_role_overrides.py` assigns a dedicated subcategory, preserves the official questionnaire and Codebook source paths, withholds code labels, and repeats the unresolved-code and denominator warning in the public row. The catalog does not expose response values, code frequencies, private QA counts, or respondent-level information. The 2011 prepared source catalog has no corresponding released marker, so no analogous 2011 field was invented.

The local aggregate-only diagnostic under the protected QA directory was not copied into the repository or website and was not used to infer code meanings. Until the released marker is reconciled to official routing documentation, activity candidate analyses must derive eligibility and weights from verified wave-specific source definitions under authorized data access; blanks are not recoded as inactivity.

## Reproducibility

The role override is reapplied by both full and finalization metadata builds. `tests/test_activity_assignment_metadata.py` verifies the official source references, C-only role, withheld value labels, and unresolved eligibility warning. The final public C shard contains both wave rows; E/P candidate counts, pair listings, and the 89 formal analysis locks are unchanged. No model has been fit.
