# Building floor and entrance access measures

This review covers eight housing fields in five waves: I008 in 2011, 2013, 2015 and 2018; and I006, I006_1, I006_2 and I010 in 2020.

The 2011–2018 I008 items ask which story the sampled residence is on and route to elevator questions when the floor is above the first floor. The answer is a numeric/ordinal floor position in storeys, not an environmental concentration; Codebook extrema are not used as valid ranges. The 2020 questionnaire changes the representation: I006 marks the ground/above-ground versus underground branch (`1=On the ground; 2=Underground`), I006_1 records the above-ground storey, and I006_2 records the underground storey. Keep the selector and two routed counts separate; do not create a signed unified floor without a prespecified rule.

2020 I010 counts steps to the main entrance of the household flat. It describes a household access barrier, not an individual's mobility test. The questionnaire supplies a hard check and a soft prompt; the latter is an interviewer prompt and neither defines a validated analytic range. The 2020 interviewer may record the answer when in the residence and certain, otherwise ask the respondent, so source and measurement mode differ from earlier interviewer-administered waves.

These fields remain wave-specific household/housing-context candidates until authorized-release routes, special values, residence/respondent linkage and cross-wave equivalence are verified. No participant data, Codebook frequencies, or Codebook extrema were used. The reusable application is `scripts/apply_building_floor_access_measure_review.py` and is part of both full and finalize-only catalog pipelines.
