# Execution checkpoint: pilot gates and scale-up route (2026-10-27)

## Work performed this checkpoint

- Rechecked the repository and protected Wave 1 intake state. The metadata-only preflight finds the four required inputs (`All Data`, `PSU`, `Weight`, and `Blood`) missing or ambiguous. Its report is stored under the protected local `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\qa_outputs` directory; no participant-level values were read and no association model was run.
- Revisited the primary CHARLS source pages. The official Wave 1 page separately lists the household/community archive, PSU file, Weight file, Blood file, Codebook, national baseline guide, and Blood guide. The official FAQ directs researchers to register/apply and read each wave's guide and questionnaire before analysis.
- Rechecked the variance-method gap against CHARLS's official sampling description and the general UN survey-sampling guidance. CHARLS documents the sampling stages and implicit sorting/stratification, but the material reviewed here still does not establish a released respondent-level variance-stratum mapping, replicate weights, or a complete variance recipe. The 30 split large communities remain a specific PSU-mapping issue. Geography variables must not be substituted for a design stratum without source evidence.

## Current decision

No real-data Wave 1 pilot can be newly prepared or fitted until the official inputs are staged, source identity is reviewed, the table is rebuilt from those sources, and the separate analysis-readiness record is completed. This is a data-and-method gate, not a failed statistical pilot. Public formal association models/results remain zero. Candidate catalog rows and metadata co-availability are not association results or analytic sample sizes.

## Locked path after the gate is cleared

1. Authenticate the four Wave 1 inputs against the official release records; run the metadata-only preflight and reconcile source tables, keys, denominators, age/blood eligibility, and weight coverage.
2. Resolve the final respondent-to-PSU mapping for split communities and identify official variance strata/replicate weights or obtain an independently reviewed, explicitly limited approximation. Do not infer strata from province, city, urbanicity, region, or `areatype`.
3. Freeze the target estimand, variables/coding, survey-design declaration, M1/M2 adjustment roles, handling of non-estimable hypotheses, and full 105-coefficient pilot family before fitting.
4. Fit the complete family only after source and readiness gates pass. Review weight/effective-sample support, PSU support, degrees of freedom, convergence, estimates/uncertainty, influential PSU sensitivity, missingness, and predeclared multiplicity adjustments (BY-FDR and Bonferroni). Keep all hypotheses and failures in the private record; success is validity and reproducibility, not statistical significance.
5. If the pilot is valid and independently reproducible, freeze its code/source/plan record, then run the predeclared 2011 household-environment expansion: primary family K=150 and heating-route subdomain family K=90, adjusted separately. Keep the latter's routed target population explicit.
6. Only after 2011 review, assess each later wave separately for outcome/exposure availability, wording/units, cross-sectional eligibility, weight and biomarker response, PSU/variance design, and target population. Do not pool waves by copying NHANES cycle formulas.
7. Export only complete, disclosure-reviewed aggregate families to the website. Maintain distinct catalog-candidate, analyzed, method-reviewed, and publicly released statuses.

## No-go branches

- If official source identity or the analysis frame cannot be reconciled, stop real-data fitting and document the exact unresolved source/frame item.
- If design-based variance information remains unavailable, obtain a methods review of a clearly limited approximation before fitting; if no defensible approximation supports the intended target, narrow the estimand or do not claim representative inference.
- If the full pilot is not reproducible or diagnostics fail, repair and rerun the same frozen family; do not select replacements based on preliminary p-values.
- If the pilot is valid but null, continue the predeclared scale-up if the scientific scope remains justified. Null results do not trigger exploratory fishing.
- If a family has disclosure-sensitive results, withhold the entire predeclared family unless an approved policy allows a different complete release.

## Sources reviewed

- [CHARLS 2011 Wave 1 official data page](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)
- [CHARLS official sampling description](https://charls.pku.edu.cn/en/About/Sample.htm)
- [CHARLS official FAQ](https://charls.pku.edu.cn/en/Faq/Frequently_Asked_Questions.htm)
- [CHARLS 2011 National Baseline User Guide](https://charls.pku.edu.cn/en/data/User2011.pdf)
- [CHARLS Blood Sample Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)
- [UN Handbook on Survey Sampling: Estimation of Sampling Errors](https://unstats.un.org/unsd/demographic/sources/surveys/handbook23june05.pdf)

No website payload or analysis result was changed in this checkpoint. No restricted CHARLS data, personal IDs, private hashes, QA counts, or model estimates were added to the repository.
