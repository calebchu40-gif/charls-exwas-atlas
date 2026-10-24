# Housing review status synchronization

The official-source reviews for household room/toilet counts and selected dwelling area/timing fields were already applied to the master catalogue and browser-facing JSON, but the food/housing source CSV retained generic “questionnaire review pending” labels. This made the public directory disagree with its own review notes and value/unit metadata.

The finalization scripts now propagate those reviewed statuses and field-specific caveats into `audit/food_environment_crosswalk_v1.csv` before the concept-source index is rebuilt. Reviewed fields are:

- 15 bedroom, living-room and toilet count wave-field entries from 2011 through 2020.
- 7 dwelling area and construction-year wave-field entries reviewed in `scripts/apply_housing_area_year_review.py`.

This clears 22 stale pending labels, reducing the housing crosswalk's generic pending/under-review entries from 74 to 52. The remaining rows are not marked reviewed by this change. A reviewed field identity or unit does not establish analytic eligibility: special-value storage, eligible denominator, respondent/household linkage, missingness, and cross-wave comparability remain subject to release-specific QA. For 2020 `i002`, the existing questionnaire/Codebook review citation is retained alongside the move-in-year clarification.

A follow-up synchronization applied the separate official building-floor/access review to five-wave floor-position fields, the 2020 above/underground selector and child counts, and entrance-step count. Eight additional stale labels were cleared in the food/housing crosswalk, final source index, and browser JSON. The reviewed scopes include numeric/ordinal floor position, routed 2020 floor counts, and household entrance steps; authorized-release special values, routes, household/respondent linkage, missingness, and cross-wave equivalence remain unresolved. Pending/under-review rows fell from 52 to 44.

A further official-source review covered running-water access (`I017`, 2011–2018) and toilet flushability (`I015`, 2011–2018; `I014`, 2020). Nine more labels were synchronized. The 2015/2018 flushability skip for a seated toilet is retained as a route/eligibility caveat; no structural skip is coded No. The 2013/2015 items were checked in the original official questionnaire PDFs and transcribed into the short supporting extraction in `sources_official/CHARLS_2013_2015_housing_questionnaire_pages_extracted.txt`. The pending/under-review count is now 35. Other outstanding entries are the 2015 air-cleaner alias, bathing-facility labels, construction-year fallback intervals, 2018 area fields, electricity fields, 2011–2018 entrance-step items, nominal building structure, and remaining building-story fields.

The rebuild used metadata, official questionnaire/Codebook extracts, and existing audit scripts only. No participant records, values, frequencies, or association results were used. Formal association models remain unrun. Validation: `python -m unittest discover -s tests` (350 passed), `python scripts/validate_do_not_analyze_triage.py` (89 locks matched), `git diff --check`, and `node --check site-prototype/dist/app.js`.
