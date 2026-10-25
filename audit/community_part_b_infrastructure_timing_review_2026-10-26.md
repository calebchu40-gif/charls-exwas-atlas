# CHARLS 2011 Community Questionnaire Part B infrastructure and activity-facility review

## Scope and inventory reconciliation

Reviewed the official 2011 Community Questionnaire, official Codebook field labels, metadata-only `audit/raw_variable_catalog_v1.csv`, and the existing community crosswalk. Part B contains 127 raw JB-prefixed source fields in that inventory. All 127 now have an explicit disposition: 122 are represented in the community candidate crosswalk and five are retained as C-only measurement/source metadata. Questionnaire-only name and phone prompts JB039/JB041 are direct identifiers and are excluded from the raw metadata inventory and public catalogue.

The 122 crosswalk fields consist of the previously mapped infrastructure, transport, fuel/water, service and eldercare candidates, plus three valid historical timing fields and 42 JB029 activity-facility fields (14 facility/organization types × presence, initiator, and main funder). No respondent records, Codebook frequencies, extrema, or response text were used.

## Added candidate mappings

| Concept | Field(s) | Meaning and scope |
|---|---|---|
| `community_sewer_system_start_year` | `jb011` | Calendar year the community sewer system began operation; asked on the JB010 sewer-present route. |
| `community_sanitation_reconstruction_year` | `jb016` | Year of toilet/sewer reconstruction; village-only and conditional on JB015. |
| `community_electricity_first_available_year` | `jb022` | Year electricity first became available in the village; village-only. |
| 14 `community_*_context` concepts | `jb029_1_i_`, `jb029_2_i_`, `jb029_3_i_`, i=1…14 | Presence of each activity facility/organization, and conditional nominal categories for who initiated and primarily funded it. |

The 14 JB029 types are basketball court, swimming pool, outdoor exercise facilities, table-tennis table, card/chess room, table-tennis room, calligraphy/painting association, dance/exercise organization, organization helping older or disabled residents, employment service center, elderly activity center, elderly association, nursing home, and other entertainment facilities. These are community-level context indicators, not participant use, individual access, or measured activity. The initiator/funder fields are asked only after a Yes response; skipped follow-ups are structural missingness, not a No or absence.

The three year fields are separate constructs. Do not combine them into one sanitation/electricity rollout date. Numeric years have no fabricated category labels; actual ranges and special codes require release-specific analysis review. Community-level reports cannot be assigned to individuals without an authorized, justified linkage and a declared estimand.

## C-only metadata and exclusions

- `jb009_1`, `jb013_1`, `jb033_1`, and `jb035_1` are other-specify text fields for heating fuel, toilet type, eldercare service, and eldercare funding. Their existence is documented, but response text is not published or tokenized.
- `jb040` records the Part B informant identity/role; it is not a sampled participant characteristic and is not an adjustment covariate.
- Questionnaire prompts JB039 (informant name) and JB041 (telephone number) are direct identifiers. They are excluded; no response data are processed.
- Parent question IDs such as JB006/JB007/JB009/JB028/JB029/JB033 are questionnaire anchors, not extra raw columns; their emitted child fields are audited individually.

## Sources and validation

- `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt`: Part B, especially JB010–JB016 and JB022 (PDF pp.11–12), JB029 table and skip rules (PDF pp.13–15), and the respondent identity/name/phone prompts.
- `sources_official/CHARLS_2011_Codebook_extracted.txt`: exact JB field labels and response-category definitions only; descriptive counts and extrema were not used.
- `audit/raw_variable_catalog_v1.csv`: metadata-only release inventory used for the 127-field reconciliation.
- `audit/community_exposure_crosswalk_v1.csv` and `site-prototype/dist/community_exposures_v1.json`: generated candidate source mappings and public metadata.

All mappings remain candidate metadata; this review does not establish analysis eligibility, wave harmonization, an individual exposure measure, or any association result.
