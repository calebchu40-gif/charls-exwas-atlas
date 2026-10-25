# Social participation/care C/E overlap review (2026-10-25)

This source review links four exact wave-field rows in the C catalogue to already identified social-exposure candidates. It does not select adjustment covariates, define an analysis denominator, or make any row analysis-ready. The same field must not be used to adjust for itself.

| Wave | Field | Source-supported identity | Limitation retained |
|---|---|---|---|
| 2011 | `DA056S8` | Activity option “Attended an educational or training course.” | The Codebook summary does not establish respondent-level unselected storage or eligible denominator. Do not infer “No” from absence or use the option index as an individual response. |
| 2020 | `xsoctype_7_` | The questionnaire maps selected activity option 7 to `XSocType[7]`; the Codebook identifies this as a string variable. | Preserve string storage and the source route. Do not assume a numeric 0/1 indicator. The separate frequency question is not part of this field. |
| 2013 | `db022_w2_9_1_s64`, `db022_w2_9_2_s64` | Codebook labels both as volunteer/employee-of-facility help for money management, in two helper slots. | The questionnaire lists this helper as response category 15; `s64` is the field suffix, not a verified response code. Both exact Codebook entries say “No Observations.” Keep the functional-limitation/helper-roster route; do not infer a negative, denominator, or analytic coverage. Reconcile against the authorized release before analysis. |

The 2011 `DA057_8_` row was not linked: the exact field was not found in the 2011 Codebook, while the superficially similar Codebook entry is documented in later waves. This avoids assigning a later-wave frequency label to a 2011 field without evidence.

Official source files checked: `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`, `sources_official/CHARLS_2011_Codebook_extracted.txt`, `sources_official/CHARLS_2013_Questionnaire_extracted.txt`, `sources_official/CHARLS_2013_Codebook_extracted.txt`, `sources_official/CHARLS_2020_Questionnaire_English_extracted.txt`, and `sources_official/CHARLS_2020_Codebook_extracted.txt`. The audit table [`social_exposure_c_overlap_review_v1.csv`](social_exposure_c_overlap_review_v1.csv) records wave, exact field/module, concept link, source path, and caveat. No respondent-level data or numerical Codebook frequencies are reproduced.

The updater [`apply_social_exposure_c_overlap_review.py`](../scripts/apply_social_exposure_c_overlap_review.py) checks exact C/E role keys, source-file existence, and the two 2013 Codebook “No Observations” annotations. Regression tests ensure the four exact rows remain linked and retain their source caveats.
