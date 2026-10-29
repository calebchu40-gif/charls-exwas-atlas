# Historical Wave 1 candidate: county-prefix single-stage cluster
> **Status update (2026-10-30):** This is a historical provisional candidate, no longer the project's preferred variance approach and not approved for fitting. The official CHARLS Sample page explicitly describes village/neighborhood units as PSUs after county-level stratified systematic-PPS selection, and documents split sub-neighborhood PSUs. The public release lacks the complete design mapping. See [`charls_wave3_psu_variance_release_review_2026-10-30.md`](charls_wave3_psu_variance_release_review_2026-10-30.md); no single-stage candidate is currently preferred.

**Date:** 2026-10-30  
**Status:** candidate for independent methods review; not an approved variance specification.  
**Scope:** 2011 household environment × conventional blood-marker associations using the official blood-target population and `bloodweight` candidate.

## Why consider this candidate

The CHARLS baseline guide describes a multistage design: county-level units were ordered/implicitly stratified using region, urban/rural status and GDP, then communities were selected by systematic PPS; large communities could be split into subcommunity PSUs. The released respondent records carry `communityID`, while the official Community module's sparse `sub_commuID` does not identify every respondent's final split-community PSU. The public PSU file also does not expose a complete county stratum and final respondent-level sub-PSU crosswalk.

The official household-ID coding rule and protected key audit support a reproducible county-prefix candidate above `communityID`. This makes a first-stage cluster approximation feasible without guessing which subcommunity contains each respondent. It does not prove that the prefix is the complete design PSU variable or recover the actual implicit strata, PPS ordering, size measures, joint inclusion probabilities, or all boundary-change details.

## Candidate A — county-prefix ultimate-cluster approximation

For review, define the released biomarker-weighted association estimator on the full official baseline blood target. Use the county-prefix candidate as the sole variance cluster, with `bloodweight`; omit unsupported strata and FPC fields. This corresponds to a with-replacement top-level cluster approximation in standard survey software. Clustering at the county prefix also keeps sampled communities and any unresolved subcommunity splits together.

The interpretation must be explicit: weighted cross-sectional association for the stated blood target, with a county-cluster with-replacement variance approximation. It is **not** the exact CHARLS design variance. It does not account for the baseline's county-level implicit stratification or reconstruct systematic PPS without-replacement variance. The sign and size of the resulting variance error are not guaranteed; do not describe it as necessarily conservative.

This is a possible practical primary estimator only if an independent survey-methods reviewer accepts that approximation for the intended inference and the analysis reports the missing design information as a limitation. If national-design-valid standard errors are required, this candidate does not pass that requirement and the model gate stays closed pending additional official design information.

## Candidate B — community cluster within county, conditional second-stage variance

If respondents can be assigned to released community PSUs, a separate approximation could use `communityID` as PSU within county-prefix strata. It estimates variation among sampled communities conditional on the selected county units and omits uncertainty from selecting counties. It may better target within-selected-county variation but is not, by itself, design-based national inference. An analysis using this approach must say so in its estimand and output labels. It must not claim to solve final subcommunity membership; the split-community issue remains.

## Do not use these as shortcuts

- Do not treat region, NBS urban/rural category, GDP rank, province, or city as official design strata without source evidence that maps the original strata.
- Do not infer the final subcommunity assignment from sparse `sub_commuID` values or fabricate a crosswalk.
- Do not put `communityID` or county-prefix in the ordinary regression adjustment set to stand in for survey variance.
- Do not create replicate weights from the point weights alone and call them official replicates.
- Do not interpret a successful software run or synthetic calibration as approval of the estimator.

## Review and implementation gates

1. Reviewer verifies the official county-prefix coding and the selected county-level clustering interpretation against the exact released files and CHARLS guide.
2. Reviewer chooses whether the target is explicitly conditional on the selected counties, accepts Candidate A's with-replacement approximation with limitations, or requires additional design data. No option is preselected as approved here.
3. Confirm the blood-target weight and the exposure-module complete-case target remain compatible; record any response/coverage limitations.
4. Only after the variance choice, age/estimand, covariates, blood valid-value rules and fasting handling are frozen should a source/hash-bound readiness record be produced.
5. Run association models only if the readiness gate and independent review pass. Never use p-value yield as a reason to select Candidate A or B.

## Sources

- CHARLS [2011 National Baseline Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/CHARLS_nationalbaseline_users_guide.pdf): staged sampling, county ordering, systematic PPS community selection, subcommunity PSUs, and released ID coding.
- CHARLS [2011 Wave 1 data page](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html): released PSU and weight materials.
- Lumley's [`survey::svydesign` documentation](https://r-survey.r-forge.r-project.org/pkgdown/docs/reference/svydesign.html): when FPC is omitted, variance computation assumes top-level with-replacement sampling and uses only the first cluster stage.
- Internal source-bound key and table review: `scripts/audit_wave1_county_prefix_design.py`; aggregate-only QA remains in the owner-only protected local directory and is not reproduced here.

This note contains no participant values, fine geography, row counts from private data, estimates, or p-values. It does not open the model or public-results gate.
