# Wave 1 pilot sensitivity analysis (methods only)

**Status:** exploratory, PI-delegated, not independently reviewed, and not approved for publication. All coefficients, confidence intervals, p/q values, exact counts, and result-derived comparisons remain in the protected server workspace.

## Prespecified variants

| Variant | Change from the draft reference model | Purpose |
|---|---|---|
| `main` | Blood examination weight; `communityID` PSU; no strata; WR Taylor; age, age-squared, sex, urban/rural, and education; fasting restriction for glucose and triglycerides | Draft reference specification |
| `county_psu` | Use the six-digit county prefix of `communityID` as PSU | Sensitivity to broader clustering |
| `no_urban` | Remove urban/rural adjustment | Probe exposure/urbanicity dependence |
| `age_sex` | Retain age, age-squared, and sex only | Probe adjustment-set dependence |
| `drop_small` | Exclude the marsh-gas and other-fuel contrasts | Probe sparse exposure categories |
| `fasting_adjust` | Use the full sample with fasting status as a covariate for glucose and triglycerides | Probe fasting-handling choice |

The driver is `scripts/run_wave1_pilot105_exploratory.py`; comparison logic is in `scripts/compare_wave1_pilot105_variants.py`. Outputs remain under `private/results/` and `private/qa_outputs/`.

## Interpretation boundary

These variants are robustness diagnostics for an exploratory run. They do not select a preferred model, validate causal assumptions, or replace the official survey design. Statistical significance in any variant is not a criterion for retaining a pairing or scaling up. The output files predate a frozen configuration and lack a contemporaneous signed manifest binding input, code, and configuration hashes. Independent methods review, reproducibility QA, and disclosure review are still required before any result can be released.