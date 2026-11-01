# CHARLS official sample-design and variance review

**Updated:** 2026-11-01  
**Purpose:** identify what the official CHARLS documentation specifies for the sample, target weights, PSU stages, and variance estimation before replacing the prior user-selected variance approximation.

**Implementation status:** county/community ID validation and the synthetic `survey` package mechanics check are complete. The synthetic check confirms that `ids=~county+community` without FPC gives the same covariance as `ids=~county`; this is software behavior only, not evidence about CHARLS effects.

## Official source findings

- The official 2011 National Baseline Users' Guide describes county-level systematic PPS selection after ordering/implicit stratification by region, urban district versus rural county, and GDP per capita; it then selects three village/neighborhood PSUs per county. For selected sub-neighborhood PSUs, the household selection probability is further adjusted by the sub-neighborhood's share. Thirty communities were split into sub-neighborhoods.
- The baseline guide explicitly derives household and individual weights from county, village, household, and within-household selection probabilities. It separately provides biomarker nonresponse-adjusted person weights for blood analyses. The searchable guide text does not prescribe a named Taylor, jackknife, BRR, or replicate-weight variance command.
- The 2020 User Guide describes the baseline design as an implicitly stratified multistage PPS design. It says the follow-up cross-sectional person weights account for sampling and nonresponse, and explains the cross-sectional sample flag/weight scope. This is a point-weight and target-population specification; it does not itself provide a released variance-stratum and split-PSU crosswalk.
- Metadata-only inspection of the official Wave 1 and Wave 2 PSU tables found parent-community rows keyed by communityID and geography/area labels. They do not expose an explicit variance-stratum field, respondent-level assignment for the 30 split sub-neighborhood PSUs, or replicate weights. The 2018 and 2020 guides state that PSU information is the same as in earlier waves, making the Wave 1/2 PSU release the official PSU source for later waves too.

## What this means for the current analyses

The previous five-wave results were fitted using the user's earlier selected communityID with-replacement Taylor setup. They remain private historical comparison outputs. They are not presented in this project as results computed using a complete reconstruction of CHARLS's multistage sampling variance.

For the next formal run, use official wave-specific target flags and weights, and source variance stages from CHARLS documentation. The 2011 guide states that householdID's first six digits identify province/city/county and its first seven identify the community. This makes the county component a documented candidate for a county-stage identifier, not an invented stratum; it must be validated against the person files, follow-up IDs and boundary changes before use. Do not treat `urban_nbs`, `areatype`, province/city context labels, or ID syntax alone as official strata. Do not import NHANES cycle-pooling or NHANES design variables into CHARLS.

## Metadata-only inventory completed on 2026-11-01

The existing authorized server intake was checked across the official design-related files for Waves 1–5. The inspection read Stata metadata (variable names, labels, dimensions) and archive member names only; it did not inspect respondent-level values. Temporary extracted design files were removed after inspection.

| Wave | Official design-related release files inspected | Findings relevant to the design |
|---|---|---|
| 2011 | `PSU.dta`, `weight.dta`, `Blood_20140429.dta` | PSU table contains `communityID` and geography/area/release labels, without explicit stratum, split-subcommunity respondent key, or replicate weights. Weight files distinguish household/person nonresponse weights and biomarker nonresponse weights; blood file carries `bloodweight`. The official guide documents the first six digits of householdID as province/city/county and first seven as community. |
| 2013 | `PSU.dta`, `Weights.dta` | PSU metadata has the same parent-community and area/geography fields. Weights distinguish cross-section and longitudinal samples and include a cross-sectional biomarker weight; release note specifies separate target samples and biomarker nonresponse adjustment. |
| 2015 | `Sample_Infor.dta`, `Weights.dta` | Sample-info file identifies cross-section membership and community. Weights provide household/person response-adjusted variants and a biomarker weight. No explicit strata, county-stage design field, split-PSU crosswalk, or replicate-weight field appears in these inspected files. |
| 2018 | `Sample_Infor.dta`, `Weights.dta` | Sample-info identifies cross-section membership and community; weights provide household/person base and household-response-adjusted variants. The inspected weight file has no separate biomarker-weight field. |
| 2020 | `Sample_Infor.dta`, `Weights.dta` | Sample-info identifies cross-section membership and community; weights provide household/person base and household-response-adjusted variants. The inspected weight file has no separate biomarker-weight field. |

