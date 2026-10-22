# Change log

## 2026-10-22 (continued)

- Recorded official Wave 5 Sample Information and Sampling Weights hashes and a source-level verification checklist for the age-domain audit. The local prepared tables cannot yet be matched to those source archives, so the 2020 target age domain remains provisional.

This file records project-level changes that affect reproducibility, methods, data handling, or the local prototype. Individual variable audits remain documented in `audit/`.

## 2026-10-22

- Established the private GitHub repository `calebchu40-gif/charls-exwas-atlas` and pushed the local project on `main`.
- Added repository ignore rules for licensed respondent-level data, temporary outputs, locally derived sample/coverage QA tables, credentials, and machine-specific operational notes. These files remain local where needed and are not part of the Git history.
- Added GitHub Actions checks for the standard-library Python tests, website JSON parsing, and JavaScript syntax. The checks do not download CHARLS respondent data or run association models.
- Declared the preparation-script test dependencies (`pandas` and `pyreadstat`) so CI can import and test the wave-table preparation code reproducibly.
- Fixed the CI dependency setup; the run for commit `b77ca0e` passed all checks.
- Recomputed empty concept-link counts from the final website catalog and corrected an obsolete audit heading/count that had presented historical E/P fields as a current queue. The final catalog has 0 empty E IDs, 0 empty P IDs, and 717 empty C metadata/covariate rows; links remain candidates subject to scientific and design review.
- Added a CI guard that fails if a future website catalog contains an E/P row without a candidate concept link.
- Recorded the official wave-specific age/target-population limits: the 2020 guide says younger cohorts are no longer nationally representative after 2018. Added this limitation to the local prototype and marked the 2020 age domain as unresolved pending source-file verification.
- Changed respondent-data audit scripts to write aggregate QA under the private LocalAppData root by default and added a path guard against common cloud-sync folders. Updated handoff commands; local validation again passed for all five prepared tables and the 31-concept/945-pair availability build.
- Added a suppressed local-only Wave 5 age/weight coverage audit to evaluate the unresolved 45+ versus 50+ target-domain question; 50+ remains a candidate pending source-release verification, not a frozen analysis target.
- Confirmed the current project is still in metadata and methods development: no CHARLS association models have been fitted and the website must continue to show zero reviewed results.
