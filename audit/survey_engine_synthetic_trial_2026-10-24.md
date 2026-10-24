# Complex-survey engine probe using synthetic data only

Date: 2026-10-24  
Purpose: check a possible analysis-engine candidate and illustrate why a PSU-and-weight-only design is not interchangeable with the documented stratified CHARLS design. This is software preparation only; no CHARLS file, record, answer, weight, or statistic was read.

## Setup and reproduction

The isolated local environment under `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\survey_engine_trial` contains `svy` 0.35.0, Polars 2.0.0, NumPy 2.5.4, SciPy 1.18.1, and `svy-io` 0.7.1. The probe script is [`survey_engine_synthetic_trial.py`](survey_engine_synthetic_trial.py). Run it only with that environment, or install the pinned package version in a disposable test environment:

```powershell
& "$env:LOCALAPPDATA\CHARLS_ExWAS_Atlas\survey_engine_trial\Scripts\python.exe" audit/survey_engine_synthetic_trial.py
```

It creates 4 strata, 2 PSUs per stratum, and 12 synthetic observations per PSU. The same outcomes, weights, PSUs, and with-replacement setting are passed to two design specifications: one with the synthetic stratum field, and one with the stratum omitted. A weighted mean and Gaussian survey GLM are fitted only to this generated data.

## Result

| Synthetic design declaration | Weighted mean | Engine mean SE | Manual mean SE | Mean df | Exposure beta | Engine exposure SE | Manual exposure SE | GLM df |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Known four strata + PSU + weight | 4.896739 | 0.250000 | 0.250000 | 4 | 1.349993 | 0.038839 | 0.038839 | 3 |
| Stratum omitted; one unstratified PSU design + same weight | 4.896739 | 0.866025 | 0.866025 | 7 | 1.349993 | 0.117514 | 0.117514 | 6 |

For the mean, the engine's SE exactly matches an independently calculated one-stage with-replacement PSU Taylor variance in the script. Let `u_hi = sum_j w_hij (y_hij - ybar_w)` be the linearized total for PSU i in stratum h. The hand calculation is `Var(ybar_w) = sum_h [m_h/(m_h-1) * sum_i (u_hi - mean_h(u))^2] / (sum w)^2`; omitting strata treats all PSUs as one group in this formula.

For this Gaussian identity-link model, the weighted least-squares coefficient and its PSU-score Taylor sandwich SE are independently calculated in the script and match the engine to floating-point precision. The manual covariance is `B^-1 [sum_h m_h/(m_h-1) * sum_i (s_hi - mean_h(s)) (s_hi - mean_h(s))'] B^-1`, where `B = X'WX` and `s_hi = X_hi' W_hi e_hi`. The script also recomputes the two-sided Student-t p-value from the engine-reported coefficient df and confirms the numerical value.

## Synthetic binary-outcome logistic check

The same script builds a separate deterministic dataset with 6 strata, 3 PSUs per stratum and 12 records per PSU (`n=216`). Binary outcomes are drawn from a logistic probability that includes a fixed PSU effect; the fitted model includes the exposure only, so uncertainty must account for PSU-level dependence. A root solve of the weighted logistic score independently recovers the coefficient. The covariance is independently calculated from the inverse weighted information matrix and stratum-centered PSU score totals. The engine and manual values agree to numerical tolerance:

| Quantity | `svy` | Independent calculation |
|---|---:|---:|
| Exposure log-odds coefficient | 0.40678681 | 0.40678681 |
| PSU-sandwich standard error | 0.16179455 | 0.16179455 |
| Student-t p value, engine df=11 | 0.02876984 | 0.02876984 |

This verifies this pinned package's basic binary-logit coefficient, Taylor covariance, and p-value path for one synthetic non-separated model. It does not validate rare outcomes, separation handling, categorical coding, nonlinear terms, marginal effects, finite-sample degrees of freedom for CHARLS, or any CHARLS result. The package documentation itself warns that separated coefficients can have undefined uncertainty; production code must detect and retain nonconvergence/inestimable statuses rather than publish such values.

A second synthetic logistic model treats a three-level exposure as a factor and sets `low` as the explicit reference. Both dummy-variable contrasts match an independently solved weighted logistic score and stratified PSU-score sandwich:

| Contrast vs. low | `svy` estimate (SE) | Manual estimate (SE) | `svy` p | Manual t p | df |
|---|---:|---:|---:|---:|---:|
| medium | 0.54842864 (0.35146885) | 0.54842864 (0.35146885) | 0.14972877 | 0.14972877 | 10 |
| high | -0.25773359 (0.29124097) | -0.25773359 (0.29124097) | 0.39696328 | 0.39696328 | 10 |

This exercises an explicit categorical reference in a synthetic, adequately populated example; it does not establish a CHARLS wave's harmonized categories, eligible denominator, or minimum category support. The CHARLS codebook must define the category semantics and route before a real pair can be specified.

