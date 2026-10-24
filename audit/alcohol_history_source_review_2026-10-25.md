# Alcohol-history and morning-drink source review

Date: 2026-10-25. Scope: official 2011, 2013, 2015, and 2018 questionnaires and Codebooks. No respondent records or Codebook frequencies were used.

## Past alcohol history (`DA069`)

The four wave questionnaires and matching Codebooks use the same three response categories: never drank; used to drink less than once a month; and used to drink more than once a month. The item is retrospective history/frequency, not current past-year drinking, alcohol quantity, or an exact monthly frequency. It remains separate from the wave-specific past-year beverage-frequency questions.

The skip route matters for the denominator. In each wave, `DA069=1` or `2` routes past the later drinking-history questions; only `DA069=3` continues to the quit/start and drinking-detail sequence. For re-interviews, questionnaires say to skip `DA069` if it was already asked in an earlier interview; the 2018 procedure specifically uses `ZDA069` to determine whether to ask the item and which later route to follow. Thus an absent or skipped `DA069` is not a No response. The concept remains a source-mapped candidate; authorized-release field identity, prior-wave carry-forward, and missing-value handling still require file-level QA before modeling.

## Morning drink to steady nerves or relieve a hangover (`DA078`, 2011 and 2013)

The 2011 and 2013 questionnaires and Codebooks identify `DA078` as a Yes/No item asking whether the respondent took a first drink in the morning during the past year to steady nerves or relieve a hangover. The surrounding questionnaire route means it is not a population-wide item: respondents reporting never drinking or less-than-monthly past drinking at `DA069` skip past the later sequence that contains `DA078`. The site retains the eligible-route caveat; structural skips are not No. This is a dependence-related behavior marker, not alcohol quantity and not a clinical diagnosis. It is not extended to unlisted waves by name similarity.

## Reproducible propagation

`scripts/apply_alcohol_history_source_review.py` validates the official source text, adds wave-specific source locators and route semantics to the behavior crosswalk, and updates the behavior-topic JSON without importing any Codebook summary counts. It runs after behavior labels are enriched in the full pipeline and before the E/P catalog is constructed in finalize-only mode. Tests check the mapping, public catalog, topic browser and candidate-pair caveats.

Sources: `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt:L2607-L2610` and `:L2666`; `sources_official/CHARLS_2013_Questionnaire_extracted.txt:L3245-L3254` and `:L3314`; `sources_official/CHARLS_2015_Questionnaire_extracted.txt:L2649-L2657`; `sources_official/CHARLS_2018_Questionnaire_extracted.txt:L3116-L3129`; wave-specific Codebook entries for `da069` (and `da078` in 2011/2013). The Codebooks are used for response labels only; their frequency summaries are excluded.
