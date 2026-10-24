# CHARLS 2020 physical-activity duration source review

Date: 2026-10-24. Scope: public 2020 English questionnaire and Codebook; no respondent records or frequency tables were copied into the catalogue.

## Field structure and unresolved source conflict

The questionnaire asks about activity in a usual week, retaining activity bouts of at least 10 minutes. `DA032[i]` records whether the respondent did each activity intensity; `DA033[i]` asks the number of days in a usual week; `DA034[i]`, `DA035[i]`, and `DA036[i]` all ask time spent on one of those days; `DA037[i]` asks the activity purpose. The index `i` represents intensive, moderate, and light activity, respectively. These are components within the same wave-specific activity module, not independent environmental exposures.

The printed questionnaire (p. 32; extracted lines 1109–1132) and the official Codebook agree on the `DA034` (<2 hours / ≥2 hours) and `DA036` (<4 hours / ≥4 hours) thresholds. They conflict on `DA035`: the questionnaire prints `<30 hours` / `≥30 hours`, whereas the Codebook labels the responses `<30 minutes` / `≥30 minutes`. The released questionnaire page does not print skip instructions that establish how `DA034`, `DA035`, and `DA036` route into one another. The Codebook summaries suggest conditional fields, but the catalog does not use their frequencies as results or as a substitute for verifying the authorized release's routing and storage.

The site therefore leaves `DA035` value labels blank and marks it `DO NOT ANALYZE` pending official release-level verification. It records the agreed labels for `DA034` and `DA036` with a routing caveat. It does not collapse the fields into minutes, sum them, calculate weekly dose, apply an IPAQ formula, or claim equivalence with 2011–2018 activity measures. The three activity intensities remain separate and preserve the 2020 light-activity wording.

## Reproducible changes

`scripts/build_behavior_exposure_crosswalk.py` now annotates the 2020 activity-duration family with this field structure and conflict. `scripts/enrich_behavior_value_labels.py` attaches exact question locations and withholds the disputed `DA035` labels. `scripts/build_charls_atlas_catalog.py` carries the no-label conflict status into the E catalogue. The regression test checks the CSV, public catalogue, source locator, and behavior topic payload, and asserts that no Codebook frequencies leak into the public metadata.

Sources: `sources_official/CHARLS_2020_Questionnaire_English.pdf` p. 32 and its text extraction lines 1109–1132; `sources_official/CHARLS_2020_Codebook_extracted.txt` entries `da034_1_`–`da036_3_` (response labels only; Codebook frequencies excluded from the site). The questionnaire PDF is also available through the [official CHARLS 2020 data page](https://charls.pku.edu.cn/en/Data/2020-charls-wave5/en.html).
