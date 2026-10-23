# 2011–2015 housing and property numeric-amount review

## Scope

Reviewed 40 still-pending E-role housing/property amount fields from the 2011, 2013, and 2015 questionnaires. They cover 2011 renovation spending, house acquisition/construction spending, and housing market values; 2013/2015 acquisition spending and current-residence market values; and 2011/2013 retrospective acquisition and demolition-compensation values.

## Measurement decisions

- Acquisition, construction and total market-value fields use the questionnaire reporting unit of 10,000 Yuan.
- Unit-area market-value fields use 1,000 Yuan per square metre.
- 2011 decorating/renovation expenditure uses Yuan.
- Current market total prices and unit-area prices remain separate measures. Per-house numbered slots remain components of a household housing roster and are not summed or treated as stable property IDs across people or waves.
- Each amount field has no discrete category labels assigned. Official questionnaire soft checks are interviewer prompts, not analytic cutoffs. Codebook frequencies and extrema are not copied into the atlas.
- The questionnaire reporting unit is documented, but the stored scale, special/missing codes, eligible denominator, and completeness of unfolding-bracket linkage still need confirmation using the authorized analysis release.

## Sources and implementation

The review uses the extracted official 2011 baseline and household questionnaires, the official 2013 and 2015 questionnaires, and the corresponding wave Codebooks. `scripts/apply_housing_numeric_measure_review.py` verifies source-code presence, propagates units and amount/no-category status to the candidate catalog and concept-source crosswalk, and records the remaining release-level limits. It is included in the full and finalize-only metadata pipelines.

No participant records, sample frequencies, or Codebook descriptive extrema were used. All 40 remain candidate exposures; the review does not declare them eligible for a final model.
