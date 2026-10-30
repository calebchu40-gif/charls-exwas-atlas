# Wave 1 biomarker estimand and age-adjustment recommendation

**Date:** 2026-10-30  
**Status:** methods recommendation for review; not a frozen analysis specification and does not open the model gate.  
**Scope:** CHARLS 2011 household environment × conventional blood-marker associations.

> **Status update (2026-10-30):** This memo records a pre-decision recommendation for using the full official blood target as the primary analysis population. The user later supplied a specific working plan that retains the complete observed blood sample as the survey design object, estimates the lower-bound age-45+ domain as primary, and prespecifies upper-bound age-45+ and the full observed sample as sensitivities. That user-selected plan controls current implementation pending independent review. The concern in this memo remains part of the review packet: the 45+ domain must be described as a domain of the blood-target population, not as the full blood target or all Chinese adults aged 45+.

## Current user-selected primary estimand candidate

The current project working plan, supplied after this memo's original recommendation, is to retain the complete observed Wave 1 blood-sample design object and estimate the **age domain whose official age-interval lower bound is at least 45 years** as the primary domain, using `bloodweight`. Prespecified sensitivity domains are the upper-bound ≥45 rule and the complete observed positive-`bloodweight` blood-sample frame. This is a survey-domain analysis: do not physically remove younger respondents/spouses before constructing the design object. The estimate pertains only to the defined domain within the official blood target and must not be described as all Chinese adults aged 45+.

The original recommendation below to make the complete blood target the primary population is superseded for current implementation. The domain target, interval-boundary classification, full design-frame construction and pair-specific complete-case set still require independent review; this memo does not freeze them or open the model gate. The official blood target comprises baseline main respondents and spouses, while main-respondent age eligibility and spouse eligibility differ. `bloodweight` handles the blood nonresponse weighting described by CHARLS but does not automatically correct exposure/covariate complete-case selection.

Describe the target precisely as a domain within the baseline interviewed main-respondent/spouse blood target, drawn from household-living residents and excluding institutionalized people at baseline. This is a cross-sectional weighted association, not a causal effect or personal chemical-dose estimate.

## Age as an adjustment covariate

Age remains an important adjustment variable even when it is not an inclusion rule. Use the official Wave 1 demographic fields and survey interview timing, not a third-party harmonized age field:

- Use `ba002` birth year/month/day and `ba003` calendar type, linked to official interview year/month. Interview day is not released in the reviewed source, so calculated attained age may be an interval around the survey month rather than a falsely exact date.
- For complete solar dates, validate the Gregorian date and calculate the age interval across possible interview days in the recorded month.
- For lunar dates, use the CHARLS-cited `python-lunardate` lineage for dates with an unambiguous ordinary-month route. If the month could be a leap month, preserve an age interval based on the known birth year; the questionnaire has no separate leap-month response.
- The official Wave 1 questionnaire codes `ba003=1` as solar and `ba003=2` as lunar, and says `ba004` is asked only when the complete `BA002` birth-date response is DK/RF. Use `ba004` only when the released year, month, day, and calendar fields are all missing; an invalid or partial DOB must remain unresolved rather than trigger the conditional-age fallback. The provisional derivation code now enforces this conservative route. A source-only exhaustive comparison found exact parity between every row of CHARLS's official Mata lunar lookup and pinned `python-lunardate` 0.1.4; this validates conversion mappings, but not the Wave 1 route, age intervals, or 45+ domain, which remain unapproved candidates.
- For a primary covariate candidate, use the midpoint of the derived attained-age interval and prespecify sensitivity fits using the lower and upper bounds; also compare the complete, unambiguous-DOB subset. Keep unresolved age missing and report the resulting complete-case target. Do not infer precise ages for invalid or absent dates.

This interval treatment is a transparent approximation, not an exact reconstruction of age on the interview day. The pinned conversion implementation matches CHARLS's Mata lookup table cellwise across both official tables; the remaining uncertainty concerns the respondent's recorded calendar route, missing leap-month flag, unknown interview day, and choice of analytic age/domain rule.

## Age-domain construction and prespecified sensitivities

Implement the primary lower-bound ≥45 domain and the upper-bound ≥45 and full observed blood-frame sensitivities as survey domains on the complete blood-sample design object; do not delete younger spouses before constructing the design. Because age is interval-valued for some records, the lower-bound rule is conservative for ambiguous birthdays; report the prespecified upper-bound alternative. Do not use sample eligibility (main respondent selected at 45+) as a substitute for each respondent's own age-domain status. Independent review must decide whether this domain estimand is supported by `bloodweight` and whether complete-case associations admit the intended interpretation.

## Weight and model boundary

`bloodweight` is the candidate weight for conventional blood outcomes in the blood-target sample. It does not establish the variance design and cannot be reused automatically for non-blood outcomes, module-specific exposure nonresponse, or age-stratified cystatin C. Keep the primary household-exposure models and their sensitivity families fixed before examining association results. Core covariates remain a separate review item under the existing DAG memo; survey weights/PSU/strata are design elements, never ordinary adjustment covariates.

## Remaining gates before any real-data association

1. Independent review accepts or revises the user-selected lower-bound ≥45 primary domain, upper-bound/full-frame sensitivities, and age-interval covariate strategy.
2. Independently review Option A (`communityID` cluster, no strata, WR Taylor approximation) and its stated limitations. The sparse Community-module `sub_commuID` does not provide respondent-to-final-sub-PSU linkage; if Option A is judged insufficient, association inference remains blocked.
3. Freeze the primary covariates, age missingness/sensitivity rules, blood outcome valid ranges/transforms, and the authoritative fasting interpretation. Until Wave 1 `qc1_va003` mapping and review pass, all seven glucose and seven triglyceride hypotheses remain registered but blocked from estimation.
4. Bind the frozen configuration to current source/prepared-data hashes and run the readiness gate. Only then reproduce the historical pilot as an exploratory/technical check; do not treat matching pair scope as scientific validation.

## Official sources

- CHARLS [2011 Blood Sample Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf): blood target sample, `bloodweight`, and biomarker response adjustment.
- CHARLS [2011 Sample description](https://charls.pku.edu.cn/en/About/Sample.htm): main-respondent age screening, spouse interview, baseline household sampling frame, and multistage design.
- The reviewed official Wave 1 baseline questionnaire documents `BA004` as conditional on not knowing the birth date; source text is archived in `sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`.
- Candidate age-interval construction and aggregate QA remain protected locally; no participant values or age counts are included in this memo.
