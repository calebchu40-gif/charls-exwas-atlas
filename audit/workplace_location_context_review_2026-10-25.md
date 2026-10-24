# Current workplace location context review — 2026-10-25

## Decision

Reviewed the current workplace location item `FD004` in 2011, 2013, 2015 and 2018. It is a coarse, self-reported geographic-context candidate among respondents routed into the employed-work section. It is not a commute-distance measure, an ambient pollution measure, or a personal environmental dose. The four waves remain separate source fields; matching response numbers do not establish cross-wave equivalence.

The 2011 questionnaire anchors responses to village/community, county/city, province and workplace address. It instructs the interviewer to enter `0` when the respondent has no fixed workplace address; this is retained as a source-specific special response requiring authorized-release storage verification, not presented as a fifth location category. The 2013 and 2015 instruments anchor the first categories to the permanent address and include “Other” and “Abroad”; both skip `FD004` for the individual-farmer/resident-household routes (`FD002=6/7`) to `FD011`. The 2018 questionnaire uses its own residence wording and records subcounty/workplace place-name details for applicable responses. These differences preclude automatic category pooling.

The 2020 field with a similar name is `FC004` and belongs to a separate concept; 2020 `FD004` is employee count. Neither is silently merged into this 2011–2018 mapping. Address/place-name text is not released by this public catalogue and must not be geocoded without a separate privacy and authorization review.

## Release and analysis gates

The review uses official questionnaires and Codebooks only. No participant records or Codebook frequencies were used. Before an analysis, verify the exact authorized-release variable names, special/missing codes, routing eligibility and person linkage. Restrict the denominator to people eligible for this current-work item; structural skips are not zero or “same location.” Treat response categories as nominal and keep wave-specific labels. Do not report associations until the applicable survey design, estimand, covariates and pair-level support are independently specified and reviewed.

## Reproducibility

Run `python scripts/apply_workplace_location_context_review.py` to validate the official text anchors and synchronize the four field statuses, response labels and caveats across the work crosswalk, E/P source index and public metadata JSON. This script does not read respondent-level data.

Sources: `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`, `CHARLS_2011_Codebook_extracted.txt`, and the corresponding 2013, 2015 and 2018 questionnaire and Codebook extractions.
