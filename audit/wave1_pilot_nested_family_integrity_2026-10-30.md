# Wave 1 pilot nesting and family integrity

**Date:** 2026-10-30
**Scope:** Tracked hypothesis registry only; no CHARLS participant data or private QA were read.

## Result

The metadata-only audit found 240 planned hypothesis rows: 150 in K150 and 90 in K90. Exactly 105 rows are marked as pilot overlap, comprising the seven predeclared `i017`/`i022` contrasts crossed with the same 15 phenotype concepts. All 105 are nested in K150. The remaining 135 planned rows are outside the pilot; all K90 rows remain outside it. This confirms the pilot is an execution tranche, not an extra multiplicity family.

The audit now enforces these counts, contrast membership, family placement, and explicit yes/no overlap labels so accidental double-counting or K90 overlap fails the structural check.

## Interpretation boundary

The check establishes only registry arithmetic and labels. It does not verify source coding, sample eligibility, measurements, model estimands, survey-design validity, or association estimates. Every planned hypothesis remains unapproved. The independent methods review and all other readiness gates remain closed; no real-data associations were fitted.

Implementation: [`scripts/audit_wave1_scaleup_hypothesis_registry.py`](../scripts/audit_wave1_scaleup_hypothesis_registry.py).
