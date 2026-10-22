# Housing and building response-label reconciliation

This audit transcribes categorical response labels for building structure, building age interval, building floor type, dwelling independence, elevator, accessibility facilities, and entrance steps. It supports catalogue lookup only; it does not establish analysis eligibility, wave comparability, respondent-level code distributions, or valid derived exposure definitions.

## Source and scope

Labels were checked against the official extracted Codebooks in `sources_official/CHARLS_{2011,2013,2015,2018,2020}_Codebook_extracted.txt`. The field roster was checked against `audit/raw_variable_catalog_v1.csv`. Codebook frequency counts and percentages were intentionally excluded from the label strings and are not sample-size or denominator evidence.

The reviewed categorical fields are:

| Wave | Structure | Build-age interval | Floor type | Independent/compound | Elevator | Accessibility | Entrance steps |
|---|---|---|---|---|---|---|---|
| 2011 | i004 | i005_1 | i006 | i007 | i009 | i010 | i011 |
| 2013 | i004 | i005_1 | i006 | i007 | i009 | i010 | i011 |
| 2015 | i004 | i005_1 | i006 | i007 | i009 | i010 | i011 |
| 2018 | i004 | i005_1 | i006 | i007 | i009 | i010_w4 | i011 |
| 2020 | i001 | i003 | i004 | i005 | i007 | i009 | continuous i010 |

The follow-up pass also reviewed the household telephone and broadband indicators and air-cleaner ownership:

| Construct | 2011 | 2013 | 2015 | 2018 | 2020 |
|---|---|---|---|---|---|
| Telephone connection | i023 | i023 | i023 | i023 | i022 |
| Broadband connection | i024 | i024 | i024 | i024 | i023 |
| Air cleaner in residence | not mapped in this review | not mapped in this review | i027_w3 | i027_w3 | i024 |

Additional residence-context fields included after codebook and questionnaire review are 2011–2018 `i003` (whether the residence is also used for business), 2018 `i000_w4_2` (residence location category), 2018 `i000_w4_3` (house type), and 2020 `i027` (floor/ground condition). The 2018 location and house-type fields are a single-wave questionnaire module; they are not harmonized to the NBS urban/rural identifier or to other waves by label similarity.

A further field-level pass covers interviewer-observed home cleanliness (`i025`) and temperature (`i026`) in all five waves, plus 2020 tap-water access (`i016`) and whether tap water is treated by waterworks (`i029`). These are distinct constructs: cleanliness/thermal comfort are interviewer-recorded household observations, tap-water access is not water-quality testing, and `997=Do not know` remains a substantive response category for the 2020 treatment question. The 2011 Codebook does not list the `6=Not applicable` category shown from 2013 onward, so it is not backfilled into 2011.

## Wave differences retained

- 2011 structure uses codes 1–10, including code 8 `Tent`. The 2013 Codebook category table lists 1–7, 9, and 10; code 8 is not imputed from the prior wave.
- From 2015, structure is recoded to categories 1–7. The 2015 Codebook spells the final word of category 5 as `Tend`; the lookup records that source spelling. Later Codebooks spell it `Tent`.
- Floor type has two categories in 2011/2013 and three from 2015 onward.
- Accessibility is Yes/No through 2015. The 2018 and 2020 instruments add `3=Do not need`, which remains separate from No.
- Entrance steps are categorized in 2011–2018. In 2020, i010 is a continuous count and is deliberately given no categorical value labels.
- Building-age intervals use codes 1–6 throughout the reviewed waves, but exact upper-bound wording varies slightly by Codebook.
- Telephone, broadband, and air-cleaner response labels are all Yes/No, but the raw source codes shift in 2020. Air cleaner is not mapped for 2011/2013 in this review. The 2018 released name retains the `_w3` suffix; the 2018 questionnaire asks about the current residence, but the suffix and measurement history should remain visible pending approved-data identity checks.

## Use limits

These are display labels for source codes, not harmonized measures. Do not pool wave codes without a separate construct-level review. Do not interpret category code order as a dose scale. Preserve the conditional routes, household/dwelling level, missing/special codes, and wave-specific wording during approved-data analysis. No respondent-level microdata were read for this label review.

The generator is `scripts/build_housing_value_label_review.py`; the values flow into the main field catalog, the candidate concept-source crosswalk, and the housing lookup JSON. Regression checks are in `tests/test_housing_value_labels.py`.
