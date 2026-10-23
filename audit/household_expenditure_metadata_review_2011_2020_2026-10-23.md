# Household expenditure metadata review (2011–2020)

This review covers 53 currently pending E catalog wave-fields in the household economic resources domain. It uses the official household questionnaires and wave Codebooks stored in `sources_official/`; no respondent-level records were opened. The updater is `scripts/apply_household_expenditure_metadata_review.py` and is part of the repeatable full/finalize metadata build.

## Measurement meaning

The included `GE009_*` fields are household spending in the previous month, recorded in Yuan. `GE010_*` and 2020 `GF013_*` are household spending in the previous year, recorded in Yuan. The 2018 `GE008` and 2020 `GF010` fields in this batch are household alcohol/tobacco spending during the previous week, in Yuan. The four `GE006_W2`/`GF007` fields in this batch are household self-production indicators; the official Codebooks explicitly label `1=Yes` and `2=No`. Amount fields remain continuous and have no discrete response labels.

Question wording and listed expenditure components change across waves. The panel therefore preserves source-wave wording and period. Do not combine monthly, weekly, and annual amounts, derive a household total, divide by household size, inflation-adjust, or treat household amounts as a respondent's personal spending without a separately prespecified and validated method. A household financial respondent or primary food purchaser may answer relevant sections; the response source does not change the household measurement level.

## Missing values and interpretation limits

The 2011 baseline household questionnaire instructs interviewers to enter 0 when there is no corresponding expenditure and -9999 when the respondent cannot recall the amount. Later questionnaire wording uses 0 for no corresponding spending and missing when recall is unavailable. The public catalog displays the item-level questionnaire instruction where applicable, but it does not assert the release-specific stored representation. Authorized-release QA must establish how these instructions appear in the actual files and how the release represents other special values. Codebook means, extrema, counts, soft checks, and frequencies are not copied into the catalog or used as analytic cutoffs.

This review is metadata completion, not an analysis-ready determination. Household expenditure values may be duplicated across linked respondent records, and nonresponse, routing, household linkage, source respondent, and wave comparability still require authorized-data validation before any model is run.

## Source inventory

| Wave | Official source | Fields reviewed |
|---|---|---:|
| 2011 | Baseline Household Questionnaire and 2011 Codebook | 14 |
| 2013 | Wave 2 Questionnaire and Codebook | 4 |
| 2015 | Wave 3 Questionnaire and Codebook | 4 |
| 2018 | Wave 4 Questionnaire and Codebook | 17 |
| 2020 | Wave 5 English Questionnaire and Codebook | 14 |
| **Total** |  | **53** |

The four self-production fields are 2013/2015/2018 `ge006_w2` and 2020 `gf007` (the 2011 form has no corresponding reviewed field in this queue). The continuous household amount measures are classified by their official reporting period and Yuan unit. The dynamic item lists remain wave-specific.

