# CHARLS 2020 COVID prevention/context candidate review

**Status:** metadata-only candidate mapping; not an association analysis or approved variable set. **Scope:** the 2020 COVID questionnaire module only. The official questionnaire defines prevention questions, infection/quarantine questions, outbreak-period activities, and residence-area restrictions in separate sections; this review preserves those distinctions.

## Source basis and handling

- Primary field dictionary: `audit/raw_variable_catalog_v1.csv`, restricted to the 2020 `COVID_Module` rows.
- Official sources: `sources_official/CHARLS_2020_Questionnaire_English_extracted.txt` (COVID module, questionnaire pages 96–104) and `sources_official/CHARLS_2020_Codebook_extracted.txt` (COVID module). The builder verifies each mapped source code against the dictionary, exact questionnaire question anchor, and Codebook text before writing the crosswalks.
- The Codebook contains descriptive frequency tables; this project does **not** copy any counts, percentages, means, extrema, or response distributions into the crosswalk or public site.
- Crosswalk builder: `scripts/build_covid_prevention_context_crosswalk.py`. Outputs: `audit/pandemic_context_exposure_crosswalk_2020_v1.csv` and `audit/pandemic_context_phenotype_crosswalk_2020_v1.csv`.

## Candidate mapping

The E table contains 48 wave-field rows / 22 concepts. It covers awareness of prevention measures (7 selection fields), information sources (10), mask use and mask-use transition, early stockpiling, perceived government response strictness, reported cases among household/non-household contacts, quarantine reasons and location, duration/cost/social setting, fear-related self-isolation, outbreak-period residence, and four separately defined residence-area restriction types with their duration components.

The P table contains 21 wave-field rows / 21 concepts. It covers the respondent's reported suspected/confirmed case status, COVID-treatment hospital days, the positive-test quarantine reason, 14 self-reported behavior/function changes during the specified outbreak period, two pandemic-specific emotional-response items, and two public recreation cancellation-duration items.

These labels are a screening taxonomy. They do not imply that every E/P combination is scientifically appropriate or that an item is a validated scale. All are 2020-only fields; the outbreak-period comparison questions explicitly ask respondents to compare with a hypothetical no-pandemic situation. They must not be interpreted as measured absolute behavior or a causal effect.

## Field-level boundaries

- Checklist awareness, information-source, and stockpiling options stay item-specific. Blank/unselected values are not automatically coded as “No”; exclusive none, “don't know,” and refusal options remain outside the E/P matrix where field identity or storage is ambiguous.
- The mask items distinguish pandemic-period use, current use, no outing, and duration since stopping. The status fields are not collapsed into a single binary measure.
- The respondent's suspected/confirmed status is not called laboratory-confirmed infection. Household, relative, and acquaintance case reports remain separate contextual E candidates. COVID test status/date was not promoted as infection status.
- Perceived government response strictness is a single subjective policy-context item. The questionnaire says “appropriate” while the Codebook uses “Satisfied” for response 2; that wording discrepancy remains explicit and is not silently harmonized. Quarantine-location indicators are conditional on a quarantine experience and are not objective facility-quality or dose measures.
- Quarantine, self-isolation, and community restriction measures remain separate. The questionnaire says restriction levels should not overlap; their durations must not be summed until the release data and routing are checked.
- Fear/anxiety items remain single-item pandemic-specific responses, not a validated general mental-health scale. Behavior-change items are retrospective comparisons, not physical activity, sleep, smoking, alcohol, or dietary absolute amounts.
- Codebook/Questionnaire disagreements, exclusive options, structured skips, “-1” entry conventions, and analysis denominators require authorized-release validation. No weights, eligible-sample counts, covariate model, or association results are inferred here.

## Reproducible integration

The builder is registered in both metadata pipelines. `build_charls_atlas_catalog.py` brings the two reviewed crosswalks into the E/P field catalogue, and `build_ep_concept_source_crosswalk.py` exposes exact wave-field-to-concept provenance. These additions do not change the formal `DO NOT ANALYZE` lock inventory or enable an analysis model.

## Value-label handling and build record (2026-10-25)

- For checkbox fields, only explicit numeric category/value lines printed under that exact Codebook field are copied (for example, `0=No; 2=Yes`). Frequency and percentage columns are discarded. The parser stops at the next field heading so a following field's table cannot be assigned to the current variable.
- For ordinal fields, numeric category wording is taken from the questionnaire and checked against the Codebook's category wording. Continuous amounts/durations have no invented response labels. If a Codebook section prints only one category, only that category is shown; no absent category is inferred.
- All 69 source rows now carry a specific label or no-label review status. Candidate statuses still require authorized-release coding, route, storage, and denominator QA; a reviewed label does not establish analysis eligibility.
- The complete metadata finalization pipeline completed on 2026-10-25 in 9.6 minutes after the completeness review added two additional questionnaire-grounded candidate concepts (VA007 and VB009). Final coverage: 7,076 E/P catalogue records; 6,863 distinct wave-fields; 3,723 records with explicit labels; 0 generic pending E/P statuses and 0 generic pending C statuses. The 92 formal analysis locks were reconciled unchanged. Models and participant-level results remain 0.
