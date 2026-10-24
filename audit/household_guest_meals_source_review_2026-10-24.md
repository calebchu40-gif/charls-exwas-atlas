# Household guest-meal count source review

Reviewed 2026-10-24 from the official 2011, 2013, 2015, 2018 and 2020 questionnaires and wave Codebooks. The questionnaires ask how many meals the household provided to guests during the prior week. The 2011 and 2018 Chinese wording explicitly identifies the count as `人次`; 2020 asks about the main respondent's household. Codebooks identify the corresponding fields as guest-meal counts. The source review uses question wording and field titles only; Codebook summary means, ranges and observation counts are not copied or used as project sample sizes.

The reviewed wave-field candidates are 2011/2013/2015/2018 `GE005` and 2020 `GF005`. They are represented as a continuous count of guest person-meals over the previous week, with no invented categorical response labels. The questionnaire soft-check threshold is retained only as an instrument note and is not an analytic exclusion rule.

This is a household-level hosting/social-reciprocity proxy. It does not measure the respondent's food intake, diet quality or a pollutant exposure. When linked to people, retain the household unit and use an analysis design that accounts for shared household exposure; do not duplicate a household value into independent person-level observations. Exact authorized-release field identity, special/missing codes, routing and cross-wave measurement equivalence still require release-specific QA before harmonization or modeling. The catalogue maps candidate source fields; it does not assert that the waves are statistically interchangeable.

The repeatable source checks and metadata mapping are implemented in `scripts/build_residual_behavior_exposure_crosswalk.py`; no respondent records or Codebook frequency statistics were used.
