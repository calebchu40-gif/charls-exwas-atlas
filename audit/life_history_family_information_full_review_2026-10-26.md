# 2014 Life History FAMILYINFORMATION full-field disposition audit (2026-10-26)

## Scope

The official 2014 Life History Codebook contains 473 structured fields in `FAMILYINFORMATION`. The generated ledger `life_history_family_information_full_coverage_2014_v1.csv` gives every field exactly one disposition and preserves the Codebook field label. It contains no participant values or Codebook frequency statistics.

## Disposition counts

| Disposition | Fields | Meaning |
|---|---:|---|
| Mapped E/P candidate metadata | 431 | Mapped to the 2014 Life History crosswalk with concept ID, questionnaire item, and caveat |
| Deferred sibling living-status fields | 15 | Relative roster status without a defined event-time estimand |
| Deferred sibling education fields | 15 | Sibling attainment timing does not define a respondent phenotype |
| Deferred caregiver identity | 2 | Route-defining relationship metadata |
| Deferred parent birth year | 6 | Background/timing fields; event-age derivation not yet specified |
| Excluded person/household/community linkage keys | 3 | Join keys, never participant values for the public site |
| Excluded release version metadata | 1 | Not an E/P measure |
| **Total** | **473** | **Every Codebook field dispositioned once** |

The 431 mapped fields correspond to 42 concepts (1,005 E-role fields and 28 P-role fields) across the full separate Life History crosswalk; this FAMILYINFORMATION module contributes 431 of those source-field mappings. Concept and field counts are catalog metadata, not sample sizes or association results.

## Reproducibility and safeguards

`scripts/build_life_history_exposure_crosswalk.py` regenerates the full ledger. The builder fails if a new FAMILYINFORMATION Codebook field is not explicitly mapped or deferred/excluded, if any field appears more than once, or if the inventory size changes from 473 without an intentional review. `tests/test_build_life_history_exposure_crosswalk.py` asserts all 473 rows and the disposition totals. Exact source identity is the official Codebook module plus field code; frequency tables are never copied.
