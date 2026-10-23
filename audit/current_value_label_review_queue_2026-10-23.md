# Current value-label review queue (2026-10-23)

This snapshot reads only the public, generated metadata in `site-prototype/dist/catalog_{e,p,c}.json`. It contains no respondent records or response frequencies. “Not yet reviewed” is the catalog value-label review field; it does not mean every row should receive a discrete category label, and it is separate from E/P analysis eligibility.

| Role | Catalog rows | Generic `not yet reviewed` rows |
|---|---:|---:|
| E exposure candidates | 4,722 | 624 |
| P phenotype candidates | 2,067 | 0 |
| C covariate/measurement metadata | 914 | 329 |

The E queue divides into four domains: social determinants 390, housing and built environment 95, food and household environment 73, and social protection 66. The largest subgroups are income/wealth/material resources (140), social relations and care (88), dwelling conditions/property (95), food security/utilities (73), household expenditure (53), transfer income (50), and individual income/wages (45). These are field rows, not independent concepts or tests.

## Processing rule

Continue by source-backed field families. For each field, establish whether its official questionnaire and Codebook define a categorical response, a continuous amount/count/date, an open response, a routed component, or a special missing code. Add categories only when the official source supports the exact wave-field mapping; omit frequencies. For numeric/open fields, replace the generic pending state only when the source record is located and its measurement meaning can be stated. Preserve conflicting labels and existing `DO NOT ANALYZE` locks. A blank category list is not itself an error for a continuous measure.

## Next review batches

The immediate high-yield batches are the remaining housing/property fields (95 rows) and household food/security/utilities (73 rows), followed by the 66 social-protection fields. Each batch needs questionnaire scope, response unit, household/person measurement level, wave comparability, and Codebook storage semantics checked together. Income/wealth and household-member roster amounts remain a larger follow-on group; their numerous amount slots must not be counted as independent exposures without a construct-level rationale.

The 2018 current-home owner-relation batch is now reviewed at the response-label level: one of nine fields has a complete Codebook 0/1 label set; eight show only the `0=Do Not Own` category in the extracted Codebook and are marked partial without guessing the missing category. No frequencies were copied. See [`housing_current_owner_relation_labels_2018_v1.csv`](housing_current_owner_relation_labels_2018_v1.csv) and [`housing_current_owner_relation_labels_2018_review_2026-10-23.md`](housing_current_owner_relation_labels_2018_review_2026-10-23.md). The E generic-pending count is now 624.

This queue snapshot is descriptive and does not change the current formal model count (0) or overall result-atlas completion estimate (25%–30%).
