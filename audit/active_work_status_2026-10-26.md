# CHARLS ExWAS Atlas active work status — 2026-10-26

## Current public state: v127; local metadata update prepared

v127 (commit `7b00491`) is deployed. GitHub Validate run [`40213942542`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40213942542) and Pages Deploy run [`40213942548`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40213942548) completed successfully. The public site is verified at app v127 and pair-index v5. It contains source-reviewed 2013/2020 death and end-of-life candidate metadata, no participant-level records or computed associations.

## Mortality field review

- Added 11 source-field mappings: 2013 `Exit_Interview` (year/month of reported death, calendar selector, expectedness) and 2020 `Exit_Module` (year/month/day, calendar selector, expectedness, final-illness interval and its conditional year detail).
- Classified date, expectedness, and final-illness candidates as provisional P; the solar/lunar date selector is C metadata. The C display labels are localized in the browser catalog.
- 2013 response category labels are withheld because this pass verified official field labels but did not recheck the response-code sets. 2020 category labels are copied from official questionnaire wording, without frequencies.
- Exit-module information comes from decedent/proxy pathways. It does not define non-death as zero, an all-cohort event indicator, risk denominator, follow-up completeness, or censoring. 2013 has year/month fields; 2020 adds day. Solar/lunar calendar conversion and release-specific special/missing values require separate review before date pooling.
- 2018 cover-screen alive/dead routing was kept distinct from exit-module outcomes. No 2015 counterpart was inferred from neighboring waves.

Audit source: [`mortality_endpoint_mapping_review_2026-10-25.md`](mortality_endpoint_mapping_review_2026-10-25.md); source mappings: [`mortality_endpoint_crosswalk_v1.csv`](mortality_endpoint_crosswalk_v1.csv).

## Rebuild and current counts

The previous public v127 build completed all 157 metadata-finalization steps. The current local rebuild completed 158 steps and contains E/P/C=6,020/2,116/984 rows; 1,559 E/P candidate concepts, 8,030 E/P concept-source mappings, and 3,740 explicitly labeled E/P rows. Generic `not yet reviewed` value-label rows are 0 for E/P and C. The analysis lock gate remains exactly 92 locks. Two provisional 2011 community elder-care context concepts and 12 source fields were added; see [`community_eldercare_context_source_review_2026-10-26.md`](community_eldercare_context_source_review_2026-10-26.md).

The current pair index contains 132,889 / 141,920 / 143,137 / 105,493 / 21,630 metadata co-availability pairs for 2011/2013/2015/2018/2020. These are not participant counts, eligible analytic N, or association results. Formal association models and actual pairwise-complete N remain 0. The updated directory is live from Pages Deploy [#249](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40217511361); application cache identifiers remain v127/v5 because application code did not change. The follow-up CI test fix passed Validate [#505](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40217765152).

## Verification

- Current rebuild: all 158 finalization steps completed. Full local suite: 482 passed, 90 subtests passed in 15.09 seconds.
- Public-site payload validator passed.
- `validate_do_not_analyze_triage.py` passed: all 92 catalog locks match the triage inventory.
- JavaScript syntax and deferred-loader checks passed; candidate pair cache key remains v5 and page entry point remains app v127.
- GitHub Pages Deploy #249 published the updated directory; GitHub Validate #505 passed after a CI-only source-test correction. The live homepage reports the new counts over HTTPS.

## Next work

Record and publish the validated 2011 elder-care update, then continue systematic variable-family coverage reviews without conflating catalog availability with analysis eligibility. Before mortality models, resolve source-version special values, date calendar conversion, respondent linkage, follow-up/censoring, weights and survey variance design. No mortality or other associations have been estimated.
