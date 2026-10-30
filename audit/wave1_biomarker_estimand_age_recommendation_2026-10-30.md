# Wave 1 biomarker estimand and age-adjustment recommendation

**Date:** 2026-10-30  
**Status:** methods recommendation for review; not a frozen analysis specification and does not open the model gate.  
**Scope:** CHARLS 2011 household environment × conventional blood-marker associations.

## Recommendation

Use the official Wave 1 blood-biomarker target sample—main respondents and their spouses—as the primary analysis population, with the official biomarker nonresponse weight `bloodweight`. Do not apply an automatic age-45 inclusion cutoff to each person in the primary analysis. The official blood guide defines its target as all baseline main respondents and spouses, while the sample description says the selected main respondent is age 45 or older and their spouse is also interviewed. These are different eligibility statements. Keeping the full blood target aligns the analysis denominator with the released biomarker-weight construction and avoids silently excluding younger spouses.

Describe the target precisely as the baseline interviewed main-respondent/spouse blood sample, drawn from household-living residents and excluding institutionalized people at baseline. Do not call it all Chinese adults or all Chinese people aged 45+ without a separately justified age-domain estimator. This is a cross-sectional weighted association, not a causal effect or personal chemical-dose estimate.

## Age as an adjustment covariate

Age remains an important adjustment variable even when it is not an inclusion rule. Use the official Wave 1 demographic fields and survey interview timing, not a third-party harmonized age field:

- Use `ba002` birth year/month/day and `ba003` calendar type, linked to official interview year/month. Interview day is not released in the reviewed source, so calculated attained age may be an interval around the survey month rather than a falsely exact date.
- For complete solar dates, validate the Gregorian date and calculate the age interval across possible interview days in the recorded month.
- For lunar dates, use the CHARLS-cited `python-lunardate` lineage for dates with an unambiguous ordinary-month route. If the month could be a leap month, preserve an age interval based on the known birth year; the questionnaire has no separate leap-month response.
- The official Wave 1 questionnaire codes `ba003=1` as solar and `ba003=2` as lunar, and says `ba004` is asked only when the complete `BA002` birth-date response is DK/RF. Use `ba004` only when the released year, month, day, and calendar fields are all missing; an invalid or partial DOB must remain unresolved rather than trigger the conditional-age fallback. The provisional derivation code now enforces this conservative route. A source-only exhaustive comparison found exact parity between every row of CHARLS's official Mata lunar lookup and pinned `python-lunardate` 0.1.4; this validates conversion mappings, but not the Wave 1 route, age intervals, or 45+ domain, which remain unapproved candidates.
- For a primary covariate candidate, use the midpoint of the derived attained-age interval and prespecify sensitivity fits using the lower and upper bounds; also compare the complete, unambiguous-DOB subset. Keep unresolved age missing and report the resulting complete-case target. Do not infer precise ages for invalid or absent dates.

This interval treatment is a transparent approximation, not an exact reconstruction of age on the interview day. The pinned conversion implementation matches CHARLS's Mata lookup table cellwise across both official tables; the remaining uncertainty concerns the respondent's recorded calendar route, missing leap-month flag, unknown interview day, and choice of analytic age/domain rule.

## Secondary age-45+ domain

A 45+ analysis can be retained as a secondary estimand only if its target population and weight interpretation are explicitly reviewed. Implement it as a survey domain/subpopulation on the complete biomarker target design; do not delete younger spouses before constructing the design. Because age is interval-valued for some records, prespecify how ambiguous 45th-birthday cases are handled and report an interval-bound sensitivity. Do not use sample eligibility (main respondent selected at 45+) as a substitute for each respondent's age-domain status.

## Weight and model boundary

`bloodweight` is the candidate weight for conventional blood outcomes in the blood-target sample. It does not establish the variance design and cannot be reused automatically for non-blood outcomes, module-specific exposure nonresponse, or age-stratified cystatin C. Keep the primary household-exposure models and their sensitivity families fixed before examining association results. Core covariates remain a separate review item under the existing DAG memo; survey weights/PSU/strata are design elements, never ordinary adjustment covariates.

## Remaining gates before any real-data association

1. Independent review accepts or revises the primary target and age-interval covariate strategy.
2. A Wave 1 county/community variance approximation is explicitly approved for a stated estimand, or further official design information resolves the current PSU/strata gaps. The sparse Community-module `sub_commuID` does not provide respondent-to-final-sub-PSU linkage.
3. Freeze the primary covariates, age missingness/sensitivity rules, blood outcome valid ranges/transforms, and the fasting interpretation for glucose/triglycerides.
4. Bind the frozen configuration to current source/prepared-data hashes and run the readiness gate. Only then reproduce the historical pilot as an exploratory/technical check; do not treat matching pair scope as scientific validation.

## Official sources

- CHARLS [2011 Blood Sample Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf): blood target sample, `bloodweight`, and biomarker response adjustment.
- CHARLS [2011 Sample description](https://charls.pku.edu.cn/en/About/Sample.htm): main-respondent age screening, spouse interview, baseline household sampling frame, and multistage design.
- The reviewed official Wave 1 baseline questionnaire documents `BA004` as conditional on not knowing the birth date; source text is archived in `sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`.
- Candidate age-interval construction and aggregate QA remain protected locally; no participant values or age counts are included in this memo.
