# Wave 1 pilot and scale-up hypothesis-family structure

**Date:** 2026-10-30  
**Scope:** Static review of the tracked hypothesis register only. No CHARLS participant records or private QA were accessed.

## Registry structure

The current register contains 240 planned coefficients with 240 unique `hypothesis_id` values:

- `wave1_household_environment_K150`: 150 coefficients, comprising 10 exposure contrasts across 15 blood phenotypes.
- `wave1_heating_route_K90`: 90 coefficients, comprising six `i021` fuel-versus-electricity contrasts within the questionnaire's `i020=No` route, across the same 15 phenotypes.
- The 105-coefficient Wave 1 pilot (one `i017` Yes-versus-No contrast plus six `i022` fuel-versus-electricity contrasts, each across 15 phenotypes) is exactly a subset of the K150 block. It is not an additional 105 unique hypotheses.

## Execution and multiplicity implication

The pilot is a prespecified first execution tranche, not a separate discovery family to be counted again in the final atlas. If the pilot passes its design and methods gates, retain its validated coefficient rows and run only the remaining K150 rows plus K90. Freeze the full 240-coefficient family before looking at association results, preserve non-estimable registered rows with an explicit reason, and perform the final multiplicity adjustment once across that family. A diagnostic pilot adjustment, if retained for internal review, must be labeled provisional and must not be combined with or presented alongside the final atlas adjustment as a second discovery claim.

All 240 rows remain `planned_not_approved`; static uniqueness and arithmetic do not establish source-value validity, estimability, target eligibility, or authorization to fit. The server's protected pair-level QA and independent methods review remain required.
