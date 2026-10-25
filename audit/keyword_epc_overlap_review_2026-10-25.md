# Exact source-verified E/P overlaps among generic C keyword hits (2026-10-25)

## Scope

The C catalogue is a search aid for measurement, route, design, and possible adjustment context; a C label does not establish confounder status. We found 50 C rows marked only as automated keyword discovery that also had an exact same-wave E or P field mapping. We linked 35 rows only when the exact field code was present in both that wave's official extracted Questionnaire and Codebook and the E/P crosswalk had one unambiguous exact wave+module match. The reproducible field-level list is [`keyword_epc_overlap_review_v1.csv`](keyword_epc_overlap_review_v1.csv); the updater is [`apply_keyword_epc_overlap_review.py`](../scripts/apply_keyword_epc_overlap_review.py).

The 35 rows cover smoking initiation/cessation (6), alcohol start/stop (6), education attainment (6), current hukou type (5), sleep duration (3), current hukou location (3), prostate illness (3), and three one-row concepts (prior-wave education, prior-interview hukou-location relation, and recent-stroke age). Wave distribution: 2011 (4), 2013 (10), 2015 (8), 2018 (9), 2020 (4).

## Review boundary

Both official sources corroborate field identity, not respondent-level storage, eligible denominators, or analysis readiness. Existing E/P response labels, units, and mapping statuses remain intact; this update adds the link and source references without recoding responses. The C entry is explicitly metadata-only. A field must not be used as a covariate in its own focal association; any other adjustment role requires an estimand-specific causal rationale. This work does not create a default covariate set.

Fifteen other generic C hits remain unlinked because at least one exact field code could not be independently located in both the extracted Questionnaire and Codebook, or because the existing source evidence does not support a unique same-wave E/P link. In particular, 2011 `DA057_8_` is not promoted based on later-wave analogues; 2011 brain/intellectual-disability fields and the 2018 disability follow-up fields retain their existing source limitations. The updater hard-codes the reviewed key set so that new candidate rows cannot be silently included.

No respondent-level values, Codebook frequencies, association models, or analytic sample sizes were used. The E/P/C catalogue remains 4,845/2,082/982 rows and the exact 92-entry analysis lock set is unchanged.
