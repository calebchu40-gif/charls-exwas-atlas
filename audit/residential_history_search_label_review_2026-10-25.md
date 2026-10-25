# Residential-history C search-label reconciliation (2026-10-25)

## Scope and result

The final C catalogue contained 18 2011–2015 age/mobility fields whose official Questionnaire and Codebook sources, routed question meaning, and measurement notes had already been reviewed, but whose display subcategory still said only “keyword discovery.” Replaced that stale label with field-specific, wave-aware residential-history or respondent-age metadata labels. Updated the wave-field candidate catalogue, aggregated concept-series catalogue, and public C catalogue through [`apply_residential_history_search_label_review.py`](../scripts/apply_residential_history_search_label_review.py).

The 18 rows cover two respondent-age entries and sixteen residential-history entries across nine source codes. Year/month durations remain separate; BB007 and BB009 remain distinct branches; first residence in a county/district remains distinct from first residence in a village/community. The two 2011 `bb003`/`bb005` field-identity holds were not relabeled or unlocked. The new labels classify search metadata only: they do not approve a covariate, exposure, outcome, or association model.

## Reproducibility and checks

The updater uses a frozen wave/code allowlist, requires existing Questionnaire and Codebook provenance and a non-generic source-review status, and checks that only the known stale generic labels are replaced. It runs in both full and finalize-only metadata pipelines before the final C shard is generated. The site translates each new English subcategory to a Chinese display label and retains the original source-specific explanation.

The first full-suite run exposed that the website's closed Chinese label dictionary did not yet contain these eleven new field-level subcategories. Added explicit translations and a regression test; targeted tests, public-payload validation, exact 92-lock reconciliation, JavaScript/Python syntax checks and whitespace checks then passed. Full-suite verification is recorded in the release changelog. No respondent-level data, codebook frequencies or analytic sample sizes were used.
