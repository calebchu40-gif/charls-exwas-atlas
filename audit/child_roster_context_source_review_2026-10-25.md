# Child roster context source review (2013 and 2015)

## Scope

This review identifies candidate metadata fields about CHARLS respondents' children. It does not create respondent-level exposure values, combine children, or estimate associations. No participant microdata or Codebook frequencies were used in the atlas labels.

## Source structure and linkage boundary

The official raw variable inventory lists `ID`, `childID`, and `HHmemberID` in both the 2013 and 2015 `Child` modules. This supports treating these audited fields as child records linked to a respondent. The questionnaires phrase items in terms of `Childn`, while Codebooks also list numbered child suffixes (for example, `cb053_1_` and `cb053_2_`) for family-information representations. Those numbered slots must not be confused with the separate `Child` module's record key. Before analysis, inspect the authorized release to confirm its physical layout, childID uniqueness, respondent join, missing-link semantics, and eligible denominator.

Multiple child records can link to one respondent, so child records are clustered rather than independent respondent observations. A child-level analysis must retain the respondent-child linkage and account for within-respondent dependence under a prespecified estimand and survey-design plan. A respondent-level exposure derived from child data requires an explicit child selection or aggregation rule and approved release-data QA.

## Official questionnaire checks

- **2013:** `CB053` records the child's usual residence. `CB053_2` is a kilometre distance for residence option 5; `CB054` is routed for options 5–7; `CB055` asks the child's current hukou. `CB060` asks highest completed education and the questionnaire routes children younger than 12 past the item. `CB063` asks marital status and routes children younger than 16 to the next child. `CB069` asks the child and spouse's prior-year total-income category. `CB070` asks current work using a definition that includes agricultural, wage, self-employed and unpaid family-business work; `CB071` is a nominal main-occupation menu.
- **2015:** `CB053`/`CB053_2` retain the residence categories and conditional kilometre distance. `CB054` has a seven-category location menu and is asked only after `CB053=5/6/7`; `CB055` records child hukou. `CB052_W3` is completed education. Children younger than 16 route from `CB063` to `CB063_W3_1` health; children older than 60 are asked `CB063_W3_6` self-care. `CB064_W3_2` is New Rural Social Pension Insurance participation on the age/route specified in the questionnaire. `CB069` uses a 12-band income menu, distinct from 2013. `CB071_W3` asks whether the child owns a house. The current activity item maps to the numbered `xchildsta` Codebook family; it is kept separate from 2013's yes/no work item.

## Coding and harmonization decisions

- Retain 2013 and 2015 fields separately where menus or meanings differ. In particular, do not harmonize 2013 `CB070` binary work participation with 2015 activity status, or 2013 `CB071` occupation with 2015 `CB071_W3` house ownership.
- Income is an ordinal band, not a continuous amount. The wave-specific bands are not pooled or converted to midpoints.
- Residence categories are not geocoded locations. `CB053_2` is conditional distance; the Codebooks show extreme values, whose validity is not established by summary statistics. Keep the field gated for authorized-release special-value review.
- The 2015 Codebook's numbered `xchildsta` entries include an extra unlabeled value `24`. The atlas lists only questionnaire response options 1–4, leaves 24 uninterpreted, and requires release-specific identity/special-code QA.
- Child health and self-care are characteristics of a child slot, not outcomes measured on the CHARLS respondent.
- Household linkage IDs, child names, addresses, and slot-level participant values are not published.

## Machine-readable implementation

`child_roster_context_crosswalk_v1.csv` contains 19 `E` candidate wave-field mappings covering 12 family/intergenerational context concepts. `child_hukou_lifecourse_crosswalk_v1.csv` adds 13 candidate fields across 10 concepts; direct Child-field linkage and coding against numbered Family Information questionnaire/Codebook slots remain pending. `child_education_context_crosswalk_v1.csv` adds three 2013 schooling candidates. Two education fields with questionnaire/Codebook source conflicts are documented C-only in `child_education_source_conflict_crosswalk_v1.csv`; neither has response labels or E/P role. See `child_hukou_location_history_source_review_2026-10-25.md` and `child_education_source_review_2026-10-25.md`. `child_phenotype_crosswalk_v1.csv` contains two 2015 `P` candidates: proxy-reported health for children younger than 16 and self-care ability for children older than 60. All child fields retain respondent linkage, age-routed denominators where applicable, and within-respondent clustering caveats. They are not approved tests or respondent-level measures.

Sources: `sources_official/CHARLS_2013_Questionnaire_extracted.txt`, `sources_official/CHARLS_2013_Codebook_extracted.txt`, `sources_official/CHARLS_2015_Questionnaire_extracted.txt`, and `sources_official/CHARLS_2015_Codebook_extracted.txt`. Codebook cell frequencies and distribution summaries were excluded from public outputs.

The repository keeps only a minimized `child_module_field_presence_v1.csv` derived from the local official variable inventory: wave, field code, module, and a field-presence-only status. It is sufficient for repository tests to recheck Child-module membership without committing the full 4 MB local inventory or any participant-level information. Rebuild it with `python scripts/build_child_module_field_presence_manifest.py` when the official inventory or crosswalk changes.
