# Blood-pressure and pulse measurement source review: 2011–2015

Reviewed 2026-10-24 against the official 2011 physical-examination questionnaire and the 2013/2015 Biomarker Questionnaires and wave Codebooks. This is field/protocol metadata only. No respondent measurements, Codebook frequencies, means, ranges, or observation counts were used.

## What the instruments establish

All three instruments describe three blood-pressure sessions using an Omron HEM-7200 monitor. The respondent is asked to remain seated, relaxed, and quiet. The instructions position the cuff/arm and the upper arm at heart level; separate fields record which arm was used, test position, compliance, and whether the respondent smoked, exercised, consumed alcohol, or ate in the 30 minutes before measurement. These context fields matter when interpreting measurements and should not be collapsed into the blood-pressure values.

The wave questionnaires explicitly label systolic and diastolic readings in mmHg. They collect three readings per component. Pulse is collected alongside each reading, but the questionnaire labels its unit only “P”; no explicit pulse unit was located. The public catalogue therefore leaves the pulse unit blank rather than assuming beats per minute.

For systolic reading, the interviewer instructions define 993 as attempted but unable to complete and 999 as chose not to complete. These are status codes, not pressures. Preserve them and the test eligibility/routing information; do not treat them as numeric values or encode routed absence as zero. Do not calculate a mean, select a reading, or pool waves before release-specific valid-value checks and a prespecified analysis rule.

## Field identity by wave

- **2011:** The physical-examination manual uses LI identifiers, while the release Codebook lists candidate `qa003`–`qa013` fields. The manuals establish the measurement protocol and the Codebook establishes labels for similarly named candidate fields, but the retained sources do not establish a one-to-one LI-to-QA release crosswalk. The catalogue keeps this as a candidate mapping and does not claim exact identity.
- **2013 and 2015:** The Biomarker Questionnaires use the same QA field identifiers that appear in each wave's Codebook. The source meaning is directly documented, but field presence in an authorized data extract, valid-value rules, eligibility, and analytic suitability still require release-level QA.

Protocol consistency does not by itself prove that the analytic samples or all measurement conditions are comparable across waves. These are physiological/clinical phenotype candidates, not exogenous environmental exposures. They remain outside any approved model until a target estimand and survey design are defined.

## Reproducibility

The exact concept-wave notes are in `objective_measurement_crosswalk_v1.csv`; `scripts/apply_bp_pulse_source_review.py` validates source anchors and propagates the reviewed status to the wave-field catalogue. Both full and finalization metadata pipelines run the updater. The update covers 9 concept-wave entries and 27 P-role wave-field records. It does not change the 89-row formal-analysis lock registry.

Official sources: `sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official_extracted.txt`, `sources_official/CHARLS_2011_Codebook_extracted.txt`, `sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt`, `sources_official/CHARLS_2013_Codebook_extracted.txt`, `sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt`, and `sources_official/CHARLS_2015_Codebook_extracted.txt`.
