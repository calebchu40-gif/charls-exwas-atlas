# CHARLS 2011 Community Questionnaire Part H source coverage review

## Scope and inventory

Reviewed Community Questionnaire Part H, “Community History” (printed pp. 28–34; PDF pp. 31–37), against the official questionnaire, Codebook and metadata-only raw variable inventory. Part H should be answered by two or three older residents familiar with community history. The inventory contains 75 JH-prefixed fields; 60 are mapped to nine community-history E candidate concepts (including the existing school-history concept), and 15 are excluded from E/P as interview logistics, informant attributes or unstructured text.

## Mapped concepts and source fields

| Concept | Fields | Interpretation boundary |
|---|---|---|
| `community_land_institutional_transition_history` | JH003–JH008_1 (7 fields) | Village-level dates for commune formation/dissolution, household-responsibility system, land reallocation and the first permission to transfer/subcontract land to relatives/non-relatives. Retain distinct events and V-only routes. |
| `community_sent_down_youth_migration_history` | JH009–JH013_2 (7 fields) | Retrospective community counts, timing and reported origins of rusticated youth; not a cohort member's personal migration history. |
| `community_barefoot_doctor_capacity_history` | JH014 | Recalled number of barefoot doctors in the village during the 1970s; not current services or individual care use. |
| `community_primary_school_change` | JH015–JH017 (3 fields) | Whether/when primary schools were merged or dissolved in the past 20 years and prior school count. JH016 (year) is now included. |
| `community_military_service_history` | JH018_1[1–11] (11 fields) | Community counts of residents joining the army by the questionnaire's distinct year/period slots. Slot-to-period mapping is stored in each field caveat; no denominator is available. |
| `community_university_admission_history` | JH018_2[1–11] (11 fields) | Community counts of university admissions by distinct year/period slots; not individual cohort education attainment. |
| `community_family_planning_policy_history` | JH019–JH025 and JH030 (8 fields) | Community-reported policy timing/type/change for Han and minority residents and the historical “late, sparse, few” policy. Keep policy periods and categories separate; not individual fertility or reproductive history. |
| `community_unplanned_birth_penalty_policy_history` | JH026, JH026_1, JH027–JH029b[3] (10 fields) | Community policy presence, start year and initial/change amounts. Preserve conditional routes and separate year/amount slots. |
| `community_identity_card_rollout_history` | JH032–JH033 (2 fields) | Recalled community timing of first- and second-generation national ID-card rollout; not an individual's verified document history. |

## Explicit exclusions

- JH001_1–JH001_5: meeting date/time and attendee count describe the community-history elicitation session, not a community exposure or cohort phenotype.
- JH002_1_* through JH002_3_*: education, sex and age of up to three community-history informants. These are informant attributes, not the CHARLS sampled participant's covariates; occupation/contact entries are not in the structured numeric field inventory.
- JH031: conditional open-text description of “late, sparse, few” policy. It is not a standardized structured measure and is omitted from quantitative E/P concepts.

## Coding, harmonization and analysis limits

Questionnaire-anchored response categories are included only where the Codebook provides categories; frequency summaries are omitted. JH026_1 is a numeric year asked only after JH026=Yes, so it is marked as a reviewed continuous year field with no discrete labels. JH018 array slots retain their official period mapping in per-field caveats. These items are one-wave, retrospective reports from community-history informants; recall error, source release coding, respondent-to-community linkage, valid denominators, survey weights/variance design and modeling eligibility remain unverified. No household or participant-level exposure is inferred from community-level reports.

Sources: `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt`, `audit/CHARLS_2011_Codebook_extracted.txt`, and `audit/raw_variable_catalog_v1.csv`. Generated crosswalks: `audit/community_exposure_crosswalk_v1.csv` and `audit/community_exposure_value_labels_v1.csv`. No participant-level values or Codebook frequencies were used.
