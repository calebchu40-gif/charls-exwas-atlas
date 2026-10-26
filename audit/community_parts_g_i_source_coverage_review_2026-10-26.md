# CHARLS 2011 Community Parts G and I source-coverage review

## Scope and source handling

Reviewed all 123 fields in the sanitized metadata-only 2011 community inventory whose codes begin JG or JI (Part G: 62; Part I: 61) against the official 2011 Community Questionnaire and Codebook. Crosswalk coverage is 120/123. The remaining three fields have explicit non-E/P dispositions below. This review uses variable names, labels, question wording, routes, and official codebook labels only. It does not use participant records or codebook frequency summaries.

## JG008: unresolved subsidy-amount construct

The questionnaire routes a “No” answer at JG005 to JG008. JG005 belongs to the minimum-living-allowance section. JG008's English prompt says “average subsidies standard,” while the Chinese prompt explicitly asks for the average unemployment subsidy standard. This conflicts with both the section context and the existing unemployment-subsidy items JG001–JG004. The Codebook's short label (“Average Subsidies Per Month”) does not resolve the construct. JG008 is therefore retained as C-only source-conflict metadata, with no amount unit or E/P concept assigned. It must not be treated as unemployment or minimum-living-allowance amount until the questionnaire, Codebook, and authorized release can be reconciled.

## JG042: informant identity and source-label conflict

The questionnaire calls JG042 the identity/position of the Part G respondent and lists community-informant positions. The Codebook labels the field “Respondent Identity for Part D.” Retain it as C metadata only; do not publish response values, treat it as a participant attribute, or use it as an adjustment covariate. The questionnaire/Codebook section mismatch is explicitly recorded.

## JI002_other: unstandardized open response

The questionnaire's “other” disaster follow-up asks for a free-text specification. It is already represented in the candidate field catalogue as C measurement metadata and intentionally excluded from E/P because no standardized categories are documented. Do not publish, tokenize, or infer categories from response text.

## Remaining mapped content and analysis limits

All other 120 JG/JI inventory fields map to community-context candidate concepts in `community_exposure_crosswalk_v1.csv`. These include program availability, start years, aggregate recipient counts and subsidy standards, disaster occurrence/types/severity, retrospective disaster history, and event impacts. They are community-informant reports, not automatically participant-level exposures. Preserve each source field, reference period, respondent unit, route, and unit; do not collapse categories or calculate rates without a verified denominator. All mappings remain candidate metadata with analysis eligibility pending.

## Reproducibility and source files

- Inventory: `audit/community_field_inventory_2011_v1.csv` (719 rows; sanitized four-column metadata only).
- Candidate crosswalk: `audit/community_exposure_crosswalk_v1.csv`.
- Explicit C-only dispositions: `audit/catalog_role_override_review_v1.csv` for JG008 and JG042; the existing JI002_other disposition is in the same file.
- Official sources: `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt` and `audit/CHARLS_2011_Codebook_extracted.txt`.
- Automated coverage and conflict assertions: `tests/test_community_parts_g_i_source_coverage.py`.
