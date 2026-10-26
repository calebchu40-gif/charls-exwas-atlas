# 2014 Life History parent and caregiver module review (2026-10-26)

## Sources and coverage

Reviewed the official 2014 Life History Questionnaire's parent/caregiver items and the FAMILYINFORMATION Codebook. The reproducible coverage ledger `life_history_parent_module_coverage_2014_v1.csv` enumerates all 47 structured Codebook fields in the A-section parent/family-background code families. All 47 fields now map to E candidates. A5c-A5f are mapped as separate adoptive/step-parent birth-year context, not as respondent-age-at-birth or caregiving-start measures. No response frequencies or participant records are used.

## Added candidate concepts

| Concept | Fields | Boundary |
|---|---|---|
| Biological-parent death and loss context | `a1a`, `a1b`, `a2a_1`, `a2a_2`, `a2b_1`, `a2b_2` (6) | Parent-specific alive status and conditional death year/age. This is family adversity, not respondent mortality; timing relative to respondent age needs approved linkage. |
| Parental remarriage and stepfamily transitions | `a11a*`, `a11b*`, `a12a*`, `a12b*` (24) | A11 items follow divorce; A12 items follow bereavement. Preserve maternal/paternal branches, exact age versus fallback band, and step-parent status/death routes. |
| Adoptive and step-parent education | `a6c`, `a6d`, `a6e`, `a6f` (4) | Keep adoptive/step-parent education distinct from biological-parent education and the respondent's own education. A4a/A4b caregiver routes must not be assumed from relationship category alone. |
| Main female/male caregiver relationship before age 17 | `a4a`, `a4b` (2) | Separate relationship-category reports for the main female and male caregiver; preserve the item-specific options and skips. A4a/A4b do not expose the open-text caregiver referent or identify caregiver behavior. |
| Biological parents' birth years for potential age-at-birth derivation | `a5a`, `a5b` (2) | Calendar-year inputs only; the fields are not themselves parental age. Derivation requires validated respondent birth year, authorized linkage, and release-specific missing-code review. |
| Adoptive/step-parent birth-year background | `a5c`–`a5f` (4) | Distinct relationship-specific birth-year context, routed by A4a/A4b caregiver response; does not define caregiving start/duration or age when the respondent was born. |

## Deferred fields and interpretation limits

`a4a`/`a4b` are represented as one early-life caregiving/family-structure candidate because they explicitly ask who spent the most time raising the respondent before age 17. They remain separate source fields and route parents' education and birth-year questions. Open-text descriptions are absent from the structured Codebook and are not added or published. `a5a`/`a5b` map as biological parent birth-year inputs for a potential parental-age-at-birth estimand, not as direct age measurements. `a5c`-`a5f` map as adoptive/step-parent birth-year background, conditioned on the A4a/A4b response. None of the birth-year fields directly measures respondent age at a parent event or caregiving duration; deriving any such measure requires a separate estimand, authorized linkage and release validation.

The official questionnaire distinguishes remarriage after divorce (A11) from remarriage after a parent's death (A12), treats long-term cohabitation as marriage in A12, and routes exact ages, fallback age bands, step-parent survival, and step-parent death timing conditionally. These routes are preserved; skipped data are not coded as No. The builder excludes questionnaire-only names and open-text death causes.

## Reproducibility and current directory

The source-specific builder writes the crosswalk, website JSON, parent coverage ledger, and sibling coverage ledger from official Codebook field identities and reviewed mapping definitions. The full 2014 Life History catalog now contains 181 concepts and 5,879 source-field rows (5,818 E-role, 61 P-role). These are metadata mapping rows, not independent measures or analysis-ready associations. The special survey remains separate from regular-wave weighted analysis because the official release provides no survey weight.

