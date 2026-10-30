# Wave 1 household-environment pilot execution design

**Status:** implementation specification only; the real-data gate remains closed.

## Batch scope

The `pilot105` batch is exactly the 105 registered coefficients nested inside K150: one running-water contrast and six cooking-fuel-versus-electricity contrasts, each crossed with the 15 predeclared blood phenotypes. It is not a new inferential family and adds no hypotheses to K=240.

The official Wave 1 numeric mapping for fasting field `qc1_va003` remains unresolved. The 7 glucose coefficients stay in the output registry as `blocked_by_unresolved_measurement_rule`, with no coefficient estimate or p/q value, because CHARLS warns that non-fasting glucose may be higher. The 7 triglyceride coefficients remain candidate outcomes for all observed blood samples: an EAS/EFLM consensus supports routine non-fasting lipid profiles, while a fasting-status sensitivity remains pending an authoritative Wave 1 code map. The remaining 91 coefficients are candidates only after independent review of the outcome rules, age/target estimand, covariates, and Option A approximation. Thus 98 of 105 are candidates for fitting after approval, not a claim of actual estimability.

## Review and execution boundaries

- Pilot approval uses its own analysis-plan ID, readiness record, configuration file, source-manifest ID, prepared-table hash, plan fingerprint, and configuration SHA-256. It cannot reuse or imply the later K150/K90 scale-up approval.
- The runner requires `--run --batch pilot105`, then validates the pilot-specific fail-closed readiness record before reading the prepared participant table. Full expansion uses `--run --batch full240` and the separate scale-up approval.
- Pilot output is written only under `private/pilot105_2011_household_environment/`. Its 105 rows retain the parent K150 family identifier/size, and the batch reports no tranche q-values. Final BY-FDR/Bonferroni correction remains across the complete frozen K=240 family.
- No p-value threshold selects pairs or determines whether to scale up. QA, design diagnostics, model validity, sensitivity and reproducibility determine whether the methods reviewer can support expansion.
- Templates in `audit/templates/` are not approvals. A reviewer must sign the exact configuration hash; public release remains separately disabled.

## Static implementation safeguards

Configuration validation permits an explicit blocked fasting rule only when it includes a reason and no guessed fasting field/codes. Glucose must either be restricted using verified codes or remain explicitly blocked; `retain_all` and `not_applicable` are rejected for glucose. Triglycerides may use all observed samples under the non-fasting lipid-profile candidate rule; fasting restriction/sensitivity requires an authoritative Wave 1 code map and separate review. When an outcome is blocked, the runner returns a reason-coded row without computing an outcome scale or fitting a model.

This document and the runner are part of the pilot plan fingerprint. Any future edit changes the fingerprint and invalidates a prior approval until re-reviewed.

## Operator command

After an independent reviewer has frozen the matching private configuration and approved every readiness gate, run from the reviewed server checkout:

```bash
source ../env/charls_env.sh
../env/venv/bin/python scripts/run_2011_household_environment_scaleup.py --run --batch pilot105
```

The full K=240 batch requires its own frozen configuration and readiness review:

```bash
../env/venv/bin/python scripts/run_2011_household_environment_scaleup.py --run --batch full240
```

The public templates are intentionally incomplete. Do not copy them into the private approval paths and treat them as approved; the reviewer must resolve the open estimand, age-domain, covariate, outcome and variance decisions and bind the exact hashes first.
