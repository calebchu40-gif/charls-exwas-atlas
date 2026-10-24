# Agricultural workplace location review — 2026-10-25

Reviewed official questionnaire and Codebook sources for own-household agricultural-work locations (`FC012`, 2011–2018; `FB001`, 2020) and paid agricultural-work location (`FC003`, 2011/2013). These are distinct work routes and concepts. Categories are coarse self-reports about where work usually occurs; they are not environmental concentrations, personal doses, commutes, or verified geocodes. Wave-specific response categories must remain separate.

The 2011 instruments instruct interviewers to record `0` when there is no fixed address; the value requires release-level validation. The 2020 own-farm item has a `999` refusal response and includes an option covering Hong Kong, Macao, Taiwan, or abroad. Several instruments contain subfields for place names. The public atlas contains only categorical metadata and deliberately excludes those address/place-name strings. Before analysis, verify the relevant work-route denominator, special values, variable identity and person linkage in the authorized release. No respondent records or Codebook frequencies were used.

Reproduce the review with `python scripts/apply_agricultural_workplace_context_review.py`; it validates source anchors and synchronizes seven field-wave records across domain metadata, the E/P source index and the public JSON payload.
