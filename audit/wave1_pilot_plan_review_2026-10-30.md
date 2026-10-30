# Wave 1 pilot plan review (2026-10-30)

## Decision and conclusion

The user selected variance option A as the project's primary **approximate** method: community/PSU-clustered Taylor linearization without released strata, with results labeled approximate, and requested all individual-level analysis to run in the private server workspace. Record this as a project decision, but do not describe it as reconstruction of the full CHARLS design or as automatically validated by the choice itself.

The P0–P7 outline is a useful sequence, but it is not ready to execute unchanged. The first-wave source package, protected rebuild, and Blood-to-weight linkage work are already substantially complete; they should not be scheduled from zero again. Several estimand and readiness decisions remain open. No new real-data association was fit during this review; the count of formally admitted models remains zero.

## What is supported by official documentation

- The 2011 Blood Sample Users' Guide defines the blood target as all 17,708 baseline main respondents and spouses, reports 11,847 collected blood samples, and says `bloodweight` adjusts the household and individual nonresponse and blood-sample nonparticipation. These are distinct target and observed-sample counts; they should be reconciled separately, not treated as counts that must be equal.
- The baseline sampling guide describes a stratified multistage PPS design. County-level units were stratified by region, urban/rural status and GDP per capita; three village/neighborhood PSUs were selected within each county-level unit. Therefore option A omits known design information and is an approximation. Its standard errors may be either too large or too small; do not call it conservative. The survey-design software documentation likewise treats PSU, strata, weights and FPC as distinct design inputs.
- The blood guide says interviewers requested overnight fasting but still collected nonfasting samples and recorded fasting status. It does not give a numeric mapping for Wave 1 `qc1_va003` in the reviewed official materials; the released field has no attached value-label set in the metadata review.

## Required corrections before the first real-data run

1. **Freeze the estimand.** The user's proposed 45+ primary domain with all blood-target records retained in the design is a defensible candidate for a 45+ target, with the full blood target as a sensitivity estimand. It differs from the current project memo's prior recommendation to make the full blood target primary. Record this as an explicit change only after the age-domain rule is specified. Do not remove younger spouses before defining the survey design. The current official-age interval method still needs an agreed rule for respondents whose plausible age interval crosses 45.
2. **Keep weights pair-specific.** `bloodweight` is the supported candidate for blood outcomes in the blood target. Questionnaire outcomes require the individual questionnaire weight for the corresponding target. For every pair, also verify that exposure-module nonresponse and household/person linkage do not change the target or require a different complete-case interpretation. Do not apply one weight to the whole atlas by default.
3. **Do not infer fasting codes from frequencies.** A value distribution cannot establish which numeric code means fasting. Use an official value label/codebook correction or other primary CHARLS documentation. Until then, leave fasting-dependent outcomes (at least glucose and triglycerides) unestimable in the pilot; preserve their prespecified hypotheses in the registry with a blocked status. Non-fasting-dependent biomarkers can be considered separately once their own outcome and design gates pass. Do not use the Wave 3 code as proof of the Wave 1 code.
4. **Make the variance sensitivity real.** Primary A must specify the exact PSU key, with-replacement assumption, Taylor implementation, domain handling, lonely-PSU behavior, and limitations. A 150-county sensitivity is possible only if every community-to-county mapping used is validated; do not fabricate pseudo-strata from a count or an unverified ID prefix. Neither run reproduces the complete stratified multistage design. The project's planned approximate-inference label must travel with internal result tables and any eventual public aggregate.
5. **Repair the hypothesis registry.** Audit found that 105 tagged rows are not necessarily 105 unique exposure–phenotype pairs because contrasts can create multiple rows, and the historical pilot files are not an exact match to the registered scope. Create stable unique pair IDs and contrast IDs; freeze which coefficients belong to the multiplicity family before looking at results. Generate a candidate variable inventory from the crosswalk, then manually gate eligibility, units, timing, route, and measurement level; a crosswalk row is not analysis readiness.
6. **Predeclare models and thresholds.** Define the estimand and DAG-based covariates before fitting. M0/M1/M2 need exact formulas and a reason for each adjustment; do not copy NHANES covariates mechanically or adjust for likely mediators. The proposed N>=500 and PSU>=30 rules are heuristics, not official standards. Either justify/freeze them using design degrees of freedom and precision diagnostics, or report all prespecified pairs and mark unstable/non-estimable results without outcome-driven exclusion. Choose one primary multiplicity procedure in advance; do not choose BY versus Bonferroni after seeing results.
7. **Keep the release gate.** P4 should review design/estimand validity, reproducibility and diagnostics, not significance. `--publish` must remain blocked until aggregate disclosure review is complete. Wave 2–5 each need their own source, frame, weight and variance assessment; do not carry Wave 1 settings forward automatically.
8. **Remove the email Plan B from the autonomous plan.** No message to CHARLS or another third party will be sent absent a later explicit user instruction. A draft may remain a private reference, but it is not a scheduled project dependency.

## Current execution-readiness finding

Before execution, use a clean, up-to-date checkout of the reviewed project code and verify that the runner consumes the protected private root and that result directories are access-restricted. The public site publishes no formal associations.

## Sources

- CHARLS, [2011–2012 National Baseline Users' Guide](https://charls.pku.edu.cn/en/data/User2011.pdf).
- CHARLS, [2011 Blood Sample Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf).
- CHARLS, [2011 Wave 1 official documentation index](https://charls.pku.edu.cn/en/Doc/a2011_CHARLS_Wave1__Baseline_.htm).
- Thomas Lumley, [Specifying a survey design in R's survey package](https://faculty.washington.edu/tlumley/old-survey/example-design.html).
