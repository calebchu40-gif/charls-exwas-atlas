# CHARLS 2011 Community Questionnaire Part D coverage review

## Scope and inventory reconciliation

Reviewed the official 2011 Community Questionnaire Part D (printed pp. 17–18; PDF pp. 20–21), official Codebook field labels and metadata-only `audit/raw_variable_catalog_v1.csv`. The inventory contains 18 JD-prefixed fields: 17 substantive fields JD001–JD012 (including four JD004 product-category fields) and JD014, the informant-position field. All 17 substantive fields are mapped as community-context candidates; JD014 is C-only source metadata. The questionnaire also asks informant name (JD013) and phone (JD015), but those direct identifiers are absent from the field inventory and are not added to the public catalogue. No respondent data or Codebook frequencies/extrema were used.

## Candidate structure

| Component | Fields | Interpretation and boundary |
|---|---|---|
| Local non-agricultural household participation | JD001 | 2010 village-only household count; at least one household member engaged in local non-agricultural work. Not a respondent's occupation. |
| Self-employed businesses and enterprises | JD002–JD003 | End-2010 counts; the questionnaire defines an enterprise as having at least eight employees. Keep getihu and enterprise counts distinct. |
| Enterprise products | JD004S1–JD004S4 | Four emitted fields associated with the JD004 multi-response product-list item. Keep them separate because the questionnaire and Codebook field labels do not establish the authorized-release slot/value encoding; do not assume they are binary indicators, ranks, or distinct product types. |
| Local enterprise workforce | JD005–JD006 | End-2010 employee count and male count among that workforce; JD006 is village-only. Do not infer sex composition for missing/unspecified groups. |
| Local-firm wages and workdays | JD007_1/_2, JD008_1/_2, JD009 | Daily and monthly average salaries by sex (Yuan/day or Yuan/month), and average employee workdays per month in 2010. Keep daily/monthly measures separate; do not annualize or derive wage gaps before storage and denominators are checked. |
| Manual labor and nanny wages | JD010–JD012 | Village-only 2010 daily manual-labor wages by sex (Yuan/day), and monthly live-in nanny salary excluding meals/lodging (Yuan/month). The questionnaire does not establish that these are respondent wages. |

These are community-informant aggregates or estimates and generally refer to 2010. They are contextual candidates, not individual exposures, outcomes or covariates. Field-specific village-only routing, units, reference periods and enterprise definitions remain attached to source mappings. Special values and release-specific storage need authorized-data QA before analysis.

## C-only fields and exclusions

- JD014 reports the Part D informant's position; it is not a sampled CHARLS participant attribute and is retained only as measurement metadata, without response values.
- JD013 (informant name) and JD015 (telephone number) are direct identifiers. They are not added to the public catalog; no response data are processed.
- No derived community wage index, enterprise-density rate, or individual employment assignment is created.

## Validation and sources

The 17 candidate fields are present in the metadata-only inventory and anchored to the Part D questionnaire prompts and corresponding Codebook labels. The JD004 suffix fields are linked to the questionnaire's JD004 multi-response item, rather than pretending that each suffix is printed as a separate questionnaire question. Their release-level encoding remains unresolved. `audit/raw_variable_catalog_v1.csv` supports field-presence checks only; it does not establish participant-level values, special-code handling or analysis eligibility.

Sources: `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt`, `sources_official/CHARLS_2011_Codebook_extracted.txt`, `audit/raw_variable_catalog_v1.csv`, `audit/community_exposure_crosswalk_v1.csv`, and `site-prototype/dist/community_exposures_v1.json`.
