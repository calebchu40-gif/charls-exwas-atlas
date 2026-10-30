# CHARLS 2015 sample-design and PSU/variance release review (2026-10-30)

## Scope

This review uses CHARLS public sample-design and 2015 release documents plus the published Codebook. It determines what design structure can be supported from the documentation; it does not inspect participant records, select a variance estimator, or authorize a model.

## What the official sample page documents

CHARLS describes the national baseline as a four-stage design. County-level units are sorted/stratified by region, urban/rural status, and GDP per capita and selected by systematic PPS. Within each county, three village/neighborhood units are selected by PPS. CHARLS explicitly calls these village/neighborhood units the primary sampling units (PSUs); they can include one or more former resident committees. For very large communities, 30 communities were subdivided and sub-neighborhoods were sampled. Six originally selected communities were replaced; in six counties, boundary changes meant selected communities fell within two counties, producing 156 final geographic counties. Households and respondents were sampled within these geographic units.

The 2015 Blood Release Note describes the national sample as 150 counties/districts and 450 villages/urban communities, and notes one PSU was collected in 2016. It does not give a respondent-level final-PSU map, a strata key, replicate weights, or an executable variance specification for the 2015 blood target.

## What the released 2015 files document

The current public 2015 data listing includes All Data, separate modules, Blood, Weights and Sample Information; it does not list a separate PSU/strata download. The 2015 Codebook has 18 module sections and no PSU section. Its Sample Information section documents `ID`, `householdID`, `communityID`, `crosssection`, `died`, `iyear` and `imonth`; the Cross-Sectional Weights section documents weights and IDs. These public fields do not identify original county strata or map every sampled respondent to the final sub-neighborhood PSU for the 30 split communities.

`communityID` therefore represents a useful parent-community key, but should not be assumed to equal the final sampled PSU for every split community. A county prefix reconstructed from IDs is likewise a geographic grouping candidate, not documented proof of the original design-unit key after boundary changes. Neither key by itself recovers the stratified county selection, the subsequent PPS community stage, the final split-PSU assignment, or the sampling variance.

## Check of the Harmonized CHARLS alternative

The CHARLS portal distributes Harmonized CHARLS Version D (June 2021). The Gateway's current product listing now labels Harmonized CHARLS Version D.2; its creation page says this product uses Waves 1–4 and the 2014 Life History Survey released as of 2021 and contains 4,507 variables. In the current Gateway “Get Harmonized Data” table, the D.2 row has no linked codebook; the public creation page's “Download the loading...” text also exposes no download control. A legacy `startfile.php` URL for a D.2 codebook resolves to a soft 404. Thus, the D.2 codebook and any design-variable specification could not be verified from the current public page. The Version D codebook's overview says that survey-design-adjusted standard errors are available **where CHARLS provided the required design information**; this is not a claim that Version D supplies a complete PSU/strata specification for every wave. A published cross-national harmonization profile specifically reports that cluster and strata variables were unavailable for CHARLS in the CHARLS source data available to that project. Together, these sources do not establish that D.2 adds the missing Wave 3 county stratum or respondent-to-final-sub-PSU mapping. Harmonized age or covariate fields must not be used as a proxy for official design variables.

This is a negative source check, not proof that no later restricted design release exists or that D.2 lacks such variables. The project should reopen the D.2 question only after obtaining its actual versioned codebook/creation documentation through an authorized source and checking the exact design fields and derivation. Do not derive or impute them from harmonized weights, geography, or variable names.

## Current methods decision

There is **no preferred or approved single-stage variance candidate** at this time. This supersedes the earlier provisional suggestion to prioritize a county-prefix-only with-replacement Taylor approximation. The official design description identifies county and community as distinct nested stages and names the community/neighborhood units as PSUs, while the public release lacks the full strata and final split-PSU mapping needed to reproduce the complete design. A county-only approximation omits the community stage; a parent-community-only approximation can merge distinct split PSUs and omit county-stage/strata uncertainty. Neither is guaranteed conservative or nationally design-valid.

Before model fitting, a qualified survey-methods reviewer must assess the exact 2015 design keys, whether the follow-up retains the baseline design and how refreshment cases enter it, the handling of 30 split communities and boundary changes, and what variance method is defensible with the public releases. If that review concludes that no valid design variance can be recovered, results must not be labeled as full-design national inference; any approximate/conditional analysis would need an explicitly limited estimand and independent approval before use.

## Immediate project implications

- Keep the 2015 `Blood_weight` scope decision separate: it is the released cross-sectional blood-response weight, but a correct point weight does not supply PSU/strata variance.
- Do not configure `county-prefix` as the chosen PSU or `communityID` as a complete final PSU map based only on key topology.
- Do not choose a design because it yields smaller standard errors, narrower intervals, or more significant p-values.
- Keep the formal Wave 3 model count at zero until design, age, pair eligibility, frozen model, independent review and disclosure gates pass.

## Official sources

- [CHARLS sample design page](https://charls.pku.edu.cn/en/About/Sample.htm), especially “County-level sampling” and “Neighborhood-level sampling”. This page describes the baseline design; it is not a Wave 3 respondent variance file.
- [CHARLS 2015 data page](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html), public release inventory.
- `sources_official/CHARLS_2015_Codebook.pdf`, “Cross-Sectional Weights” and “Sample Information”.
- `sources_official/CHARLS_2015_Blood_Release_Note.pdf`, design context, Wave 3 dates and blood-weight scope.
- [CHARLS 2015 Blood Data Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf).
- [CHARLS Harmonized data page](https://charls.charlsdata.com/pages/Data/harmonized_charls/en.html), which identifies the public regular-wave product as Version D (June 2021).
- [Gateway current Harmonized Data listing](https://g2aging.org/harmonized-data/get-data) and [Harmonized CHARLS creation-code page](https://g2aging.org/harmonized-charls/creation-code), which identify D.2 and its stated wave/version scope; the reviewed public page did not expose the D.2 codebook or design-variable specification.
- [Harmonized CHARLS Codebook](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/harmonized_charls/application/Harmonized_CHARLS_D.pdf), section 1.6, which qualifies design-adjusted standard errors as available where provided by CHARLS.
- Di Lego et al., [Data Resource Profile: SAGE+ Wave 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC6380306/), “Weights, clustering and stratum variables” (reports cluster and strata variables were unavailable for CHARLS in that project).
