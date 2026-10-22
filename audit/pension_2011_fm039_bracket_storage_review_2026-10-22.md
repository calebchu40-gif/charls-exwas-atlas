# 2011 FM039 unfolding-bracket storage and route review (2026-10-22)

## Sources

Reviewed the official 2011 Baseline Household Questionnaire, official 2011 Codebook, and the authorized user-local prepared Wave 1 table at `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\derived_wave_tables`. The protected table was read in memory only for these fields and route checks. No respondent identifiers, person-level rows, or small-cell outputs were written to the project or collaborator bundle.

The questionnaire describes FM038 as either a monthly Yuan amount or a percentage of pre-retirement salary. FM039 is an unfolding bracket with Yuan-labelled thresholds if the respondent is unwilling or unsure. The Codebook describes FM039 endpoints as Min/Max Bracket and reports a very large upper endpoint value (99,999,996), whose meaning is not explained in the reviewed documentation.

## Local storage findings

The local prepared table stores `fm039_a` and `fm039_b` as strings. Bracket records have both endpoints populated; an extreme upper endpoint matching the Codebook summary is present. Those records fall in the FM011=4 future-retirement route, but the `fm038` answer-format selector is empty for the bracket rows. This means the response-format branch (monthly amount versus salary percentage) cannot be recovered from the adjacent selector on these records. The Yuan thresholds suggest an amount bracket, but do not establish that the bracket is restricted to the amount branch.

## Decision

Keep the endpoint fields linked as candidate interval components for search and traceability. Continue `DO NOT ANALYZE`: do not use an endpoint as an exact amount, infer a midpoint, assume the unit branch from nearby fields, or recode the extreme value without an official definition. Resolution requires release-specific documentation or a validated route/format field that identifies the FM039 response unit and the meaning of the upper special value.

Reproducible local check used only `fm011`, `fm038`, `fm039_a`, and `fm039_b`; emitted aggregate/boolean QA and wrote no individual records.
