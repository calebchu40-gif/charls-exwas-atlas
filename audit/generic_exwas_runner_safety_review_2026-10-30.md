# Generic ExWAS scan runner: safety and statistical review (2026-10-30)

## Review scope

Reviewed the generic scan engine draft that had been created in the protected server checkout, then compared it with the tracked project runner. No CHARLS values were read and no analysis was run. The tracked `run_exwas_scan.py` already has a Wave 1 fail-closed path: it rechecks current source identity and prepared-frame provenance, requires the registered Wave 1 readiness record with all plan gates and exact plan fingerprint, requires an exact registry/design-bound exploratory-scan authorization, and keeps the result inside protected storage. That guard is retained. The server's untracked draft had omitted this authorization path; it must not replace the tracked runner.

## Engine issues corrected

- The logistic branch had exponentiated the log-odds standard error. It now reports odds-ratio-scale standard error using the delta method, exponentiates the coefficient confidence limits, and suppresses partial estimates/p-values on overflow or underflow.
- Positive-weight rows with missing PSU or specified stratum now stop the scan rather than being grouped under a stringified missing key.
- Pair-specific domains with fewer than two PSUs are marked blocked before fitting.
- Model IDs must have explicit covariate-set declarations; empty or duplicate model lists, empty pair registries, invalid family prefixes, and reversed validity bounds are rejected.

## Current gate and limitations

No authorization record or independent design approval was added. The readiness template remains unapproved, current survey-design and age gates remain unresolved, and formal association models remain 0. The tracked CLI currently authorizes only Wave 1 after the existing source/readiness gates; later waves require their own wave-specific source, frame, weight and design authorization. The generic engine's covariate list treats covariates as numeric columns, so categorical adjustment needs explicit encoding before use. Its long output schema still needs a separately reviewed adapter to the site's release-reviewed result schema. No tests or real-data fits were run.

## Server draft handling

The server checkout contains unrelated uncommitted work. The unguarded server runner will be preserved as a restricted pre-review snapshot, and the tracked guarded runner will be synchronized into the expected server script path. Only the two reviewed runner/engine files and this public-safe note are in scope; unrelated server edits remain untouched.