The 2011 guide explicitly documents the ID segments: first six digits identify province, city and county; the first seven identify the community. It says these codes are constructed within CHARLS and can distinguish county units for county fixed/random-effect models. We will test that mapping against the protected analytic IDs and cross-wave linkage before using it as a county-stage identifier. It will not be used as an implicit stratum or relabeled as one.

This inventory narrows the next step: the primary design must follow each registered analysis' actual target (cross-section versus panel; blood-specific versus person weight) and official sample flag. A private identifier-only validation found that householdID's first seven digits exactly match communityID in all five prepared waves, each community maps to one county code, and shared cross-wave communities retain the same county code. Thus the official county component is source-supported as a county-stage cluster, not an invented stratum; exact diagnostics remain in protected QA. The inspected releases still lack a variance-stratum field, county PPS inclusion probabilities/FPC, or a separate split-subneighborhood respondent key. The leading specification is therefore the documented two-stage hierarchy (county, then community) with official wave weights and a with-replacement Taylor variance at the top county stage. R's `survey` documentation states that without an FPC multistage declarations use only the first-stage cluster for variance. This is an ultimate-county approximation; the previous community-only Taylor estimator will be retained as a sensitivity. Neither method will be described as an exact reconstruction of CHARLS's full implicit-stratified PPS variance.

## Work queue

1. The householdID county/community segments have been validated against the protected person tables for all five waves. Continue searching official codebooks for a split-subcommunity assignment, released stratum, and PPS/FPC field.
2. Check the NHANES paper and `chiragjp/nhanespewas` implementation for reproducibility, registry, and family-adjustment patterns only; use CHARLS official documents for all CHARLS design decisions.
3. Freeze the documented county/community hierarchy and wave-specific target flags/weights in a hash-bound plan. Validate the county-stage Taylor implementation on synthetic data, then rerun all registered wave families. Keep community-only clustering as a prespecified sensitivity.
4. If the official releases omit a variance input needed for the full design, document the closest estimator directly supported by the official sampling description, compare reasonable sensitivity estimators, and report the resulting inference scope plainly. Never call an approximation an exact official design variance.
5. Reassess the existing Pages families only after the new design review; publish replacements only after full-family QA and disclosure review.

## References

- CHARLS, [2011 National Baseline Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/CHARLS_nationalbaseline_users_guide.pdf), sampling and sample-weight sections.
- CHARLS, [2011 National Baseline Users' Guide, household and individual ID structure](https://charls.pku.edu.cn/en/data/User2011.pdf), county/community positions in IDs.
- CHARLS, [2020 Wave 5 User Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_User_Guide_English.pdf), baseline sampling and cross-sectional sampling weights.
- CHARLS, [2013 Wave 2 Release Note](https://charls.pku.edu.cn/en/data/Release2013.pdf), distinction between cross-sectional/longitudinal weights and cross-sectional biomarker nonresponse weight.
- CHARLS, [2018 Wave 4 User Guide](https://charls.pku.edu.cn/en/data/User2018.pdf), baseline sampling and Wave 4 sample/weight context.
- CHARLS, [2015 Wave 3 official data documentation](https://charls.pku.edu.cn/sj/a2015nqgzzdc.htm), released sample information, weights, blood documentation and codebook.
- CHARLS, [official sample-design page](https://charls.pku.edu.cn/en/About/Sample.htm).
- Thomas Lumley, [`survey::svydesign` documentation](https://r-survey.r-forge.r-project.org/pkgdown/docs/reference/svydesign.html), multistage IDs and FPC behavior.
- Patel et al., [NHANES exposome-phenome atlas article](https://www.nature.com/articles/s41591-026-04266-0); code reference [chiragjp/nhanespewas](https://github.com/chiragjp/nhanespewas), particularly [`pe_catalog.Rmd`](https://github.com/chiragjp/nhanespewas/blob/main/pe_catalog.Rmd). These are workflow references only.
