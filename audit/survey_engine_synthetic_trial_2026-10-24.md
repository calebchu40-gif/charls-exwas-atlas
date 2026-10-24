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

| Synthetic design declaration | Weighted mean | Mean SE | Mean df | Exposure beta | Exposure SE | GLM df |
|---|---:|---:|---:|---:|---:|---:|
| Known four strata + PSU + weight | 4.896739 | 0.250000 | 4 | 1.349993 | 0.038839 | 3 |
| Stratum omitted; one unstratified PSU design + same weight | 4.896739 | 0.866025 | 7 | 1.349993 | 0.117514 | 6 |

The point estimates match because the records and weights are unchanged. The standard errors and design degrees of freedom differ substantially in this constructed example. This is an illustration of sensitivity to the declared design, not a general theorem that omitting strata always increases uncertainty.

## Interpretation for CHARLS

The installed `svy` API accepts stratum, PSU, weight, and with-replacement design components separately; the local probe confirms it will also calculate results when a stratum is omitted. That technical capability does not establish that omission is appropriate for CHARLS. Official CHARLS materials describe stratified multistage sampling and community PSUs. Until the exact released variance stratum, replicate-weight files, or an official variance recommendation is verified for the relevant wave and module, the unstratified output remains an explicitly approximate sensitivity candidate and is not a primary result. No unweighted/weighted regression on real CHARLS data is authorized by this probe.

The package's publisher reports comparisons against R's `survey` package for equivalent design declarations. This machine has no R installation, so the current probe does not independently reproduce that cross-software comparison. The project should still validate any selected engine against an independent trusted implementation on synthetic designs before real model runs.

## Sources

- `svy` design declaration and API: [official Getting Started documentation](https://svylab.com/docs/svy/getting_started.html).
- `svy` model variance behavior: [official GLM tutorial](https://svylab.com/docs/svy/tutorials/glm.html) states that Taylor linearization is the default and replicate weights require an explicit method selection.
- Package comparison claim (publisher-authored, not independently replicated here): [svy versus R `survey`](https://svylab.com/learn/notes/posts/svy-vs-r-comparison).
- Reference implementation scope: [CRAN `survey` manual](https://cran.r-project.org/web/packages/survey/refman/survey.html) describes Taylor and replicate-weight variance estimation for multistage, stratified, cluster-sampled, unequally weighted designs.
- CHARLS sampling and PSU constraints remain in [`survey_design_weight_review_v1.md`](survey_design_weight_review_v1.md) and [`CHARLS_ExWAS分析规约_v0.1.md`](CHARLS_ExWAS%E5%88%86%E6%9E%90%E8%A7%84%E7%BA%A6_v0.1.md).
