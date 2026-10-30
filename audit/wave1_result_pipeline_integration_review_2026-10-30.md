# Wave 1 results pipeline integration review

Date: 2026-10-30  
Scope: static inspection of the protected Wave 1 runner, canonical result schema, family finalizer and public-release validator. No CHARLS response values or model outputs were read; no model was fitted.

## Findings

1. The `pilot105` / `full240` runner writes a private execution-tranche CSV keyed by the registry's `hypothesis_id`, with private diagnostics such as pair-complete counts and support details. It is an analysis artifact, not a schema-v3 release table.
2. `finalize_atlas_primary_family.py` requires every input batch to pass the canonical schema-v3 validator and selects rows by `analysis_id`. The reviewed runner does not emit that canonical row contract. A reviewed adapter/normalization step is therefore needed between fitting and final family finalization; raw private runner CSVs must not be passed directly to the finalizer or release builder.
3. The multiplicity architecture is otherwise aligned with the written plan: pilot-tranche corrections are explicitly null/non-final; `finalize_atlas_primary_family.py` binds a frozen expected-ID manifest, rejects missing/extra/duplicate primary IDs, assigns one atlas-wide `family_id;K=...`, and applies BY/Bonferroni once across the complete frozen family. Non-estimable rows remain in the expected family and receive no fabricated adjusted value.
4. The finalizer also requires a separate hash-bound frozen-scope review. This is a distinct gate from the pilot's design/method approval and from the later disclosure review.

## Batch-to-schema constraint clarified

The result-table validator requires every successful row to contain both BY and Bonferroni values that recompute exactly over the table's declared `multiple_testing_family`; it also requires the table to contain exactly K rows. The `pilot105` runner intentionally emits no tranche q-values because the pilot is nested and the registered inferential family is K=240. Therefore, the pilot output must **not** be mislabeled as schema-v3 final results or sent to the finalizer. Keep pilot105 as a private execution/QA artifact. After the full predeclared 240-row execution and pair-level review, normalize the full240 output into one canonical K=240 table, calculating its family adjustments from the 240 raw p-values (non-estimable hypotheses remain in K and have blank p/q fields). The family finalizer may then re-bind the exact expected IDs and independently recompute the final correction from raw p-values; it must not use any pilot-tranche or per-block adjustment as input.

This makes the correct implementation target narrower and safer: a private full240 adapter, not a pilot105-to-release conversion. The adapter must require the full240 run manifest, exact frozen config and scope manifest, all 240 registered hypotheses, the full pair-review record, and SHA-256 bindings for its input artifacts. It must reject an incomplete or duplicate family, unsupported raw runner status, missing provenance, a successful fit without `estimability_review_status=reviewed_pass` plus review ID, or any missing raw p-value/estimate/SE/CI/model N for success. Failed/inestimable rows must have estimate and p-value fields blank. It must write only under private storage, retain exact counts and diagnostics privately, and pass the canonical validator before the finalizer can consume it. This adapter is future work after review gates; none of these artifacts exists yet and no model was fitted.

## Required implementation before result finalization

Create a private-only adapter that maps the runner's registered hypotheses and results into schema-v3 fields using the exact frozen config, model/run manifest, and pair-level review metadata. It must fail closed on any unregistered hypothesis, duplicate/missing ID, absent provenance field, unresolved estimability state, or inconsistent family scope. It must keep IDs, exact counts, raw support diagnostics and private hashes in protected files; public payload generation remains a separate disclosure-cleared step.

The adapter should preserve the distinction between `hypothesis_id` (pre-registered scientific coefficient) and `analysis_id` (versioned model result). It must not create public `n_model` values until aggregate disclosure review approves them. No association or result exists yet, so this review does not change the current formal model count.
