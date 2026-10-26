# 2014 Life History DEMOGRAPHICBACKGROUNDS: official-field inventory checkpoint (2026-10-26)

## Scope and evidence

The inventory parser reads only field identifier and field-title lines from the official Life History Codebook's `2 DEMOGRAPHICBACKGROUNDS` section and stops at `3 FAMILYINFORMATION`. It does not copy or parse the Codebook frequency tables, extrema, or respondent values. Questionnaire section headings were inspected to establish the module's broad organization; the questions and routes still require item-by-item review before mapping.

The official Codebook contains **1,920 unique fields** in this module. The current Life History crosswalk has no `DEMOGRAPHICBACKGROUNDS` rows, so this is a true coverage gap rather than an already mapped module. The generated CSV gives every field a unique initial state: three linkage keys are excluded, and 1,917 substantive/metadata fields remain pending questionnaire-level adjudication. These 1,917 are not 1,917 independent exposures or outcomes.

## Initial disposition

| Initial disposition | Fields | Interpretation |
| --- | ---: | --- |
| `pending_questionnaire_review` | 1,917 | Field title alone is insufficient to determine respondent vs relative referent, question route, repeated episode structure, sensitivity, or E/P/C role. |
| `excluded_linkage_key` | 3 | ID, householdID, communityID; join keys excluded from the public concept catalog. |
| **Total** | **1,920** | Exact official Codebook module inventory. |

## Questionnaire organization observed

The module covers repeated spouse/partner histories and later family/child and hukou-related material. This is retrospective special-wave content, not another regular CHARLS follow-up wave. Repeated partner/child slots, household/relative referents, preload identity fields, open text, sensitive political/religious/ethnic details, and routing/response-process variables need separate decisions. A codebook label such as `TheYearofBirth` or `TheHighestLevelofEducation` is not enough to infer whose characteristic it represents.

Questionnaire section headings located by the source extract:

- `Spouse/Partner Section 配偶/伴侣部分 . . . . . . . . . . . . . . . . . . . . 7`
- `Children Section 子女部分 . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14`
- `Hukou Section 户口部分 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28`
- `Spouse/Partner Section 配偶/伴侣部分`
- `Children Section ⼦⼥部分`
- `Hukou Section ⼾⼝部分`

## Next source-review sequence

1. Review spouse/partner items against the questionnaire routes and response categories; exclude names and direct identifiers; preserve current/former spouse versus unmarried partner, marriage/cohabitation, event year, residence transition, and hukou transitions as distinct constructs.
2. Review respondent-versus-relative party/ethnicity/religion selections with special privacy and data-minimization handling; do not publish individual-level sensitive responses or frequencies.
3. Continue to children and hukou sections, distinguishing respondent characteristics, child/relative roster descriptors, family context, linkage/preload fields, and questionnaire-process fields.
4. Each batch must update the crosswalk and this inventory through a fail-closed build: every field gets one and only one mapped, deferred, C-only, sensitive exclusion, linkage-key, or source-metadata disposition. Life History remains separate from regular-wave weighted E/P analysis because its release note provides no weight.

## Reproducibility

Run `python scripts/build_life_history_demographic_background_inventory.py` to regenerate the inventory and this note from the official extracted Codebook and Questionnaire. Only identifiers and field-title metadata are emitted; Codebook summary statistics and participant data are never read into the output.
