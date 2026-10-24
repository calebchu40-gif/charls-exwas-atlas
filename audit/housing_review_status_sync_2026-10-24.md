# Housing review status synchronization

The official-source reviews for household room/toilet counts and selected dwelling area/timing fields were already applied to the master catalogue and browser-facing JSON, but the food/housing source CSV retained generic “questionnaire review pending” labels. This made the public directory disagree with its own review notes and value/unit metadata.

The finalization scripts now propagate those reviewed statuses and field-specific caveats into `audit/food_environment_crosswalk_v1.csv` before the concept-source index is rebuilt. Reviewed fields are:

- 15 bedroom, living-room and toilet count wave-field entries from 2011 through 2020.
- 7 dwelling area and construction-year wave-field entries reviewed in `scripts/apply_housing_area_year_review.py`.

This clears 22 stale pending labels, reducing the housing crosswalk's generic pending/under-review entries from 74 to 52. The remaining rows are not marked reviewed by this change. A reviewed field identity or unit does not establish analytic eligibility: special-value storage, eligible denominator, respondent/household linkage, missingness, and cross-wave comparability remain subject to release-specific QA. For 2020 `i002`, the existing questionnaire/Codebook review citation is retained alongside the move-in-year clarification.

The rebuild used metadata, official questionnaire/Codebook extracts, and existing audit scripts only. No participant records, values, frequencies, or association results were used. Formal association models remain unrun. Validation: `python -m unittest discover -s tests` (347 passed), `python scripts/validate_do_not_analyze_triage.py` (89 locks matched), `git diff --check`, and `node --check site-prototype/dist/app.js`.
