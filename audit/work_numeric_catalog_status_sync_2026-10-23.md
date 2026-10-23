# Employment continuous-field source-status synchronization (2026-10-23)

The full metadata pipeline had 847 E/P catalogue rows still marked `not yet reviewed`. A record-level match against `audit/work_exposure_value_labels_v1.csv` found 170 unique wave-field entries in the employment/work-organization exposure category whose audited source status explicitly says the official wave Codebook contains the field but has no discrete response categories (or explicitly reviewed continuous date components). The source table gives an exact CHARLS wave/code and its official Codebook/questionnaire path.

The catalog builder now carries these source statuses and citations into the main field catalogue only when the category label is blank and the source status matches a narrow allowlist. It does not create category labels, infer units from frequencies, or alter candidate mappings or analysis eligibility. The website renders the state in Chinese and explains that continuous/open response semantics, units, and routes still require review. A regression test covers 2011 `fe002`, 2018 `fd021_1`, and 2020 `fc026`.

After regeneration, 677 E/P rows remain generically `not yet reviewed`; 339 rows now carry this precise work-field status overall, including 170 previously generic rows. The total with nonempty reviewed/official labels remains 3,199; the update is source-status transparency, not 170 new categorical variables. No respondent-level records or frequencies were used and no association models were fit.

Validation: `python -u scripts/build_ep_atlas_metadata.py --finalize-only` completed; `python -m unittest discover -s tests -v` passed 83 tests; `node --check site-prototype/dist/app.js`, `node tests/test_deferred_asset_loader.cjs`, and `git diff --check` passed.
