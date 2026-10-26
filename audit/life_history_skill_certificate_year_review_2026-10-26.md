# 2014 Life History skill-certificate acquisition-year review (2026-10-26)

## Scope and source evidence

Reviewed E133–E134 in the official 2014 Life History Questionnaire (printed p. 103; extracted questionnaire p. 103) against the `EDUCATIONHISTORY` Codebook. E133 asks whether the respondent has ever received a vocational skill certificate. E134 asks for certificate type/name and year. The official Codebook inventory contains five fields `e134_2_1_` through `e134_2_5_`, each labelled as year of getting certification; it contains no corresponding certificate-name field.

## Mapping decision

The five year fields are now mapped to `life_history_skill_certificate_acquisition_years`, a distinct E candidate. The mapping represents only reported certificate-acquisition years in repeated slots. It does not supply certificate type, qualification level, credential domain, current validity, or a confirmed one-to-one link to E133. Questionnaire source: `sources_official/CHARLS_Life_History_Questionnaire.pdf`; Codebook source: `sources_official/CHARLS_Life_History_codebook.pdf`.

Before analysis, the authorized data release must confirm how open-text certificate names are stored (if at all), whether each year slot is paired by suffix, special/missing values, and event ordering. Do not infer the type of certificate, derive a number of certificates, or treat an empty slot as no certificate. No participant responses, certificate names, frequencies, or association results are published. The 2014 special-wave release has no survey weight and remains outside the regular-wave weighted pair matrix.

## Education History module disposition

All 1,105 Education History Codebook fields now have unique dispositions: 1,077 candidate mappings, 22 sensitive school-location fields excluded, three linkage keys, one no-observation release marker, one data-quality flag, and one release-version field. There are no unresolved generic fields. The complete field ledger is `audit/life_history_education_history_coverage_2014_v1.csv`.
