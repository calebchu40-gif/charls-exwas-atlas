# 2014 Life History famine-sequence field review (2026-10-26)

## Scope and evidence

This review extends the metadata-only 2014 Life History catalogue using the official CHARLS Life History Questionnaire and Codebook already stored under `sources_official/`. It covers the questionnaire's C4–C8 sequence about starvation during 1958–1962. It does not read participant records or use Codebook response frequencies. The public catalog exposes codebook field labels and question-derived descriptions only.

## Reconciled fields

| Questionnaire item | CHARLS field(s) | Provisional atlas role | Mapping decision |
|---|---|---|---|
| C4 | `c4` | E | Retained as family-reported starvation exposure; distinct from childhood food insufficiency before age 17. |
| C5 | `c5` | E | Added as family displacement from a famine-stricken area. It is not a geocoded location or personal dose. |
| C6 | `c6` | E | Added as a respondent-reported local-government permission context; not an independently verified policy or location linkage. |
| C7 | `c7`, `c7_1` | P | Added as family-level mortality history and its conditional count. The count is not a population mortality rate and has no defined family denominator. |
| C8 | `c8s1`–`c8s6` | P | Added as family-reported reproductive consequences, not automatically the respondent's own clinical or reproductive outcome. |

C5–C8 refer to “during those days” after the C4 question in the questionnaire. This supports sequence context, but the available questionnaire text does not provide a separate explicit skip instruction for every item; conditional routing remains a release-file QA item. A skipped or absent field must not be recoded as No.

## Source conflict and unresolved encodings

The Chinese questionnaire labels C8 option 5 as “弃养婴儿” (abandoning an infant), while the English questionnaire repeats “Artificial abortion” from option 4. The Codebook label for `c8s5` is generic (“ResultsBecauseofFoodShortage”) and does not resolve the translation. The website therefore preserves the discrepancy and does not silently harmonize it. Option-specific fields and the “none” option (`c8s6`) require authorized-release review for checkbox storage and mutual exclusivity; blank fields are not interpreted as No.

The role labels are discovery candidates only. C6 is an indirect policy-context report; C7 and C8 are family-level endpoints, not person-level phenotypes. None of these candidates is analysis-ready or automatically eligible for association modeling. The 2014 survey remains separate from the five regular waves because it has no released weight and a distinct sample composition.

## Reproducibility and output

`scripts/build_life_history_exposure_crosswalk.py` now maps four additional concept groups and ten source fields from the official Codebook: 2014 Life History totals become 22 concepts and 481 field mappings (468 E-role rows, 13 P-role rows). These are mapping-row counts, not independent exposures, outcomes, respondents, or tests. The builder regenerates `audit/life_history_exposure_crosswalk_v1.csv` and `site-prototype/dist/life_history_exposures_v1.json` without copying Codebook frequencies.

