# Most recent job location review — 2026-10-25

Reviewed the `FL004` last-job location menu in the official 2011, 2013, 2015 and 2018 questionnaires and Codebooks. The questionnaire menus were transcribed by wave; no response frequencies are copied.

- **2011:** the questionnaire numbers options 1–4 and tells interviewers to enter 0 when no fixed address, but the Codebook does not supply an FL004 response-category table. Keep the source row `DO NOT ANALYZE` until numeric released-data coding and the no-fixed-address instruction are reconciled.
- **2013 and 2018:** the questionnaire includes `4=Abroad`, while the respective Codebook category tables list only options 1–3. The public catalogue now preserves the official questionnaire option and clearly marks the discrepancy; confirm storage in the authorized release before analysis.
- **2015:** the questionnaire and Codebook both list the Abroad category; release-specific special values, prior-job eligibility and denominator still require QA.

This is a retrospective, coarse geographic context, not commute distance, geocoded location or environmental dose. Address/place-name subfields remain excluded from public metadata. Reproduce the checks and synchronization with `python scripts/apply_last_job_workplace_location_review.py`. No respondent records or Codebook frequencies were used.
