# Wave 1 model-entry provenance gate (2026-10-27)

## Finding

The protected local workspace still contains legacy prepared wave tables. Its 2011 entry in `prepared_data_manifest.json` has only row/column metadata and no source-review object or prepared-output hash. Before this change, both exploratory association scripts required `--run` but did not check source provenance, so an old derived frame could still enter a fresh model run.

## Change

Added a metadata-only analysis gate shared by the water/blood pilot and household-environment extension. Before either script reads respondent values, it now requires:

- a prepared Wave 1 manifest carrying a verified source-review status;
- the same source-manifest ID in the current intake manifest;
- all four currently staged official release files, with exact names and SHA-256 values matching the prepared record and human-reviewed intake manifest;
- the official source identifiers/pages and reviewed source identity to pass the existing intake validator; and
- the prepared respondent table filename and SHA-256 to match its preparation manifest.

The validator reads JSON, Stata headers, ZIP inventories, and file bytes only. It does not read respondent-level values. It returns source provenance for the private run manifest but explicitly leaves survey-design review unresolved; source authentication is not an analysis approval.

## Separate analysis-readiness approval

Both model entry points now also require a reviewer-completed readiness file under the protected `analysis_review` directory. The water/blood pilot record must bind to the current source-manifest ID and prepared-table SHA-256, identify the frozen pilot plan, and show evidence for source identity, frame/denominators, age/target, weights/nonresponse, final PSU, variance method/limitations, and the frozen analysis plan. It must also include `analysis_plan_sha256`, calculated by the gate over the exact bytes of the tracked pilot, scale-up, success-criteria, and multiplicity protocol documents. A text change to any of those documents invalidates the existing review hash and requires review again; keeping the same plan ID is insufficient. The run manifest records the verified plan hash. Approval only means permission to run the internal exploratory pilot; it must keep `public_release_status` at `not_approved`.

The household-environment extension uses its own review file and additionally requires a documented pilot success/reproducibility review. It cannot be launched merely because the pilot's source/design checks passed; the prior pilot must first be reviewed as valid and reproducible. Empty templates are under `audit/templates/`; they are not approvals and should only be copied to protected storage after the evidence is assembled.

## Validation

Synthetic tests verify that a legacy Wave 1 manifest without provenance is rejected and that a workspace outside protected storage is rejected. Existing `--help` and default-invocation guard tests still pass. No participant values were read and no model was run in this validation.

## Current state and next action

The local Wave 1 prepared manifest is legacy and lacks provenance. The current intake directory has the manifest and README only; all four official release files are missing. Therefore both model scripts now fail closed before reading respondent rows. When authorized official files are staged, run the metadata-only preflight, review source identity, rebuild Wave 1 using the gated builder, then continue the denominator/eligibility/weight/PSU/variance gates before any pilot refit. Only after design review can the frozen pilot be used as the scale-up decision point.

## Privacy

Only the validator code, synthetic tests, and this method note are stored in Git. Microdata, hashes, sample counts, and model estimates remain under protected local storage.

## Synthetic code-path check added (2026-10-27)

A fully synthetic fixture exercises the positive provenance path: it creates a test ZIP, three synthetic Stata headers, a synthetic intake manifest, and a synthetic prepared-table hash. The validator accepts this only as provenance-structure validation and returns `survey_design_status=still_requires_independent_review`. Synthetic readiness tests check hash binding, unresolved variance review, and the extension-stage pilot review. None authenticates a real CHARLS source or contains CHARLS participant data.
