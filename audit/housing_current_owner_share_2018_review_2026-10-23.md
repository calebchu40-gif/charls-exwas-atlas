# 2018 current-home ownership-share review

Reviewed five Wave 4 fields in the `current_home_owner_share` candidate family: `i000_w4_4_1`, `i000_w4_4_3`, `i000_w4_4_6`, `i000_w4_4_7`, and `i000_w4_4_8`.

The official Wave 4 HA&I questionnaire asks which parties hold rights to the respondent's current home and records percentage shares for listed relationship categories. The five source descriptions also identify percentage ownership shares. These are continuous numeric percentage responses, not categorical value labels. The public catalog therefore shows the unit as “% of the specific house's property rights” and leaves the discrete-label field blank.

The questionnaire includes additional relationship categories and follow-up questions beyond these five numeric fields. The five fields must not be presented as a complete ownership composition. Preserve each source slot and its household/house route. Do not sum values across relationship slots or infer an individual's ownership share from household-level responses. The questionnaire's interviewer instruction for the “Other” route can imply a 100% entry in a particular circumstance; this is a route-specific instruction, not a general rule for imputing missing shares.

The Codebook supplies descriptive numeric summaries. Those extrema are not treated as permissible ranges and no summary statistics or response frequencies are copied into the public site. Special values, numeric storage, eligible denominator, route-specific applicability, and missing-slot semantics still require verification in the authorized release before analysis. The fields remain candidates; this review does not approve an association model or a cross-wave harmonized variable.

Rebuild the housing mapping, then apply the review to field-level catalogs with:

```powershell
python scripts/build_housing_exposure_crosswalk.py
python scripts/apply_2018_current_home_measurement_review.py
```

The application script checks that exactly the five reviewed Wave 4 codes and the continuous-percent unit are present, preserves empty categorical labels, and changes metadata only. It does not read participant-level data.