A third fixture sets a binary outcome equal to a binary exposure across all 216 synthetic records. The pinned engine emits the `GLM_SEPARATION` warning and returns finite iteration coefficients together with `NaN` standard errors, intervals, and p values. Those coefficient values are not finite estimates and must not be released. The project's result validator already permits `fit_status=inestimable` only with blank estimate fields and rejects estimate fields for every non-success status; production code should map this warning/non-finite uncertainty to `inestimable`, keep a sanitized diagnostic, and never mark it successful. This check covers complete separation in one synthetic fixture; it does not validate every quasi-separation, sparse-cell, or convergence case.

A fourth fixture changes only one outcome among the 216 records. The engine still emits `GLM_SEPARATION`: the exposure coefficient is a finite iteration value, but its standard error, confidence limits, and p value are `NaN`; the intercept uncertainty remains finite. This demonstrates that a finite coefficient alone is not evidence of an estimable contrast. Production status handling must be term-specific: suppress the affected exposure contrast as `inestimable`, while retaining any separately valid nuisance-term diagnostic only in protected logs. This one-case example does not establish a general numeric threshold for quasi-separation.

The point estimates match because the records and weights are unchanged. The standard errors and design degrees of freedom differ substantially in this constructed example. The example intentionally contains strong between-stratum differences; this is an illustration of sensitivity to the declared design, not a general theorem that omitting strata always increases uncertainty. The CRAN `survey` manual likewise treats stratification and cluster structure as explicit design inputs and documents the ultimate-cluster option for multistage variance estimation.

## Domain filtering and singleton PSUs

The same synthetic records include a domain present in only one of the two PSUs in each of four strata. Fitting with `where=` on the original 96-row design retains all PSUs, detects four domain-singleton strata, and returns the domain model. Its coefficient and PSU-score sandwich SE also match an independent weighted least-squares calculation that assigns zero domain weight to out-of-domain records while retaining both PSUs in every stratum. The fixture gives the out-of-domain rows null exposure/outcome values, and the model still runs without `drop_nulls=True`, matching the package's documented skip-pattern handling. Physically filtering to the 48 domain rows first removes the other PSU from every stratum; the default design then raises an unhandled-singleton error rather than estimating variance from the reduced design.

A second synthetic pairwise-complete case has one missing exposure/outcome record inside the target domain. `glm.fit(where=..., drop_nulls=True)` reports 47 complete observations while retaining all 96 design rows; its coefficient and SE match a hand calculation with the missing record's analysis weight set to zero and all PSUs retained. This demonstrates the package's implementation only, not that complete-case analysis is unbiased or appropriate for CHARLS. The pair-specific estimand, module eligibility, missing-data assumptions and domain still require prespecification and official-release review. For real survey inference, preserve the full eligible released design and encode a defined subpopulation/complete-case domain without deleting design rows before variance estimation.

## Interpretation for CHARLS

The installed `svy` API accepts stratum, PSU, weight, and with-replacement design components separately; the local probe confirms it will also calculate results when a stratum is omitted. That technical capability does not establish that omission is appropriate for CHARLS. Official CHARLS materials describe stratified multistage sampling and community PSUs. Until the exact released variance stratum, replicate-weight files, or an official variance recommendation is verified for the relevant wave and module, the unstratified output remains an explicitly approximate sensitivity candidate and is not a primary result. No unweighted/weighted regression on real CHARLS data is authorized by this probe.

The package's publisher reports comparisons against R's `survey` package for equivalent design declarations. This machine has no R installation, so the current probe does not independently reproduce that cross-software comparison. The hand calculations independently check this specific mean and Gaussian-model covariance formula; they do not replace broader cross-software and family-specific validation before any future real model run.

## Sources

- `svy` design declaration and API: [official Getting Started documentation](https://svylab.com/docs/svy/getting_started.html).
- `svy` model variance behavior: [official GLM tutorial](https://svylab.com/docs/svy/tutorials/glm.html) states that Taylor linearization is the default and replicate weights require an explicit method selection.
- `svy` domain and singleton behavior: [official singleton tutorial](https://svylab.com/docs/svy/tutorials/singletons.html) documents domain singletons and the default standard-domain variance rule; the [official GLM tutorial](https://svylab.com/docs/svy/tutorials/glm.html) says `where=` retains the full design while pre-filtering does not.
- `svy` missing-value behavior: [official release notes](https://svylab.com/docs/svy/changelog.html) describe null values outside `where=` as out-of-domain and `drop_nulls=True` as zeroing analysis weights instead of physically dropping rows; exact behavior must be checked against the pinned package version before production use.
- Package comparison claim (publisher-authored, not independently replicated here): [svy versus R `survey`](https://svylab.com/learn/notes/posts/svy-vs-r-comparison).
- Reference implementation scope: [CRAN `survey` manual](https://cran.r-project.org/web/packages/survey/refman/survey.html) describes Taylor and replicate-weight variance estimation for multistage, stratified, cluster-sampled, unequally weighted designs and identifies `one.stage=TRUE` as an ultimate-cluster variance estimator.
- CHARLS sampling and PSU constraints remain in [`survey_design_weight_review_v1.md`](survey_design_weight_review_v1.md) and [`CHARLS_ExWAS分析规约_v0.1.md`](CHARLS_ExWAS%E5%88%86%E6%9E%90%E8%A7%84%E7%BA%A6_v0.1.md).
