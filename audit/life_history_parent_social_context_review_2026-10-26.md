# 2014 Life History parent/caregiver social-context review (2026-10-26)

## Scope and source identity

Reviewed the official CHARLS 2014 Life History Questionnaire, printed pages 43–45 (PDF extraction around pages 46–49), and the matching `FAMILYINFORMATION` Codebook labels. The C1_g1 party-membership, C1_g2 minority-status, C1_g2_1 ethnic-group, and C1_g3 religious-belief fields comprise 36 structured option/loop fields: nine each. The generated ledger `life_history_parent_social_context_coverage_2014_v1.csv` confirms each Codebook field maps exactly once. Codebook frequencies and respondent values are not used.

## Item interpretation and route

- C1_g1 asks which listed biological/adoptive/step parent or caregiver was a Communist Party member; it includes a none option.
- C1_g2 selects which listed parent/caregiver was an ethnic minority; C1_g2_1 asks the ethnicity category only for selected relatives.
- C1_g3 asks which listed parent/caregiver had a religious belief; it includes a none option.
- These are retrospective family-of-origin context items. The option slots refer to relative categories, not nine independent participants or exposures. The public catalog does not publish relative identities or infer negative responses from blank slots.

## Translation caveat

The English C1_g3 option 8 refers to the male caregiver/A4b slot, while the Chinese text repeats the female caregiver/A4a reference. The discrepancy is retained verbatim as a caveat; no slot-to-relative correction is assumed. Actual release storage, selector coding, route, and roster alignment require authorized-release QA before analysis.

## Atlas disposition

Added four E-role candidate concepts with 36 source-field mappings. Party membership, minority status, ethnicity group, and religious belief remain separate; C1_g2 selector fields and C1_g2_1 category fields are not merged. These historical family-context measures are not the respondent's own political, ethnic, or religious characteristics and are not recommended adjustment covariates. The 2014 Life History survey remains a separate special survey with no released weight; no association result or analytic eligibility is implied.

## Reproducibility

`scripts/build_life_history_exposure_crosswalk.py` regenerates the crosswalk, Life History JSON, and this batch's 36-row field coverage ledger. The dedicated unit test verifies all 36 fields, unique mapping, four concept counts, and persistence of the C1_g3 language caveat.
