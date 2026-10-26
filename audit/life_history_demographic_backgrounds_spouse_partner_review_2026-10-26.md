# 2014 Life History DEMOGRAPHICBACKGROUNDS spouse/partner section review (2026-10-26)

## Scope and source basis

Reviewed the official Life History Questionnaire spouse/partner section (printed pp. 7–18; PDF pp. 11–22) against Codebook module `DEMOGRAPHICBACKGROUNDS`. The review uses questionnaire wording, item routes, Codebook field identifiers and field titles. It does not use Codebook frequency tables, respondent-level values, or named spouse/partner data. Field-level coverage is written to `audit/life_history_demographic_backgrounds_full_coverage_2014_v1.csv`; the reproducible catalog builder is `scripts/build_life_history_exposure_crosswalk.py`.

## Mapped E candidate groups (114 source fields)

| Concept | Fields | Interpretation |
| --- | ---: | --- |
| `life_history_marital_union_history` | 40 | Ever having a spouse/partner; repeated legal-marriage status, year, voluntariness, continued co-residence, separation reason/year, death year, divorce and year. Marriage and non-marital partnership histories are not conflated. |
| `life_history_nonmarital_cohabitation_history` | 28 | Partner cohabitation start, living arrangement, reason for not marrying, continued co-residence, ending reason/year and conditional partner-death year. The questionnaire defines a partner as a long-term co-resident without marriage ceremony or registration. |
| `life_history_marital_hukou_transitions` | 21 | Hukou-location/type changes associated with marriage and divorce, retaining event and route distinctions. |
| `life_history_marital_residential_transitions` | 15 | Coarse residence arrangement/locality after marriage and move after marital relationship breakdown. |
| `life_history_nonmarital_partner_residential_transitions` | 6 | Whether and where the respondent moved after non-marital partner relationship ended. |
| `life_history_spouse_partner_education` | 4 | Highest education of spouse/partner, explicitly a relative/household-context candidate rather than respondent education. |

Repeated slots remain component fields under six concepts; they are not separate people-level exposures. All concepts are candidate metadata only, not approved analytic variables or associations.

## Source conflicts, routes and privacy boundaries

- The questionnaire asks P012c for the new hukou type after P012b=Yes, but no P012c field appears in the official Codebook inventory. The catalog does not invent a variable or infer that the answer was stored elsewhere.
- Questionnaire death-cause items P009a and P019a are open text; no linked structured Codebook field is added to the public E/P catalog. The questionnaire's spouse-name preload P001b is not exposed.
- P020a asks whether another spouse/partner remains to be entered and routes back to the roster start; its five fields are C-only loop metadata, not independent exposures. P025 and PC001–PC003 are interview/proxy metadata. `rgender` is redundant respondent metadata, not a new historical construct.
- Twelve spouse/partner birth-date fields are excluded from the public candidate catalog. Ninety party-membership, minority-identity and religion roster fields are held as `deferred_sensitive_relative_identity` pending separate data-minimization, release and disclosure review; no responses or frequencies are published.
- P005c/P011b/P013c/P018b are coarse locality categories, not addresses, distances, geocodable residence, or environmental measurements. Marriage and divorce routes remain distinct; routed blanks are not No.
- The Life History release note states that no weight is provided. These retrospective 2014 candidates remain outside the regular-wave weighted E/P pair universe unless a separate target population and design are justified.

## Current full-module disposition

The module ledger now assigns exactly one status to all 1,920 Codebook fields:

| Disposition | Fields |
| --- | ---: |
| Mapped E candidate metadata | 114 |
| Deferred demographic/child-family section review | 1,420 |
| Deferred hukou section review | 270 |
| Deferred sensitive relative-identity fields | 90 |
| Excluded spouse/partner birth-date components | 12 |
| C-only partner-loop metadata | 5 |
| C-only interview/proxy metadata | 4 |
| Excluded linkage keys | 3 |
| C-only redundant respondent-gender metadata | 1 |
| Excluded release metadata | 1 |
| **Total** | **1,920** |

The counts reflect unique Codebook field identities. Deferred fields are visibly unresolved and are not silently counted as mapped indicators. The next reviews should follow the questionnaire's children/family and hukou sections.

## Reproducibility and safeguard

Run `python scripts/build_life_history_exposure_crosswalk.py` to rebuild the special-wave concept catalog and exhaustive module coverage. The builder fails if the module no longer contains exactly 1,920 unique fields or if a field is duplicated. The Life History JSON contains field metadata only; no individual identifiers, responses, frequencies or association results are included.
