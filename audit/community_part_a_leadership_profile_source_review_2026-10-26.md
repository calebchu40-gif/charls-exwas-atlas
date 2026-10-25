# CHARLS 2011 Community Questionnaire Part A: JA042 leadership profile source review

## Source and scope

Reviewed JA042 in Part A (questionnaire printed p. 5; PDF p. 8), the corresponding official Codebook field labels, and the metadata-only raw variable inventory. The questionnaire table names four positions: community director (community-only CAPI), village head, village secretary, and village accountant (village-only CAPI). For these four positions, the form requests education category, age, and years in position.

## E candidate mapping

| Measure | Verified source fields | Disposition |
|---|---|---|
| Education category | `ja042_1_1_` community director; `_1_2_` village head; `_1_3_` village secretary; `_1_4_` village accountant | Four separate role-specific concepts; preserve nominal education categories and do not convert the codes into a numeric score. |
| Age | `ja042_2_1_` through `ja042_2_4_` | One candidate profile concept with four role-labelled fields; unit years of age; keep role slots separate. |
| Years in position | `ja042_3_1_` through `ja042_3_4_` | One candidate profile concept with four role-labelled fields; unit years in position; keep role slots separate. |

These are single-wave, community-context candidates. They are not participant education, age, occupation or tenure, and they are not a default covariate set. Community-only and village-only eligibility must be respected. Candidate status does not establish that the reported leaders can be linked to participants or that these measures are appropriate adjustment variables.

## Unresolved slots

The metadata inventory and Codebook include `ja042_2_5_` (Age) and `ja042_3_5_` (How Long did He/She Hold this Position). The questionnaire table excerpt names only four positions and provides no fifth title. These two fields are therefore retained as C metadata with no assigned position, no categories and no E/P association role. Do not infer a fifth role from neighboring rows.

## Verification and limits

The questionnaire explicitly presents the education options; the site now displays the same questionnaire-based category labels across all four roles, including the illiterate category omitted from some slot-specific Codebook summaries. Do not convert these categories into an ordinal score. Codebook frequencies, minima/maxima, observations and respondent-level data were not used or reproduced. Validate release-specific codes, special missing values and the exact field-to-position link in an authorized release before any analysis.

Source: `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt` (JA042) and `audit/CHARLS_2011_Codebook_extracted.txt` (JA042 field labels only). Generated mappings: `audit/community_exposure_crosswalk_v1.csv`; public metadata: `site-prototype/dist/community_exposures_v1.json`.
