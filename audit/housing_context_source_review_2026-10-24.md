# Housing and indoor-context source review (2026-10-24)

This audit records questionnaire wording, response structure and target level for selected CHARLS housing-context candidates. It uses official extracted wave questionnaires and Codebooks only. No respondent records or Codebook frequencies/percentages are copied into the public catalogue.

## Heating and gas availability

The 2011–2020 housing catalogue source-reviews residential heating availability and coal/natural-gas supply wave by wave. Heating-source response routes differ by wave. The 2018 questionnaire and Codebook differ in their heating-source label for code 8. In 2020, the questionnaire asks whether XFinancialResp's house has heating, while the Codebook label for I019 is “Centralized Heating”; both source representations are retained. These are household/residence context measures, not fuel use or pollutant dose.

## Water and air-cleaner items

The 2011, 2013, 2015 and 2018 questionnaires ask whether the respondent's residence has running water (`I017`, 1=Yes, 2=No). The 2013/2015 wording was checked in the original PDF pages and retained as a small supplemental extraction because the earlier text extraction omitted that section. Keep it as household access, not water source or quality; do not treat the 2020 tap-water item as automatically equivalent.

The 2020 questionnaire/Codebook review covers tap-water access (I016), reported waterworks treatment (I029), and air-cleaner presence (I024). I016 describes household access, not drinking-water quality. I029 includes “Do not know,” which must not be recoded as “No.” The I024 household referent is XFinancialResp's house; an interviewer may record the air-cleaner item only when in the respondent's housing and clearly certain, otherwise asking the respondent. Presence does not establish use, filter condition, indoor concentration or personal exposure.

The same yes/no residence air-cleaner question I027_W3 appears in 2015 and 2018. These wave-specific source rows now map to the canonical `air_cleaner_home` concept alongside 2020 I024. Preserve the different household referents and verify household-person linkage before person-level assignment.

## Interviewer-rated indoor cleanliness and temperature

I025 and I026 are present in the 2011, 2013, 2015, 2018 and 2020 housing questionnaires. Each wave marks these items as interviewer-recorded. I025 asks about household indoor tidiness/cleanliness; codes 1–5 progress from excellent/very tidy to poor, while 2013–2020 Codebooks also list 6=Not applicable. I026 asks the interviewer to assess household temperature from very hot through hot, bearable and cold to very cold; 2013–2020 Codebooks also list 6=Not applicable. Keep both measures ordinal and household-level. They are not an indoor-air contaminant assay, standardized hygiene inspection, thermometer measurement or personal thermal dose.

For 2011, the official baseline questionnaire lists 6=Not applicable for both items, but the 2011 baseline household questionnaire and Codebook list only codes 1–5. The 2011 source-version discrepancy is preserved; the atlas does not add category 6 to the published Codebook-based field labels or infer how it is stored in a particular release. The exact instrument/release supplied with any approved analysis dataset must resolve this before recoding.

## Household floor condition

The 2020 questionnaire and Codebook identify I027 as household ground/floor condition: 1=Flat covered, 2=Flat concrete, 3=Uneven. The interviewer is instructed to record it only when inside the respondent's housing and clearly certain; otherwise ask the respondent. These are nominal dwelling-condition categories, not a validated mobility, fall-risk or accessibility measure. Do not impose an ordinal severity scale or interpret the item as an individual's outcome.

## Current-residence move-in timing

The 2020 I002/I003 pair asks when the Household Financial Respondent moved into current housing, despite the Codebook labels “Time House Built” and “Time Interval House Built.” I002 is calendar year with a questionnaire range of 1900–2020 and an interviewer instruction to enter -1 if the respondent cannot answer. I003 is a six-category fallback asked when the year is unclear (0–5 through more than 40 years). Preserve the respondent household referent and two different response formats; neither item measures building construction year. Do not combine I003 into a single year or assume -1 storage without checking the authorized release. Codebook frequencies are excluded.

## Elevator and home-accessibility items

Elevator availability is I009 in 2011, 2013, 2015 and 2018, and I007 in 2020. In 2011–2018, the questionnaire routes to I009 only when I008 > 1; a skipped item for a lower-floor dwelling is structural missingness, not a “No” response. In 2020, I007 is asked without that displayed I008 > 1 route and includes an interviewer-in-home/certainty instruction. Preserve these wave-specific routes and household referents. The item records availability, not use or an individual's mobility.

Home accessibility facilities are I010 in 2011–2015, I010_W4 in 2018, and I009 in 2020. The 2011–2015 Yes/No items route a “No” response to the entrance-step question. The 2018 and 2020 versions add a third response for a level/flat entrance where facilities are not needed; retain that as its own category, not as “No.” In 2020, the interviewer instruction also limits direct recording to cases where the interviewer is in the respondent's housing and clearly knows the answer. These are household/building context items, not measures of an individual's disability or a standardized accessibility score. Confirm household-to-person linkage and release-specific missing-value storage before analysis.

The public catalogue displays response labels and route caveats only. Questionnaire and Codebook frequencies are not copied or used to define candidate status.

## Source files

Wave-specific English questionnaire and Codebook extracts are in `sources_official/`. The 2011 discrepancy is checked against both `CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` and `CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`, plus `CHARLS_2011_Codebook_extracted.txt`. The incremental propagation script is `scripts/apply_housing_context_source_review.py`.
