# Individual transfer-income source coding review (2011–2020)

This review covers 50 person-level, past-year transfer-income source fields (10 response options in each of five waves). It uses the official questionnaires and Codebooks under `sources_official/`; no participant records or response frequencies were used. The repeatable updater is `scripts/apply_individual_transfer_source_review.py`, called by both full and finalization builds.

## Wave-specific coding

The questionnaires define the source question as check-all-that-apply. The option lists and income scope change by wave, so source wording and option number remain attached to each wave.

| Wave | Fields | Official evidence | Catalog treatment |
|---|---:|---|---|
| 2011 | 10 | Baseline questionnaire lists options; Codebook shows affirmative option text/codes but does not document a No category for each slot. | No response-value labels assigned. The participant-level unselected state, stored value, special codes, and denominator remain unresolved. A blank is not recoded as No. |
| 2013 | 10 | Questionnaire says check all that apply; Codebook lists option-specific affirmative entries but not a No category for each slot. | Same unresolved handling as 2011. |
| 2015 | 10 | Questionnaire says check all that apply; Codebook lists option-specific affirmative entries but not a No category for each slot. | Same unresolved handling as 2011. |
| 2018 | 10 | Wave 4 Codebook explicitly lists `0=No` and the item option number as `Yes` for every field. | Exact Codebook value labels shown; response frequencies omitted. |
| 2020 | 10 | Wave 5 Codebook explicitly lists `0=No` and the item option number as `Yes` for every field. The questionnaire says COVID-19 pandemic subsidies are included. | Exact Codebook value labels shown; response frequencies omitted. COVID-specific scope retained. |

The value code for Yes is the option number (for example, option 3 is coded `3=Yes` in the fully documented 2018/2020 fields), not a common `1=Yes` binary recode. Option 10 is “None of the above”; it is a separate, exclusive questionnaire option and should not be interpreted as a transfer source. Amount variables are separate fields and are not represented by these source indicators.

## Analysis limits

These fields identify individual transfer-income source participation, not amount, household receipt, or a causal exposure by themselves. Early-wave missing/unselected slots cannot be interpreted as No without authorized-release verification. For all waves, confirm field-level stored values, nonresponse/special codes, skip patterns, eligible denominator, and cross-wave item equivalence before a formal analysis. Codebook frequencies are deliberately excluded from the site. The catalog review does not mark the fields analysis-ready or create statistical associations.

