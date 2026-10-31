# Wave 1 pilot execution note (methods only)

**Status:** exploratory, PI-delegated, not independently reviewed, and not approved for publication. Coefficients, uncertainty estimates, p/q values, exact analytic counts, and result-derived diagnostics remain in the protected server workspace.

## Analysis specification used for the exploratory run

The pilot driver is `scripts/run_wave1_pilot105_exploratory.py`. It operationalizes the registered running-water contrast and cooking-fuel contrasts against the blood phenotype catalog, using the project’s Wave 1 analytic table and the predeclared fasting handling. The run used the user-selected approximate design: blood examination weight, `communityID` PSU, no fabricated strata, and with-replacement Taylor variance. It is not the gated scale-up executor.

The delegated draft choices were: age-domain lower bound 45 using the lower endpoint of the age interval; the draft M1 covariate set; fasting-only handling for glucose and triglycerides; and outcome standardization using the weighted within-domain standard deviation. These are exploratory choices and remain subject to independent methods review.

## Source-field correction

An early driver revision treated `i020` as cooking fuel. Official labels identify `i020` as heating availability, `i021` as heating energy source, and `i022` as the main cooking-fuel field. The driver was corrected to use `i022`; the registration itself already named `i022`.

## Reproducibility and interpretation limits

The result files are protected under `private/results/`. The run predates a frozen analysis configuration and does not have a contemporaneous, signed run manifest binding the exact input, configuration, and code hashes. A current-file hash inventory can document what exists now, but cannot reconstruct those historical bindings. The exploratory outputs must not be described as confirmatory findings or used for public reporting.

The analysis uses complete cases, approximate variance without official strata or replicate weights, and interval-derived age. It does not include multiple imputation or exposure measurement-error correction. The association results require independent methods review, output QA, and disclosure review before any release decision.