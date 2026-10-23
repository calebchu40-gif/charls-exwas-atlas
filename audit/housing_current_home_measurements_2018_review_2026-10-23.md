# 2018 current-home area, rent, value, and acquisition measures

Reviewed eight Wave 4 candidate fields against the official questionnaire extract (`sources_official/CHARLS_2018_Questionnaire_extracted.txt`, lines 10383–10423) and the corresponding exact field headings in the official Codebook extract (`sources_official/CHARLS_2018_Codebook_extracted.txt`). Codebook numeric summaries were used only to confirm that the fields are numeric/open measures; no values, extrema, or frequencies were copied.

| Field | Questionnaire definition | Unit shown | Interpretation retained |
|---|---|---|---|
| `i000_w4_11` | Usable area of current home | Square metres | Asked on the route where respondent/spouse does not own property rights; keep distinct from `i000_w4_12`. |
| `i000_w4_12` | Floor area of current home | Square metres | Ownership route; keep distinct from usable area and do not assume cross-wave equivalence. |
| `i000_w4_13` | Rent actually paid per month | Yuan/month | Interviewer may enter 0 when no rent is payable, but CAPI also triggers unfolding brackets when entered value is 0; route and bracket storage must be checked before interpreting zero. |
| `i000_w4_14` | Estimated market rent per month | Yuan/month | Separate from rent paid; bracket fields are interval metadata, not point estimates. |
| `i000_w4_15_1` | Current-home market total price | 10,000 Yuan | Alternative reporting format to unit price; do not combine without a validated format selector and area. |
| `i000_w4_15_2` | Current-home market unit price | 1,000 Yuan/square metre | Alternative reporting format to total price; do not convert without a validated area and format selector. |
| `i000_w4_16` | Year acquired or built | Calendar year | Preserve as a year, not age or duration; valid years and special values need authorized-data QA. |
| `i000_w4_17` | Amount spent to acquire or build the home | 10,000 Yuan | Historical acquisition/construction amount, distinct from current market value. |

All eight remain candidate metadata. The site leaves their discrete value-label lists blank, records questionnaire units, and states that Codebook summary extrema do not establish valid ranges. The ownership-conditioned area question, rent eligibility and zero/bracket behavior, alternative market-value formats, release-specific special values, denominators, and cross-wave compatibility remain analysis gates. No respondent-level data were read.

The review is applied reproducibly by `scripts/apply_2018_current_home_measurement_review.py`, which is included at the end of the full and finalize-only metadata pipelines. `scripts/build_housing_exposure_crosswalk.py` supplies the six housing-domain units; the two area fields remain in the existing dwelling-area concept mapping and retain their distinct Wave 4 question semantics in the field catalog.
