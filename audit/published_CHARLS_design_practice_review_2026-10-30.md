# Published CHARLS design-practice evidence relevant to Wave 1 ExWAS

**Date:** 2026-10-30  
**Status:** Published-methods evidence added to the independent variance review packet; this is not a model authorization.

## Evidence reviewed

1. Zhao et al., *Cohort Profile: The China Health and Retirement Longitudinal Study (CHARLS)*, describes the baseline multistage PPS sample and explicitly calls village/neighborhood units the primary sampling units. It reports three such PSUs selected within each county-level unit, and says household, individual, and biomarker-specific weights were created to account for nonresponse and sampling-frame errors. The article uses weighted descriptive tables but does not provide executable Wave 1 `svyset` syntax, an explicit variance-stratum variable, Taylor linearization details, or a released split-community respondent crosswalk. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3937970/), especially sampling lines 105–112 and weights lines 316–320.

2. Chen et al., *Venous Blood-Based Biomarkers in CHARLS: Rationale, Design, and Results From the 2015 Wave*, confirms that the final sample includes spouses regardless of age and describes the Wave 3 blood weight as the individual sample weight multiplied by an inverse predicted blood-participation probability from a logistic model. It reports that this paper's blood weight addressed nonparticipation; it does not supply a complete PSU/strata variance specification for the Wave 1 blood-target association models. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6825825/), especially study sample lines 158–171 and weighting lines 224–227.

3. The official CHARLS site independently describes the survey as multi-stage stratified PPS and its 2011 follow-up cadence. [About CHARLS](https://charls.pku.edu.cn/en/About/About_CHARLS.htm).

## Consequence for this project

- The published cohort profile is stronger than the general forum response for the **intended PSU level**: it explicitly identifies village/neighborhood units as PSUs. A previously completed protected key-only audit found complete parent-community-key coverage between the Wave 1 respondent spine and official PSU table. Thus `communityID` has both a published design basis and release-key coverage as a parent-community PSU candidate; it is not merely an arbitrary geography proxy. The audit did not publish identifiers and does not determine final variance validity.
- Keep two distinct uses of the key separate. For a household/respondent-level exposure, the parent community may be a candidate variance cluster. For community-module exposures, the official community module has repeated parent-community records for split communities, and respondent rows do not carry `sub_commuID`; a parent-key join alone therefore cannot determine which sub-community-specific record applies to a respondent. Those community-exposure pairs must remain excluded or unresolved until an official release-specific respondent-to-subcommunity crosswalk or an independently reviewed, defensible exposure aggregation rule is available.
- This does **not** establish that a one-stage, unstratified community-cluster Taylor estimator reproduces CHARLS's full multistage design. The same published article says counties were stratified and sampled first, then communities were sampled within counties; the public files reviewed do not give an executable stratum/first-stage variance specification or complete respondent-to-final-sub-PSU map for the 30 split communities.
- The article's separate household, individual, and biomarker weights supports the project's rule that weights are estimand/module specific. It does not mean a biomarker weight alone supplies variance information. Wave 3's blood-weight construction cannot be substituted for Wave 1's official `bloodweight` definition.
- Keep the primary Wave 1 blood-target candidate as main respondents plus spouses, with the official Wave 1 biomarker weight under review; do not mechanically remove spouses under 45. The age-45+ main-sample question is a separate survey-domain estimand. Neither is frozen until independent review.

## Updated review questions

1. Do the documented respondent/PSU key coverage and official sample description suffice to establish the parent-community PSU mapping for ordinary communities, accounting for replacements and boundary changes?
2. For the full blood target and official `bloodweight`, can community PSU clustering be defended as a limited variance approximation when the county selection strata and first-stage variance contribution are unavailable? What target population, degrees of freedom, singleton handling, and limitations must be stated?
3. Does the missing split-community sub-PSU crosswalk change the variance unit for any records, and can the published community-level PSU description support aggregating those sub-PSUs to their parent community for this limited estimator?
4. For community-level exposures, is there an official or scientifically defensible way to link/aggregate repeated sub-community records without assigning an exposure to the wrong respondents?
5. Is any such approximation acceptable only for an internally reviewed exploratory atlas, or also for public inferential results? Treat these as separate decisions.

Until an independent complex-survey reviewer answers these questions and the sample-frame, age, outcome/fasting, and frozen-pilot gates pass, formal CHARLS association models remain 0. No participant-level data were opened for this literature update; no model or test was run.
