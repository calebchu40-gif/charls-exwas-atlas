# Wave 1 K150/K90 association run status — 2026-10-31

The user-authorized Wave 1 household-environment run completed on the user's private server.

- Primary scope: all 240 predeclared K150/K90 exposure–phenotype hypotheses; all 240 model fits completed successfully.
- Primary specification: bloodweight; communityID clusters; unstratified with-replacement Taylor linearization; age-domain rule and registered M1 covariates in the hash-bound server configuration.
- Sensitivity runs: county-prefix clustering, removal of the urban covariate, and age/sex-only adjustment, each covering all 240 registered hypotheses.
- Uric-acid follow-up: 16 registered Wave 1 exposure–uric-acid hypotheses refit with creatinine, self-reported kidney disease, and both together (48 additional fits).
- The private QA checks found one row per registered hypothesis in every full block, finite estimates and intervals, and no survey-engine warnings. A combined-240 Benjamini–Yekutieli diagnostic and sensitivity comparisons were written to private storage.
- Individual-level source data, result tables, exact support counts, estimates, p/q values, hashes, and run manifests remain in the server's protected `private/` tree. None is included in this repository or the Pages payload.
- The homepage reports the completed Wave 1 model-run count. The normalized, allowlisted K=240 aggregate payload is now built and included in the Pages source; live deployment is being verified.

The association models are non-causal, within-wave weighted comparisons under the selected approximate variance design. The private analysis records the limits of the released design information. This file records execution status only; it contains no association estimates or result-derived significance counts.
