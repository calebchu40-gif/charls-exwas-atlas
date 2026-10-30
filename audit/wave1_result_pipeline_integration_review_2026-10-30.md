# Wave 1 results pipeline integration review

Date: 2026-10-30  
Scope: static inspection of the protected Wave 1 runner, canonical result schema, family finalizer and public-release validator. No CHARLS response values or model outputs were read; no model was fitted.

## Findings

1. The `pilot105` / `full240` runner writes a private execution-tranche CSV keyed by the registry's `hypothesis_id`, with private diagnostics such as pair-complete counts and support details. It is an analysis artifact, not a schema-v3 release table.
2. `finalize_atlas_primary_family.py` requires every input batch to pass the canonical schema-v3 validator and selects rows by `analysis_id`. The reviewed runner does not emit that canonical row contract. A reviewed adapter/normalization step is therefore needed between fitting and final family finalization; raw private runner CSVs must not be passed directly to the finalizer or release builder.
3. The multiplicity architecture is otherwise aligned with the written plan: pilot-tranche corrections are explicitly null/non-final; `finalize_atlas_primary_family.py` binds a frozen expected-ID manifest, rejects missing/extra/duplicate primary IDs, assigns one atlas-wide `family_id;K=...`, and applies BY/Bonferroni once across the complete frozen family. Non-estimable rows remain in the expected family and receive no fabricated adjusted value.
4. The finalizer also requires a separate hash-bound frozen-scope review. This is a distinct gate from the pilot's design/method approval and from the later disclosure review.

## Required implementation before result finalization

Create a private-only adapter that maps the runner's registered hypotheses and results into schema-v3 fields using the exact frozen config, model/run manifest, and pair-level review metadata. It must fail closed on any unregistered hypothesis, duplicate/missing ID, absent provenance field, unresolved estimability state, or inconsistent family scope. It must keep IDs, exact counts, raw support diagnostics and private hashes in protected files; public payload generation remains a separate disclosure-cleared step.

The adapter should preserve the distinction between `hypothesis_id` (pre-registered scientific coefficient) and `analysis_id` (versioned model result). It must not create public `n_model` values until aggregate disclosure review approves them. No association or result exists yet, so this review does not change the current formal model count.
