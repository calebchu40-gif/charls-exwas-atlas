# Wave 1 Blood Users' Guide: weight and measurement implications

**Reviewed:** 2026-10-30, original PDF pages visually checked for printed pages 6, 8-9, 11-12, and 13-14.  
**Status:** Source review adds a concrete weighted-target candidate and measurement-condition evidence. It does not independently approve an estimator, finite sentinel mapping, or model freeze. No CHARLS participant values were opened for this review.

## Official source findings

The official CHARLS *Blood Data Users' Guide* (PDF published by CHARLS; the project's archived copy is `sources_official/CHARLS_2011_Blood_User_Guide.pdf`) states:

1. **Blood target and response:** the blood target was 17,708 main respondents and spouses from the national baseline; 11,847 blood samples were collected. The Guide characterizes the baseline sample as representative of people aged 45+ living in households, while the blood target is specifically main respondents plus spouses. Do not silently turn this into a claim about all Chinese adults aged 45+ or about institutionalized populations.
2. **`bloodweight` construction:** it combines the main-data individual weight with an inverse predicted probability of blood-collection participation. The participation model uses village dummies, age dummies, sex, sex-by-age interactions, and schooling; inverse predicted probabilities are capped at the 99th percentile. The Guide states that it corrects household and individual nonresponse plus blood-collection nonparticipation and explicitly relies on a strong selection-on-observables assumption. This supports `bloodweight` as the source weight for analyses of blood-sample outcomes under the documented target, subject to the released design's unresolved variance structure and the stated assumption.
3. **Fasting selection:** the Guide reports that about 8% of respondents provided non-fasting samples and warns that glucose from those specimens may be higher. It does not document a further fasting-status selection correction in `bloodweight`. A model using all blood participants with a fasting measurement-condition term and a fasting-stratified sensitivity is a candidate for glucose/TG; a fasting-only result is a conditional estimand and must not inherit a population-representativeness claim from `bloodweight` without additional evidence.
4. **Assay detection limits versus observed values:** the methods table gives assay coefficients of variation and detection limits. Separately, Table 4/5 give observed descriptive ranges, and the Guide says a small number of extreme values were omitted only from the kernel-density plots. Thus detection limits, clinical cutoffs, and the plotted density trims are not licensed exclusion rules. Published observed ranges are reconciliation references only, not hard admissibility bounds.
5. **Measurement notes:** the Guide discusses possible downward HbA1c differences in frozen samples. Cystatin C was measured in a subsample: all blood participants age 70+ and a random subsample under 70 (N=8,878). This supports keeping cystatin C out of the common 15-outcome full-sample family unless its sampling mechanism and applicable weight are separately resolved.

## Candidate estimand and current gates

- **Main blood-outcome sample candidate:** observed official Wave 1 Blood records with valid positive `bloodweight`, analyzed for a clearly described blood-target domain. For the proposed age-45+ domain, present the estimand as the age-eligible subset of the blood target; do not generalize beyond that source population. Exact age handling, spouse coverage and domain implementation still require the frozen plan and design review.
- **Continuous outcome handling candidate:** treat documented Stata missing values as missing; retain finite assay values without deletion based on detection limits, clinical cutoffs, or distributional extremes. A finite numeric sentinel map is not documented in the reviewed Blood Guide/header; absence of such a map is not proof that a sentinel cannot exist. Until an independent rule is recorded, mark that detail unresolved and retain the fail-closed model gate.
- **Glucose/TG:** keep the 14 coefficients registered. All-blood-participant models with fasting-status adjustment, plus a predeclared fasting-status interaction or conditional sensitivity, are candidates for reviewer decision. Do not estimate a fasted-only population effect with the blood-response weight alone as though fasting selection had been corrected.
- **Variance:** this guide explains the nonresponse weight but does not furnish a respondent-level strata/final-PSU mapping or replicate weights. User-selected community-cluster WR Taylor remains an approximation requiring methodological acceptance.

## Source anchors

- Official CHARLS 2011 Wave 1 page lists Blood Users' Guide separately from the baseline Codebook: <https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html>.
- Guide printed pages 6 (assay methods/detection limits), 8-9 (blood target/response and `bloodweight`), 11-12 (nonfasting/HbA1c/cystatin C), and 13-14 (descriptive ranges and N).
- Official Peking University baseline dataset record (file 201, Blood package): <https://opendata.pku.edu.cn/dataset.xhtml?persistentId=doi%3A10.18170%2FDVN%2FIZU8OF&version=1.1>.

This review is source-level. It does not claim independent methods approval, does not close the finite-sentinel/outcome-rule gate, and does not authorize any association run.
