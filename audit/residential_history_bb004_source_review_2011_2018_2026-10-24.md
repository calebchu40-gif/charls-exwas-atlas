# BB004 residential-history source review, 2011–2018

Reviewed official wave questionnaires and Codebooks. No respondent records, Codebook frequencies, or descriptive summaries were used.

| Wave | Source interpretation | Catalog treatment |
|---|---|---|
| 2011 | 2011 BB004 has an unresolved official-source identity conflict: the baseline questionnaire asks whether the respondent lived in the same village/community as now when first moving to the permanent address, while the 2011 Codebook describes the field as whether the respondent lived in the same county/city as the first move. Keep response labels blank and retain this C record on HOLD FOR SOURCE VALIDATION, excluded from analysis until the released field identity is reconciled. Do not harmonize with later BB004 rows or infer a response meaning from the shared code name. | Response labels withheld; HOLD FOR SOURCE VALIDATION pending field identity reconciliation. |
| 2013 | 2013 BB004 asks whether, when first moving to the permanent address, the respondent already lived in the same village/community as currently. A Yes response skips the conditional BB005 year item; No routes to that year. This is residential-history context, not current neighborhood quality or an environmental dose. Keep BB005 year separate, preserve routed missingness, and do not infer cross-wave equivalence or routine covariate use. | 1=Yes; 2=No; retain conditional year follow-up and wave-specific reference point. |
| 2015 | 2015 BB004 asks whether, when first moving to the permanent address, the respondent already lived in the same village/community as currently. A Yes response skips the conditional BB005 year item; No routes to that year. This is residential-history context, not current neighborhood quality or an environmental dose. Keep BB005 year separate, preserve routed missingness, and do not infer cross-wave equivalence or routine covariate use. | 1=Yes; 2=No; retain conditional year follow-up and wave-specific reference point. |
| 2018 | 2018 BB004 asks whether, when first moving to the current address BB001_W3, the respondent already lived in the same village/community as currently. A Yes response skips the conditional BB005_W3 year item; No routes to that year. This is residential-history context, not current neighborhood quality or an environmental dose. Keep BB005_W3 year separate, preserve routed missingness, and do not infer cross-wave equivalence or routine covariate use. | 1=Yes; 2=No; retain conditional year follow-up and wave-specific reference point. |

Sources by wave:

- 2011: `sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`; `sources_official/CHARLS_2011_Codebook_extracted.txt`
- 2013: `sources_official/CHARLS_2013_Questionnaire_extracted.txt`; `sources_official/CHARLS_2013_Codebook_extracted.txt`
- 2015: `sources_official/CHARLS_2015_Questionnaire_extracted.txt`; `sources_official/CHARLS_2015_Codebook_extracted.txt`
- 2018: `sources_official/CHARLS_2018_Questionnaire_extracted.txt`; `sources_official/CHARLS_2018_Codebook_extracted.txt`

BB004 is residential-history information, not a direct environmental dose or current neighborhood-quality measure. The same variable name does not establish equivalence: the 2011 Codebook's geographic reference conflicts with its questionnaire, and the later question references differ in wording/routing. Keep each wave separate unless the released variable identity, eligibility, and target estimand are validated.
