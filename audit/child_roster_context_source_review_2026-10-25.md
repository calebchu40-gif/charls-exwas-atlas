# Child roster context source review (2013 and 2015)

## Scope

This review identifies candidate metadata fields about CHARLS respondents' children. It does not create respondent-level exposure values, combine children, or estimate associations. No participant microdata or Codebook frequencies were used in the atlas labels.

## Source structure and linkage boundary

The 2013 and 2015 questionnaires phrase items in terms of `Childn`; the Codebooks list numbered child-slot variables (for example, `cb053_1_` and `cb053_2_` in 2013 and `cb053_1_`, `cb053_2_`, etc. in 2015). The public audit therefore describes these as respondent-linked child-roster-slot fields. It does not assume an independent child ID or a long child table. The authorized release must be inspected to confirm the physical file layout, respondent key, slot order/linkage, missing-slot semantics, and eligible denominator before any analysis.

Multiple slots can belong to one respondent. Slot records are not independent respondents. Any respondent-level use requires an explicitly defined child selection or aggregation estimand, appropriate design/variance handling, and approved release-data QA.

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

`child_roster_context_crosswalk_v1.csv` contains 21 wave-field mappings covering 14 concepts. All rows are `E` candidates in the broad family/intergenerational context discovery catalogue, with explicit roster-slot, route, and aggregation caveats. They are not approved tests, harmonized respondent-level exposures, or evidence of causal adjustment eligibility.

Sources: `sources_official/CHARLS_2013_Questionnaire_extracted.txt`, `sources_official/CHARLS_2013_Codebook_extracted.txt`, `sources_official/CHARLS_2015_Questionnaire_extracted.txt`, and `sources_official/CHARLS_2015_Codebook_extracted.txt`. Codebook cell frequencies and distribution summaries were excluded from public outputs.
