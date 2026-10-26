# Five-wave CHARLS housing fuel source review

Reviewed 2026-10-24 against each wave's official questionnaire and Codebook. This is a variable-metadata review only. No respondent responses, codebook frequencies, percentages, or derived counts are included.

## Cross-wave field map

| Wave | Heating availability/source | Main cooking fuel | Source-backed distinctions |
|---|---|---|---|
| 2011 | `i020` / `i021` | `i022` | The baseline household questionnaire defines `i020` as heating facilities excluding earth-heating systems and heating-capable air conditioners. Yes skips the heating-source item to `i022`; No proceeds to `i021`. The cooking-fuel categories are in the Codebook; the questionnaire does not provide a separate no-cooking response category. |
| 2013 | `i020` / `i021` | `i022` | The questionnaire repeats the heating route: Yes skips to cooking fuel, No asks the heating source. The 1–7 source categories match the documented earlier-wave categories. No explicit no-cooking category appears for cooking fuel. |
| 2015 | `i020` / `i021` | `i022` | Same heating route and 1–7 categories. “Other, please specify” has a separate write-in field for heating and cooking; the write-in text is not a standardized exposure category. No explicit no-cooking option is listed. |
| 2018 | `i020` / `i021_w4` | `i022_w4` | Heating availability Yes skips to cooking fuel; No asks the source. The questionnaire labels heating code 8 “Concentration heating,” while the Codebook labels it “Heating Provided”; retain this source-label discrepancy. Cooking explicitly includes code 8 “Do not cook.” |
| 2020 | `i019` / `i020` | `i021` | The questionnaire asks about XFinancialResp’s house. Heating source is presented with code 8 “No heating”; do not impose the 2011–2018 skip rule. Cooking adds code 7 “Solar,” moves “Other” to code 8, and uses code 9 “No cooking.” |

The official Codebooks list the heating-source categories for Waves 1–3 as 1 Solar, 2 Coal, 3 Natural gas, 4 Liquefied Petroleum Gas, 5 Electric, 6 Crop residue/Wood burning, and 7 Other. Wave 4 adds its code-8 label as described above. Wave 5 uses 1–7 for the same fuel categories and 8 for no heating. Cooking-fuel codes 1–6 (Coal, Natural gas, Marsh gas, Liquefied Petroleum Gas, Electric, Crop residue/Wood burning) are stable through the first four waves. Wave 5 inserts Solar at 7, shifts Other to 8, and records no cooking at 9. Wave 4 records no cooking at 8. Numeric code positions are wave-specific categories, not a dose scale.

## Interpretation and analysis boundaries

- These are household/residence-reported primary-source categories. They are useful contextual exposure proxies, but CHARLS does not measure the respondent's personal fuel use, combustion concentration, ventilation, ambient pollution, or pollutant dose through these items.
- The 2011–2018 heating-source denominator follows the heating-availability route. In 2020, keep the separately worded heating availability and source item, including the explicit no-heating response. Do not treat structural skips as a negative source category.
- Do not convert a blank cooking response in 2011–2015 into “does not cook”; that category is explicit only in 2018 and 2020. Retain “other” write-ins separately and do not publish or normalize unstandardized text.
- The 2020 household referent is XFinancialResp’s house. Confirm the household-to-person linkage and intended estimand before attaching this contextual measure to an individual.
- Do not infer cross-wave changes from category codes or assume a shared pollutant dose. If a future analysis collapses fuels into a clean/solid-fuel contrast, define and justify the mapping in advance, preserve solar/electric/gas/LPG distinctions for sensitivity checks, and consider the differing question routes and heating context.

## Official sources

- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc` (read-only Word rendering, printed pp. 182–183), its text search copy, and `sources_official/CHARLS_2011_Codebook_extracted.txt` (Housing, `I020`–`I022`). The text search copy corrupts the Chinese I020 parenthetical; use the original DOC rendering for its exact wording.
- `sources_official/CHARLS_2013_Questionnaire_extracted.txt` and `sources_official/CHARLS_2013_Codebook_extracted.txt` (Housing Characteristics, `I020`–`I022`).
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt` and `sources_official/CHARLS_2015_Codebook_extracted.txt` (Housing Characteristics, `I020`–`I022`, including separate other-write-in fields).
- `sources_official/CHARLS_2018_Questionnaire_extracted.txt` and `sources_official/CHARLS_2018_Codebook_extracted.txt` (`I020`, `I021_W4`, `I022_W4`). The questionnaire/Codebook wording difference for heating code 8 is preserved, not resolved by assumption.
- `sources_official/CHARLS_2020_Questionnaire_English_extracted.txt` and `sources_official/CHARLS_2020_Codebook_extracted.txt` (`I019`–`I021`).

Crosswalk rows and the searchable site metadata are generated by `scripts/build_food_environment_crosswalk.py`. The public directory displays the field-specific status and source paths; it contains no responses or counts.
