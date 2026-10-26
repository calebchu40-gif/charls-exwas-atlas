# 2011 parent-slot education source review (2026-10-26)

## Decision

Add four 2011 source fields (`ca009_1_`–`ca009_4_`) as one **discovery-only, repeated parent-slot education candidate**. Keep all four slots separate. Do not label them as the respondent's biological father or mother, combine them, or use them in a respondent-level association until the slot-to-relative and respondent-linkage rules are verified in the authorized release.

## Official source evidence

The 2011 baseline household questionnaire defines CA009 as the respondent's father's highest completed education and lists 11 attainment options. It then directs interviewers to repeat the same parent section for the respondent's mother, father-in-law and mother-in-law, in that order. The 2011 Codebook lists four generic `CA009` “Parent' Highest Level of Education” slots. This confirms a four-slot field family, but neither source ties suffixes `_1_`–`_4_` to those four relatives. The Codebook's slot tables also do not establish that all 11 questionnaire options are present in the released coding; do not assume codes 10 or 11 are available without authorized-release verification. A local metadata-only source-field inventory contains four CA009 slots; its file, row-count and archive-source details are intentionally not reproduced here.

The four source mappings therefore share one generic concept ID, `parent_slot_education_2011`, with explicit slot/linkage caveats. The Codebook field family is identified, but suffix-to-relative mapping, the questionnaire/Codebook response-menu discrepancy, release coding and skip behavior remain unresolved. The public catalogue uses the questionnaire response wording only as a provisional menu and displays the discrepancy; it does not claim those options are all observed or valid in each release field. No respondent records or values were accessed; Codebook frequencies are not used or reproduced.

## Analysis and harmonization boundary

- This is a family-context discovery candidate, not the respondent's own education.
- Parent, in-law and other relative slots must not be pooled. The slot suffix cannot currently establish relationship identity.
- Preserve the four source fields independently. Do not convert structural skips or unavailable parent information to “no schooling.”
- Do not harmonize these fields directly with 2013/2015 biological-parent education concepts until the 2011 slot relationship and release field coding are confirmed.
- No respondent-level exposure or association eligibility is granted by catalog presence; a relation-specific estimand, linkage check and eligible denominator would be required.

## Reproducibility

`scripts/build_parent_education_exposure_crosswalk.py` regenerates the four rows from the local metadata-only field inventory and cites both the official 2011 questionnaire and Codebook for field-family context. The generated public crosswalk contains the four source codes, generic labels, provisional questionnaire response wording and unresolved-code/linkage caveats, but no microdata, Codebook frequencies, file-level counts, sample summaries or archive manifest.
