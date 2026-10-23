# 2018 actual and market monthly rent by property slot

This review covers six observed monthly-rent amounts (`HA006_W4`, indexed house slots 1–5 and 7) and seven market-rent estimates (`HA007_W4`, slots 1–7). The questionnaire reports both in Yuan/month and asks them within the current-household property loop for houses where the main respondent or spouse has a current ownership interest.

Actual monthly rent is routed after the corresponding `HA005_W4` answer is Yes. No or refusal skips the actual-rent amount; an absent amount must not automatically be treated as zero. The questionnaire also routes an entered zero to an unfolding-bracket follow-up. Market rent is a distinct estimate and must not replace actual rent or be summed with it as an observed payment. Keep property slots separate: their numeric positions are loop identifiers, not stable property identities across households.

These fields describe household property/rental resources, not the respondent's current home rent, and remain subject to special-value, bracket, route, denominator and linkage QA using the authorized release. No participant records or Codebook frequencies were copied. `scripts/apply_2018_property_rent_amount_review.py` applies the units and restrictions through both catalog pipelines.
