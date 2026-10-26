# 2011 Community Questionnaire Part A: exposome-context source review (2026-10-26)

## Scope and source basis

Reconciled all 80 `JA`-prefixed 2011 community-module fields in the sanitized field inventory against the official 2011 Community Questionnaire and Codebook. The questionnaire distinguishes village-only (`V`) and community-only (`C`) respondents; this matters because JA007–JA008 are C-only while JA009–JA010 and most land-policy items are V-only. The crosswalk stores source fields and conceptual candidates; it does not establish individual exposure, cross-wave equivalence, or analysis eligibility. Descriptive Codebook counts/frequencies were not copied.

## Candidate mappings (69 fields)

| Candidate concept | Official fields | Handling |
|---|---|---|
| Community/village office establishment year | `JA002` | Keep as community administrative-history context. `JA001` office type is survey-unit/design metadata. |
| Community boundary-change history | `JA004`, `JA005`, `JA006_1`, `JA006_2` | The latest year and pre-change area are conditional on `JA004=Yes`. Keep square-kilometre and mu values distinct; do not sum. `JA006` is the unit selector. Boundary change can break cross-wave geographic comparability. |
| Community urban-administrative transition history | `JA007`, `JA008`, `JA009`, `JA010` | Preserve the C-only office-conversion question versus V-only city-planning designation. Years are conditional on Yes. Neither establishes a sampled person's urban residence or hukou. |
| Land/property-rights certification | `JA015`–`JA026` | Keep the land-rights delimitation, farmland contract, housing-land use, house ownership, forest-rights and collective-asset share certificates distinct. Each year follows its own Yes route. `JA023` has an explicit no-forest category. |
| Land development and consolidation history | `JA027`, `JA028`, `JA030`, `JA031` | Distinguish agricultural land development from construction-land consolidation since 2005. Their area outcomes `JA029` and `JA032` remain in the land-use profile. Year fields follow Yes routes. |
| Land expropriation history | `JA035`–`JA037` | Community/village report since 2000; latest year and compensation per mu are conditional on Yes. No sampled-household or participant linkage is inferred. |
| Homestead allocation policy | `JA051S1`–`JA051S6`, `JA052`, `JA053`, `JA054` | Preserve six multiple-response conditions, source categories, and rule-change timing since 2000. The open-text `JA052_1` is excluded. Do not infer any sampled household's eligibility or receipt. |
| Surname concentration context | `JA043`, `JA044`, `JA046_1`–`JA046_3` | Keep presence, number of groups, and household counts separate; no proportions without a validated denominator. `JA045_1`–`JA045_3` surname strings are excluded. Suppress small cells if ever summarized. |

Existing JA candidates retained: `JA003_1`, `JA003_2`, `JA011`, `JA013`, `JA014`, `JA029`, `JA032`, `JA033`, `JA034`, `JA050` (land area/use); `JA038` (nominal terrain); `JA039_1`, `JA039_2`, `JA040`, `JA041` (community-reported 2010 weather); and the four named leadership positions' education/age/tenure fields in `JA042`. The unidentified fifth age/tenure slots remain C-only.

## Explicit non-candidate/source-metadata disposition (11 fields)

`JA001`, `JA003`, and `JA006` are office/unit selectors; `JA012` is unresolved; `JA042_2_5_` and `JA042_3_5_` have Codebook slots without a named questionnaire-table position; `JA045_1`–`JA045_3` and `JA052_1` are open text; `JA048` identifies the community-section informant. They are retained only as C metadata or excluded from the public E/P catalogue, not silently dropped.

**JA012 conflict:** the official questionnaire asks for paddy-field area, while the 2011 Codebook labels it “Among Arable Land, How Many is Irrigatable.” These are not interchangeable. JA012 is held C-only until the authorized source/release clarifies it; no meaning or numeric unit is guessed.

Questionnaire items JA047 and JA049 ask for the respondent's name and phone number but are absent from the analyzed field inventory; no direct identifier or response value is imported. The raw local QA inventory remains untracked. The public sanitized inventory contains only variable code and official label metadata.

## Reproducibility

`scripts/build_community_exposure_crosswalk.py` validates the mapped JA codes against both official source extracts and emits the public community crosswalk; `scripts/build_community_value_labels.py` emits labels without Codebook frequencies. Regression coverage verifies complete 80-field disposition, the 69/11 split, route/level caveats, and the JA012 conflict. No participant records, Codebook frequencies, or association results were used.
