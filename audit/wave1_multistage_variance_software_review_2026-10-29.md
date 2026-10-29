# Wave 1 multistage variance: software capability and design-data limits

**Review date:** 2026-10-29  
**Status:** candidate specification only; no variance estimator or real-data model is approved.

## Recoverable sampling-unit keys

The CHARLS 2011 National Baseline Users' Guide states that the first six digits of the 9-digit household ID identify province/city/county and distinguish county-level codes; digit seven identifies the within-county village/community; the person ID adds two digits. The source-bound protected audit in [`audit_wave1_county_prefix_design.py`](../scripts/audit_wave1_county_prefix_design.py) verifies these prefixes against person, household, and official PSU keys locally and on the private server. It emits aggregate QA only.

There is a design-identity discrepancy that prevents calling the prefix a verified first-stage PSU: the audit finds 150 prefix groups with three sampled communities per group, matching the nominal design described in the Users' Guide, while CHARLS's current [official Sample page](https://charls.pku.edu.cn/en/About/Sample.htm) says that administrative boundary changes caused the final geography to cover 156 county-level units. The page explains that six sampled communities fell within additional counties and were not replaced. The ID encoding rule supports a county-geography code, and the observed topology is consistent with the original 150 selected sampling groups, but available documents do not explicitly state whether the prefix denotes the original selected county unit or the final county containing the household. Therefore the prefix is a **county-code grouping candidate**, not yet a confirmed county first-stage design identifier or an administrative county-name crosswalk.

The official design description is four-stage: county-level units, three communities within each selected county, households, and respondents. The county frame was ordered by region, urban/rural county type, and per-capita GDP before systematic PPS selection. The released variables do not provide an explicit variance-stratum identifier, the original county selection order/frame size, or respondent membership in the sub-communities used when large communities were split.

## Software review

The private server has R 4.5.3 and the CRAN `survey` package 4.5 installed. Its official [`svydesign` documentation](https://r-survey.r-forge.r-project.org/survey/html/svydesign.html) allows IDs at each sampling stage, stage-specific strata, weights, and finite-population corrections (FPCs). The same documentation states that when FPC is omitted, sampling is treated as with replacement at the top level and **only the first sampling stage is used for variance computation**; if FPC is supplied for fewer stages than the ID formula, later stages are treated as completely sampled.

Therefore, specifying `ids = ~county_prefix + communityID` with only the released final respondent weight does not by itself produce a complete two-stage variance. A county-only ultimate-cluster Taylor approximation would omit a separately estimated within-county community-sampling component. A community-only PSU analysis would instead ignore the sampled-county stage. Neither is a recovered official design. A multistage FPC/without-replacement treatment needs documented stage-specific inclusion probabilities or population counts and appropriate PPS support; these are not present in the currently verified files. The split-community respondent crosswalk is also unavailable.

## Candidate paths and restrictions

1. **Preferred exact path:** obtain a traceable official variance specification or additional release fields that identify county strata/order, stage-specific selection information, and split-community respondent assignments; then map the full design into an estimator that supports that design.
2. **Conditional approximate path for independent review:** only if a reviewer first confirms that the prefix groups correspond to the 150 selected first-stage sampling units, evaluate using that verified key as a top-level ultimate cluster with the relevant official outcome-specific weight, no invented strata or FPC, and explicitly state that lower-stage variance and implicit systematic PPS are not reconstructed. Until the sample-unit identity is confirmed, do not use it as the county PSU. Any resulting analysis would remain approximate and not automatically suitable for population inference or public Atlas release.
3. **Not allowed as a repair:** treating geography labels as actual design strata, inventing sub-community assignments, setting arbitrary FPCs, or representing a single-stage community cluster as the exact CHARLS design.

## Existing pilot output status

An earlier protected local run contains exploratory water-access-proxy × blood-analyte estimates using `communityID` as an unstratified with-replacement Taylor PSU and a provisional Harmonized CHARLS D age covariate. Its manifest explicitly says it is not release-ready and that source, target-population, age, weight, and survey-design gates remain open. The aggregate technical-integrity audit passed for both private result tables, including declared multiplicity adjustments; this validates output structure and arithmetic only. It does not validate the estimand, model specification, survey variance, or scientific results. These historical tables stay under the protected local root and are not formal approved models or public Atlas data.

## Gate decision

- County/community prefix-structure audit: passed locally and on the private server; the prefix's identity as the original 150 selected first-stage county units is unconfirmed because official materials distinguish 150 selected units from 156 final geographic counties.
- Wave 1 age method: not approved; the official Mata matrix has been retrieved, but exact comparison still requires a licensed Stata/Mata runtime.
- Full official sample design/variance: not approved; strata/order, stage-specific selection information, and split-community respondent linkage remain unresolved.
- Historical exploratory tables: technical integrity passed; scientific/design validity not assessed and not approved.
- Formal association models and public result payload: remain zero/absent.

## References

- [CHARLS 2011 National Baseline Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/CHARLS_nationalbaseline_users_guide.pdf)
- [R `survey::svydesign` documentation](https://r-survey.r-forge.r-project.org/survey/html/svydesign.html)
- [R `survey` multistage variance documentation](https://r-survey.r-forge.r-project.org/pkgdown/docs/reference/svyrecvar.html)
