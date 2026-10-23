# Toilet type and nearest-toilet distance review

This review covers 13 fields: toilet type and nearest-toilet distance in the 2011–2015 waves, the single toilet-type and distance items in 2018, and the renamed items in 2020.

The 2011–2015 questionnaire presents one toilet-type question with two options, while the extracted Codebooks list separate option-specific fields (`I014S1` without a seat and `I014S2` with a seat). The atlas records only the documented affirmative option for each field. Until the authorized-release storage and missing-value behavior are verified, absence or zero in one option-specific field must not be treated as the opposite category. In 2018 and 2020, a single field uses `1=Toilet without a seat; 2=Toilet with a seat`; the 2018 questionnaire says to choose the seated toilet if both types are present. These structures remain wave-specific.

Nearest-toilet distance is continuous and measured in meters. The question's reference is the respondent's/current household residence, with 2020 explicitly naming the financial respondent's house. The 2011–2018 questionnaires show a soft prompt above 500 meters; 2020 provides a different soft-check prompt. These prompts are not validated cutoffs. Codebook summaries contain extreme values in some waves, which are not copied and must not define valid ranges.

Both measures describe household sanitation/access context, not a measured contaminant or individual health outcome. Confirm release-specific special values, routes, respondent/household linkage and missingness before modeling. No participant data, Codebook frequencies or extrema were used. `scripts/apply_toilet_access_review.py` applies the field-specific metadata in the full and finalize-only catalog pipelines.
