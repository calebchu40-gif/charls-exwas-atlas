# 2020 current-employer location review — 2026-10-25

Reviewed official 2020 questionnaire `FC004` and Codebook. The item asks where the respondent's current employer is located, with residence-relative categories, a Hong Kong/Macao/Taiwan/abroad response, and `999` refusal. Conditional place-name fields are excluded from the public atlas. This is nominal geographic context, not commute distance or measured pollution; verify route, denominator, released coding and person linkage before analysis.

The crosswalk had inherited an unrelated “months in past year” unit from another work measure. Corrected it to “wave-specific nominal workplace location category; not a distance measure” across the domain crosswalk, final E/P source index and website JSON. No respondent records or frequencies were used. Reproduce with `python scripts/apply_2020_current_employer_location_review.py`.
