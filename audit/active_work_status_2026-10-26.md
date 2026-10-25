# CHARLS ExWAS Atlas active work status — 2026-10-26

## Current local state: v127 prepared

The last publicly deployed site remains v126 until this update is pushed and its Pages workflow succeeds. Local v127 adds source-reviewed 2013/2020 death and end-of-life candidate metadata and updates the wave-specific pair index. It does not contain participant-level records or computed associations.

## Mortality field review

- Added 11 source-field mappings: 2013 `Exit_Interview` (year/month of reported death, calendar selector, expectedness) and 2020 `Exit_Module` (year/month/day, calendar selector, expectedness, final-illness interval and its conditional year detail).
- Classified date, expectedness, and final-illness candidates as provisional P; the solar/lunar date selector is C metadata. The C display labels are localized in the browser catalog.
- 2013 response category labels are withheld because this pass verified official field labels but did not recheck the response-code sets. 2020 category labels are copied from official questionnaire wording, without frequencies.
- Exit-module information comes from decedent/proxy pathways. It does not define non-death as zero, an all-cohort event indicator, risk denominator, follow-up completeness, or censoring. 2013 has year/month fields; 2020 adds day. Solar/lunar calendar conversion and release-specific special/missing values require separate review before date pooling.
- 2018 cover-screen alive/dead routing was kept distinct from exit-module outcomes. No 2015 counterpart was inferred from neighboring waves.

Audit source: [`mortality_endpoint_mapping_review_2026-10-25.md`](mortality_endpoint_mapping_review_2026-10-25.md); source mappings: [`mortality_endpoint_crosswalk_v1.csv`](mortality_endpoint_crosswalk_v1.csv).

## Rebuild and current counts

All 157 metadata-finalization steps completed. The final local role shards contain E/P/C=6,008/2,116/984 rows; the catalog includes 1,557 E/P candidate concepts, 8,018 E/P concept-source mappings, and 3,733 explicitly labeled E/P rows. Generic `not yet reviewed` value-label rows are 0 for E/P and C. The analysis lock gate reports exactly 92 locks, unchanged.

The pair index contains 132,463 / 141,920 / 143,137 / 105,493 / 21,630 metadata co-availability pairs for 2011/2013/2015/2018/2020. These are not participant counts, eligible analytic N, or association results. Formal association models and actual pairwise-complete N remain 0.

## Verification

- Full local suite: 480 passed, 90 subtests passed.
- Public-site payload validator passed.
- `validate_do_not_analyze_triage.py` passed: all 92 catalog locks match the triage inventory.
- JavaScript syntax check passed; candidate pair cache key advanced to v5 and page entry point to app v127.
- GitHub validation and Pages deployment are pending until commit/push.

## Next work

Complete remote workflow verification and live-site checks for v127. Continue systematic variable-family coverage reviews without conflating catalog availability with analysis eligibility. Before mortality models, resolve source-version special values, date calendar conversion, respondent linkage, follow-up/censoring, weights and survey variance design. No mortality or other associations have been estimated.
