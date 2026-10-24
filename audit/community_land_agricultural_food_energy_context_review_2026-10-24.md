# 2011 community land, agricultural, food-price and energy-price context review (2026-10-24)

## Scope

This review adds 72 source-field mappings across nine concepts to the 2011 Community-module candidate inventory. It uses the official community questionnaire and Codebook plus the project's raw field-name catalogue. All values are community-informant context, not participant-level measurements. The fields remain candidates pending authorized-release linkage, eligibility, special-value and analysis-design checks. No respondent records, Codebook frequencies or descriptive extrema are used.

## Added concepts and source fields

| Concept | 2011 source fields | What the source supports | Interpretation boundary |
|---|---|---|---|
| Community land area and agricultural land-use profile | `JA003_1`, `JA003_2`, `JA011`, `JA013`, `JA014`, `JA029`, `JA032`, `JA033`, `JA034`, `JA050` | Area/unit alternatives; 2010 and 2007 arable area; 2010 construction land; conditional land-development/consolidation amounts; leased-land share and annual price; 2010 house-site area per person | Community/village aggregate, not a sampled person's parcel or housing exposure. Preserve the separate years and units. Do not derive density or proportions without compatible validated denominators. `JA003_1` and `_2` must not be summed. |
| Community main terrain/topography | `JA038` | Five nominal choices: plain, hill, mountainous region, plateau and basin | Coarse community description, not measured elevation, slope or an ordinal severity scale. |
| Community agricultural mechanization context | `JJ002`–`JJ004` | Reported mechanization percentage, whether large machinery is rented, and conditional daily rental price | Community production context, not the participant's occupation, machinery contact or pollution dose. `JJ004` is asked only after `JJ003=Yes`; a structural skip is not zero. |
| Community fertilizer and seed input context | `JJ006`–`JJ010` | Open-text name of one commonly used fertilizer and reported fertilizer/seed/seedling prices | The text is not a standardized chemical identity, and prices do not establish a participant's purchase, handling or absorbed dose. Preserve source-specific price units. |
| Community food commodity prices | `JJ017`–`JJ020` | Current reported local prices for pork tenderloin, eggs, rice and wheat/flour, each per jin | Food-market context, not individual purchasing, dietary intake or nutrient exposure. Do not merge the four commodities into a score. |
| Community household energy prices | `JJ021`, `JJ022`, `JJ025` | Current reported natural-gas price per m³, LPG per bottle and coal per jin | Local price context, not evidence of household connection/use, fuel mix or combustion exposure. LPG bottle size is not specified. |
| Community major-crop production | `JJ001_1a`–`JJ001_3f` | Up to three ranked crops; each has open-text crop name, 2010 planted area (mu), yield (jin/mu), machinery use (Yes/No), current harvest seasons and historical maximum seasons | Keep crop rank and unlike units separate. Do not sum yields or derive production without release-level validation; these are community agricultural context, not an individual's occupation, diet or pesticide exposure. |
| Community household communication/appliance penetration | `JB023`–`JB026` | Village estimates of household prevalence of fixed telephones, at least one cell phone, television and refrigerator, in percent | These are aggregate 0–100% context measures, not individual or sampled-household device ownership/use; retain the four amenities separately. |
| Historical severe disaster/epidemic severity | `JI003_1a`–`JI003_3h` | Since 1945, the three community-informant-ranked most severe listed disasters or epidemics; each event has type, start/end year and month, deaths/injuries, affected-population share and grain-output decline | Long retrospective recall and village reporting; keep event ranks and unlike components separate. Not a sampled person's confirmed direct exposure or a measured disease/environment dose. |

Questionnaire locations are Part A, printed pp. 2–7 (land and terrain), Part B, printed p. 11 (household amenity percentages), Part I, printed pp. 34–35 (historical disaster/epidemic severity), and Part J, printed p. 35 (ranked crop table) and pp. 35–39 (agricultural inputs and prices). The generator verifies the mapped field identifiers against both official source extracts, checks the question wording and route anchors, and separately checks the terrain response list. The value-label builder exposes only Codebook categories; it omits Codebook frequencies and numeric summaries.

## Unresolved source conflict: JA012

`JA012` is intentionally not included in the new land-use mapping. The official questionnaire prompt asks how much of the arable area is paddy field; the 2011 Codebook heading describes the item as “Among Arable Land, How Many is Irrigatable.” Those constructs overlap but are not interchangeable. Do not label or analyze it as either paddy-field area or irrigated area until the authorized release documentation resolves the field identity. This exclusion is not evidence that the raw field is absent.

## Reproducibility

Run `python scripts/build_community_exposure_crosswalk.py` followed by `python scripts/build_community_value_labels.py`. The full/finalize-only metadata pipelines already invoke both builders before rebuilding the concept-source crosswalk and public catalogue. Regression checks are in `tests/test_community_land_agricultural_food_energy_review.py`.
