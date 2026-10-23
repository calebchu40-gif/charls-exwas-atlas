# Pension bracket endpoint review (2011–2015)

This review covers 16 lower/upper endpoint fields attached to conditional pension benefit or contribution questions. The official wave questionnaires and Codebooks were checked; no participant data, Codebook frequencies, means, or extrema were copied into the website. The repeatable updater is `scripts/apply_pension_interval_endpoint_review.py`.

| Wave | Fields | Measurement meaning and source detail |
|---|---:|---|
| 2011 | 12 | Six item-specific min/max pairs (`fn005`, `fn008`, `fn014`, `fn019`, `fn023`, `fn037`). The first five pairs concern pension benefit/contribution routes; `fn037_a/b` are expected monthly benefit bounds under a conditional defined-contribution plan. Preserve each pair and route. |
| 2013 | 2 | `fn035_w2_bracketbracket_min/max` are bounds for the combined monthly contribution from respondent and employer, not the respondent-only contribution or percentage field. The Codebook explicitly calls the endpoint fields strings. |
| 2015 | 2 | `fn035_w2_bracket_min/max` are bounds for the combined monthly contribution amount. The Codebook provides numeric summary statistics, but those summaries are not response categories, data type confirmation, or valid analytic cutoffs. |
| **Total** | **16** |  |

These variables encode interval bounds for conditional follow-up questions. They are not discrete response categories, direct point estimates, or independent measures that can be averaged. Keep lower and upper endpoints together, preserve the question route and plan identity, and do not midpoint-impute or coerce string fields until the authorized release dictionary confirms representation. The 2011 Codebook summary extrema and all wave soft checks are excluded from analytic range rules. Special codes, route denominators, actual stored types, and analysis eligibility still need authorized-release QA.

