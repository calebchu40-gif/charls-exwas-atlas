# Wave 1 fasting-status source reconciliation

**Status:** source review note; outcome handling remains subject to the hash-bound methods review.

## CHARLS 2011 official documentation

The CHARLS 2011–2012 Blood Sample Users' Guide states that respondents were asked to fast overnight, blood was still collected from non-fasting respondents, and fasting status was recorded in the data. It reports that over 92% of respondents who provided blood reported fasting. The same guide warns that non-fasting glucose can be higher and notes that about 8% of respondents provided non-fasting blood samples. It describes the measured triglyceride assay and reports population summaries, but does not give the numeric coding for Wave 1 field `qc1_va003` in the reviewed text.

The Wave 1 release header audit found no Stata value labels for `qc1_va003`. The 2011 user guide, official document index and reviewed questionnaire materials establish that fasting status is collected, but do not establish its numeric value mapping. Wave 3 `bl_fasting` labels cannot be transferred to Wave 1.

## Candidate handling by outcome

- **Glucose:** keep its seven pilot coefficients blocked until an authoritative Wave 1 mapping supports a prespecified fasting rule. The official CHARLS guide expressly warns that non-fasting glucose may be higher. Do not infer codes from value frequencies or another wave.
- **Triglycerides:** candidate primary handling is all observed blood samples under a continuous non-fasting lipid-profile estimand. The EAS/EFLM joint consensus recommends routine non-fasting lipid profiles and says fasting sampling may be considered in selected very-high-triglyceride situations. This clinical consensus does not replace review of CHARLS assay behavior or survey-specific model assumptions. A fasting-status sensitivity is desirable only after the Wave 1 mapping is verified from an authoritative source.
- **Other 13 blood outcomes:** fasting relevance must be assessed per analyte; do not apply the glucose rule to every outcome.

A third-party CHARLS variable catalog was discovered during literature search and reports a candidate `qc1_va003` mapping, but it is not an official CHARLS source. It is recorded only as a lead for source reconciliation and is not used to assign codes or unblock an analysis.

## Effect on the pilot

The 105 registered coefficients remain unchanged. The current implementation blocks the seven glucose coefficients and leaves the seven triglyceride coefficients eligible for review under the all-sample candidate rule. The remaining 91 coefficients also remain unapproved until their outcome validity, age/target estimand, covariates and Option A approximation are reviewed. Thus, 98 coefficients are candidates for model fitting after approval; this count is a prespecified registry count, not an analysis sample size or a claim that the coefficients are estimable.

No CHARLS participant values were used in this source review. No association was fitted. This note is included in the pilot plan fingerprint; any subsequent change requires a fresh hash-bound approval.

## Sources

- CHARLS, *2011–2012 National Baseline Blood Data Users' Guide* (March 2014), especially blood collection and fasting status (PDF pp. 8–9) and the discussion of non-fasting glucose (PDF p. 17): https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf
- Nordestgaard et al. European Atherosclerosis Society/European Federation of Clinical Chemistry and Laboratory Medicine joint consensus statement on non-fasting lipid profiles, *European Heart Journal* (2016): https://academic.oup.com/eurheartj/article/37/25/1944/1749006
- CHARLS official Wave 1 documentation index (the Codebook page requires account access): https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html
- Secondary-only discovery lead for the candidate `qc1_va003` labels; not accepted as authority and not used to assign codes: https://www.dbcodebook.cn/nodes/post/56/
