# 2014 Life History historical family-class field review (2026-10-26)

## Scope and exact source identity

Reviewed the official questionnaire's C5-C5f items and corresponding 2014 Codebook entries in the `WEALTHHISTORY` module. The matching requires both module and field code: `FAMILYINFORMATION:c5` is the separate famine-flight item and must not be confused with `WEALTHHISTORY:c5s1`–`c5fs27`. The generated coverage ledger enumerates all 189 option fields (27 options in each of seven respondent/relative forms), all mapped to one concept group. Codebook frequency tables are not used.

## Questionnaire and route interpretation

The questionnaire says respondent C5 is asked only of respondents aged 80 and over (printed as born before December 1934). The item asks about family class background during the 1950s–1970s. C5a asks the biological father's family background; if C5a=27 (“None”), C5b asks the paternal grandfather's background. C5c asks the biological mother's family background; if C5c=27, C5d asks the maternal grandfather's background. C5e/C5f are asked for foster father/mother when the respondent was raised by foster parents. These routes are preserved without assuming that the fields were administered or observed for every participant.

Each of the seven relative forms has 27 option-specific fields. They are slots of multi-select questions, not 189 independent exposure measures. Option 26 is a write-in request and its response text is not ingested; option 27 is “None.” The atlas does not infer No from blank fields, combine relative forms, or collapse class labels into a numeric socioeconomic score.

## Atlas treatment

Mapped all 189 structured Codebook fields to the candidate concept `life_history_historical_family_class_background` (E role), with field-level Codebook labels and a common age/route caveat. This is a historical family socioeconomic/political context candidate for a narrow older-respondent subgroup; it is not current wealth, income, a chemical exposure, or a measure available to all Life History participants. The field rows do not increase the count of distinct concepts by 189.

## Reproducibility and status

`scripts/build_life_history_exposure_crosswalk.py` generates `audit/life_history_historical_family_class_coverage_2014_v1.csv` and the Life History JSON. The full 2014 directory now has 36 candidate concepts and 993 source-field mappings (965 E-role, 28 P-role). Formal association eligibility is still unestablished; the 2014 survey remains separate from the five regular waves because no survey weight was released.

