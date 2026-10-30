# Wave 1 Option A variance implementation review

**Date:** 2026-10-30  
**Status:** internal static implementation review; not independent methods approval and not authorization to fit associations.

## Scope

Reviewed the current protected Wave 1 design-support aggregate, the hash-bound draft model configuration, the scale-up runner, and the pinned server environment. No biomarker values or fitted associations were inspected in this review. Exact community/weight support metrics remain in the server-private QA tree.

## What the current implementation says

- The selected candidate design is `bloodweight`, `communityID`, with-replacement Taylor linearization and an explicitly empty stratum list. The runner rejects unsupported design choices and passes these fields to the pinned `svy` implementation.
- The configured singleton behavior is `center`; domain-singleton handling is `standard`, with warnings requested. The `svy` documentation defines `standard` domain variance as retaining out-of-domain PSUs as zero totals. This is different from treating each age-domain sample as a newly selected survey. The configuration must retain the full blood-response design frame and use the age/complete-case subset as the analysis domain.
- The protected design-support summary shows that the candidate community clustering has broad support, with a small number of one-observation communities. These are support diagnostics, not final model N and not, on their own, singleton-stratum diagnoses. With no released strata in this approximation, a one-record community does not mean a one-PSU stratum.
- A county-prefix grouping has been inspected only as a sensitivity candidate. Its identifier structure is consistent with a nominal county count, but the source does not confirm that it reconstructs the original first-stage PSU, implicit strata, PPS size measures, or the final split-community map. It must not be promoted to the main design or presented as a recovered official design.

## Interpretation and required caveat

Option A is executable as a **user-selected approximate variance analysis**, but the data do not identify the full original sampling design from the released design fields. Community clustering may not match CHARLS's first-stage sampling unit. Therefore, report estimates and standard errors as approximate, state that the full multistage PPS/implicit-strata design was not reproduced, and avoid describing confidence intervals or p-values as official CHARLS design-based inference. County-prefix clustering may be shown only as a predeclared sensitivity if the methods reviewer approves it; it is not a substitute for documented design metadata.

The code's singleton/df safeguards must remain explicit at freeze: use the pinned engine's declared singleton and domain behavior, preserve the theoretical design degrees of freedom before any engine floor, and mark a model non-estimable if variance/inference diagnostics fail. A returned coefficient alone is insufficient evidence of valid inference.

## External technical documentation checked

- `svy` singleton documentation: <https://svylab.com/docs/svy/tutorials/singletons.html> — describes centered singleton handling and the distinction between standard and apply domain-singleton handling.
- `svy` package/source: <https://github.com/samplics-org/svy>.
- The server environment reports `svy==0.35.0`, matching the runner's pinned version.

These software references describe implementation behavior; they do not validate the approximation for CHARLS. Independent methods review is still required, and no model was run.

## Decision record

1. Keep the user-selected community-PSU/no-strata WR Taylor candidate unchanged for the proposed primary approximation.
2. Preserve county-prefix results as sensitivity-only and explicitly unvalidated.
3. Keep the age-domain/complete-case estimand and singleton/df behavior in the freeze packet for reviewer decision.
4. Leave the association readiness gate closed until outcome rules, the full configuration, and an independent hash-bound methods review pass.
