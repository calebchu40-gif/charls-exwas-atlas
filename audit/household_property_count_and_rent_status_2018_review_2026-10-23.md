# 2018 household property count and rent status

This batch covers the 2018 `HA000_W4_0` house-property count and seven slot-specific `HA005_W4` rent-status fields.

The count includes properties for which the main respondent or spouse is named on the property-rights certificate. The questionnaire specifies 0 when there is no property and routes new households to this item; previously interviewed households proceed through a prior-property listing loop. Thus this is not the number of dwellings occupied by the respondent and its route must be preserved.

Each `HA005_W4` field asks whether its indexed house is for rent. Questionnaire/Codebook labels are `1=Yes; 2=No; 999=Refuse to answer`; No and refusal skip the rent-amount follow-up. The seven slots are not stable property identities across respondents and should not be collapsed into a single exposure without a prespecified property-level rule. These items represent household assets/rental context, not the current residence's own rental status.

No Codebook frequencies or participant values were copied. Check authorized-release routing, special values, slot correspondence, household linkage and missingness before modeling. Metadata application is reproducible through `scripts/apply_2018_household_property_rental_status_review.py` in both catalog pipelines.
