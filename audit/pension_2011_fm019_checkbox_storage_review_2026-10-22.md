# 2011 FM019 pensionsource checkbox storage review (2026-10-22)

## Evidence reviewed

This review uses the official 2011 baseline household questionnaire, official 2011 Codebook, and the authorized user-local prepared Wave 1 table at `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\derived_wave_tables`. The protected table was read only in memory for field-presence, storage-pattern, and route-consistency checks. No respondent identifiers, row-level records, or small-cell outputs were written to the project or collaborator bundle.

The questionnaire defines FM019 as a choose-all-that-apply source item following FM018. Its routing text sends normal/early retirees through FM014–FM024 when FB011 indicates retirement and FM011 is 1/2; FM010 current pension recipients are routed to FM018. The Codebook lists the option-specific FM019 fields and their observed option labels.

## Local storage findings

All five fields `fm019s1`–`fm019s5` are present in the local Wave 1 prepared table. Non-empty entries are string option codes matching the slot number; unselected/not-populated entries are empty strings. There is no explicit “No” response code in these checkbox slots. Therefore the Codebook's displayed option index cannot by itself be treated as a respondent-level Yes/No value.

A route consistency check also found non-empty selections outside the apparent questionnaire route, including records not explained by the documented normal/early-retirement route or FM010 affirmative path. The field values alone cannot distinguish an unselected option from a field that was not asked. The eligible denominator and the out-of-route responses therefore remain unresolved.

## Decision

Keep all five fields searchable under the pension-source candidate concept, but retain `DO NOT ANALYZE`. Do not convert empty strings to No, build binary option indicators, infer a denominator, or include the fields in an association model. A future release-specific correction/official clarification or validated route metadata is needed to resolve the discrepancy.

Reproducible check: `pyreadstat` read only `fb011`, `fm010`, `fm019s1`–`fm019s5` from the user-local Wave 1 derived table; the check emitted only boolean QA and route-level aggregates, then wrote this qualitative finding without row-level data or counts.
