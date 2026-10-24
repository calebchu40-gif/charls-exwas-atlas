# CHARLS 2020 physical-activity duration source review

Updated: 2026-10-25. Scope: official Chinese and English Wave 5 questionnaires, Chinese flowchart, and Codebook. No respondent records or frequency tables were copied into the catalogue.

## Source reconciliation and routing

The activity module asks about usual weekly activity lasting at least 10 minutes. For each intensity `i` (intensive, moderate, light), `DA032[i]` records whether the activity occurred, `DA033[i]` records days per usual week, `DA034[i]`–`DA036[i]` are conditional duration bands, and `DA037[i]` asks the activity purpose. These are routed components of one wave-specific module, not independent doses.

The official Chinese questionnaire (PDF p.36, printed p.30) gives `DA034` as `<2`/`≥2 hours`, `DA035` as `<30`/`≥30 minutes`, and `DA036` as `<4`/`≥4 hours`. The Codebook agrees with these response labels. The English questionnaire prints “30 hours” for `DA035`; this is a translation discrepancy and is superseded by the matching Chinese questionnaire and Codebook wording for interpreting the item.

The official Chinese flowchart (PDF p.30, printed p.24) resolves the route: `DA032=Yes` proceeds to `DA033` and then `DA034`; a `DA034` response `<2 hours` routes to `DA035`, while `≥2 hours` routes to `DA036`; both continue to `DA037`. The activity-intensity index remains attached to each field. This confirms questionnaire routing, not the released file's exact field identity, storage, special values, or analytic eligibility.

The directory now displays reviewed `DA035` labels and documents the English translation discrepancy. It preserves the conditional route and denominator and does not combine the three duration fields, convert categories to exact minutes, derive weekly totals, apply an IPAQ formula, or claim equivalence with 2011–2018 measures. Authorized-release field and special-code QA remains required before analysis.

## Reproducible changes

`scripts/build_behavior_exposure_crosswalk.py` records the official conditional route and translation discrepancy. `scripts/enrich_behavior_value_labels.py` uses the Codebook response labels and cites the Chinese questionnaire and flowchart. `scripts/build_charls_atlas_catalog.py` propagates the reviewed labels to the E catalogue. Regression tests compare the audit, source text, field mapping, public catalogue, topic browser, and candidate-pair payload; they also guard against publishing Codebook frequencies.

## Sources

- Official [CHARLS 2020 Chinese documentation page](https://charls.charlsdata.com/pages/Data/2020-charls-wave5/zh-cn.html).
- `sources_official/CHARLS_2020_Questionnaire_Chinese.pdf`, PDF p.36 (printed p.30), SHA-1 `307FB0F902E76FD08E07222324A4CE5FA24FEC99`; extracted text is a search aid.
- `sources_official/CHARLS_2020_Flowchart_Chinese.pdf`, PDF p.30 (printed p.24), SHA-1 `83DA535E9542AD6974FF3474B7FE0FCDED0ED0BD`; extracted text is a search aid. The conditional route was read from the official page diagram.
- `sources_official/CHARLS_2020_Codebook_extracted.txt`, entries `da034_1_`–`da036_3_`; response labels only, with Codebook frequencies excluded from the site.
- `sources_official/CHARLS_2020_Questionnaire_English.pdf`, p.32 and extracted lines 1109–1132, retained to document the translation discrepancy.
