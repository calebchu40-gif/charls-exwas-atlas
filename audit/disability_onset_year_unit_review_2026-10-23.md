# CHARLS disability-onset year unit review

Date: 2026-10-23

The official disability crosswalk identifies DA006 numeric components as reported onset years and records wave-specific questionnaire/Codebook sources. The catalog now carries `calendar year` for all 22 phenotype-side continuous year fields across 2011–2018, including the 2018 prior-wave reported-year components. The concept-source crosswalk preserves this unit when it rebuilds the public wave-field catalog.

The update does not recode response values, infer onset from current disability status, or treat the response as biological onset or necessarily a physician-diagnosis year. Conditional disability and prior-wave verification routes remain explicit; structural skips, special values, and valid ranges still require authorized release-level QA. The 2018 `DA006_W4_*` verification fields with categorical `1=Yes; 99=Never Had It` remain categorical and were not assigned a year unit.

Validation: 67 unit tests pass. The finalization pipeline preserved the 7,544-row site catalog and the exact 33-entry `DO NOT ANALYZE` inventory. No respondent records or association models were used.
