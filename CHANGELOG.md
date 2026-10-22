# Change log

This file records project-level changes that affect reproducibility, methods, data handling, or the local prototype. Individual variable audits remain documented in `audit/`.

## 2026-10-22

- Established the private GitHub repository `calebchu40-gif/charls-exwas-atlas` and pushed the local project on `main`.
- Added repository ignore rules for licensed respondent-level data, temporary outputs, locally derived sample/coverage QA tables, credentials, and machine-specific operational notes. These files remain local where needed and are not part of the Git history.
- Added GitHub Actions checks for the standard-library Python tests, website JSON parsing, and JavaScript syntax. The checks do not download CHARLS respondent data or run association models.
- Confirmed the current project is still in metadata and methods development: no CHARLS association models have been fitted and the website must continue to show zero reviewed results.
