# Exact source-verified E/P overlaps among generic C keyword hits (2026-10-25)

## Scope

The C catalogue is a search aid for measurement, route, design, and possible adjustment context; a C label does not establish confounder status. We linked 40 rows only when the exact field code was present in both that wave's official extracted Questionnaire and Codebook and the E/P crosswalk had one unambiguous exact wave+module match. Five additional 2011 Codebook fields were verified after recognizing that the source PDF extraction changes `_` before a numeric suffix into a space (for example, `da070_2` becomes `da070 2`); the updater recognizes only an exact normalized Codebook bullet heading. The separate 2011 social-activity frequency field is audited under [`social_exposure_c_overlap_review_2026-10-25.md`](social_exposure_c_overlap_review_2026-10-25.md), where its parent-question route and source-version discrepancy are retained. The reproducible field-level list is [`keyword_epc_overlap_review_v1.csv`](keyword_epc_overlap_review_v1.csv); the updater is [`apply_keyword_epc_overlap_review.py`](../scripts/apply_keyword_epc_overlap_review.py).

The 40 rows cover smoking initiation/cessation (8), alcohol start/stop (8), education attainment (6), current hukou type (5), sleep duration (3), current hukou location (3), prostate illness (4), and three one-row concepts (prior-wave education, prior-interview hukou-location relation, and recent-stroke age). Wave distribution: 2011 (9), 2013 (10), 2015 (8), 2018 (9), 2020 (4).

## Review boundary

Both official sources corroborate field identity, not respondent-level storage, eligible denominators, or analysis readiness. Existing E/P response labels, units, and mapping statuses remain intact; this update adds the link and source references without recoding responses. The C entry is explicitly metadata-only. A field must not be used as a covariate in its own focal association; any other adjustment role requires an estimand-specific causal rationale. This work does not create a default covariate set.

The earlier inventory had 50 generic keyword-only C/E/P overlaps. Five additional E/P links were confirmed through exact normalized 2011 Codebook headings, and the 2011 `DA057_8_` overlap was separately confirmed and linked in the social-exposure review. The current C catalogue retains nine generic keyword-only rows; they remain unlinked wherever dual-source exact-field evidence or a unique same-wave E/P mapping is missing. Brain/intellectual-disability follow-ups and several diagnosis-history fields retain their source limitations. The updater hard-codes the reviewed key set so that new candidate rows cannot be silently included.

No respondent-level values, Codebook frequencies, association models, or analytic sample sizes were used. The E/P/C catalogue remains 4,845/2,082/982 rows and the exact 92-entry analysis lock set is unchanged.
