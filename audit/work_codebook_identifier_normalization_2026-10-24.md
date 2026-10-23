# CHARLS 2011 work Codebook identifier normalization

Updated 2026-10-24. The extracted 2011 Codebook frequently renders identifiers with spaces where the catalogue and questionnaire use underscores (for example, `fd005 indc` versus `fd005_indc`, and `fm017 a` versus `fm017_a`). The work-label parser now normalizes punctuation and spaces for exact field lookup while retaining the complete identifier and question title in the mapping.

This matters for source traceability and type classification. Fields such as `fd021_1` (years) and `fm017_a` (minimum bracket bound) are now recognized as Codebook fields with numeric/date metadata and no discrete response menu. Occupational and industry identifiers such as `fd005_indc` are explicitly marked as classification codes rather than numeric scales or answer choices; their meanings require the matching official classification lookup. Category labels that are present in the Codebook remain attached to the field, while printed frequency columns are stripped and excluded.

The parser still reports categories as wave-specific and keeps special source conflicts and routing locks intact. A regression test checks spaced identifiers, numeric/date fields, classification-code status, and extraction of a categorical menu without frequency text. The change is metadata-only and does not read respondent records.
