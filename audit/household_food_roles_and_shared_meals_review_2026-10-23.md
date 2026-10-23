# Household food-purchaser roles and shared-meal count review

This review covers 15 fields across five waves: respondent-as-primary-food-purchaser (GE001 in 2011–2018; GF002 in 2020), identity of the primary purchaser (GE002; GF003), and household people usually eating meals together in the past week (GE004; GF004).

The yes/no purchaser item has stable `1=Yes; 2=No` labels in the questionnaire/Codebook. Its skip route leads a respondent who is the primary purchaser directly to the meal-count item. The purchaser identity item is a dynamic selector whose numeric choices refer to wave-specific household roster entries and, in later waves, other children or other persons. Those numeric codes do not identify a stable person or a portable exposure category; the atlas therefore records the roster-dependent nature of the response and leaves its fixed value-label list empty.

The shared-meal item is a household count in persons, excludes guests, and refers to people who usually ate meals together during the past week. Questionnaire soft checks (for example, a prompt at 10) are interviewer prompts, not analytic thresholds. Although the broad wording is similar across waves, roster and household composition can change; treat it as a household-context candidate and verify special values, wave-specific eligibility, respondent linkage and missingness in the authorized release before analysis. It is not an individual dietary frequency or nutrient exposure.

Only official questionnaires and Codebooks were used. Codebook frequencies and extrema were not copied. The reproducible metadata application is `scripts/apply_household_food_role_review.py` and runs in both the full and finalize-only catalog pipelines.
