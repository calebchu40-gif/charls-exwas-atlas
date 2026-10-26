# 2011 parent-slot education source review (2026-10-26)

## Decision

Add four 2011 source fields (`ca009_1_`–`ca009_4_`) as one **discovery-only, repeated parent-slot education candidate**. Keep all four slots separate. Do not label them as the respondent's biological father or mother, combine them, or use them in a respondent-level association until the slot-to-relative and respondent-linkage rules are verified in the authorized release.

## Official source evidence

The 2011 baseline household questionnaire defines CA009 as the respondent's father's highest completed education and lists 11 attainment categories, from no formal education through doctoral degree. The same questionnaire instructs the interviewer to repeat the parent section for the respondent's mother and both parents-in-law. This establishes a repeated family-relative question family, but the public questionnaire does not identify which of the four data suffixes maps to which relative. A local metadata-only source-field inventory contains four CA009 slots with the generic label “Parent' Highest Level of Education”; its file, row-count and archive-source details are intentionally not reproduced here.

The four source mappings therefore share one generic concept ID, `parent_slot_education_2011`, with explicit slot/linkage caveats. The categories come from the official questionnaire; Codebook-specific field identity, release coding, skip behavior and slot assignment remain unverified. No respondent records, values, or Codebook frequencies were accessed for this review.

## Analysis and harmonization boundary

- This is a family-context discovery candidate, not the respondent's own education.
- Parent, in-law and other relative slots must not be pooled. The slot suffix cannot currently establish relationship identity.
- Preserve the four source fields independently. Do not convert structural skips or unavailable parent information to “no schooling.”
- Do not harmonize these fields directly with 2013/2015 biological-parent education concepts until the 2011 slot relationship and release field coding are confirmed.
- No respondent-level exposure or association eligibility is granted by catalog presence; a relation-specific estimand, linkage check and eligible denominator would be required.

## Reproducibility

`scripts/build_parent_education_exposure_crosswalk.py` regenerates the four rows from the local metadata-only field inventory and uses only the official 2011 questionnaire for the response menu. The generated public crosswalk contains the four source codes, generic labels, categories and caveats, but no microdata, file-level counts, sample summaries or archive manifest.
