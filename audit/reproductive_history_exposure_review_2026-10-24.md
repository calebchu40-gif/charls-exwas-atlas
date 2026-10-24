# Female reproductive timing as life-course exposure candidates

Reviewed 2026-10-24 against the official 2011, 2013, 2015 and 2018 questionnaires and wave Codebooks. No respondent-level records, Codebook frequencies, or association results were used.

## Candidate constructs

The catalog now contains two separate wave-specific exposure candidates: `age_at_menarche` (`DA026_2`) and `age_at_menopause` (`DA028_2`) in 2011, 2013, 2015 and 2018. Only the response component explicitly designated as age in years is mapped. The separate `DA026_1`/`DA028_1` calendar-year fields are not converted into ages. The two constructs are not combined with one another and are not declared harmonized across waves.

These are retrospective, female-only life-course measures, not routine adjustment recommendations. The observed group is restricted by the questionnaire's new-interview, prior-wave menopause, current menopause-status and age-versus-year response routes. Structural skips, year responses, and the 2018 `never menstruated` answer are not ages and must not be recoded as zero or ordinary missing values. Any future model must define the eligible denominator from the authorized release and preserve these routes.

## Wave-specific routing

- **2011:** The official baseline questionnaire routes the reproductive history block to new interviews and separately records year and age components. The item asks menopause status before the conditional menopause-timing item; men are routed past this section.
- **2013 and 2015:** The official follow-up questionnaires retain separate prior-wave (`ZDA`) history fields. Returning women already reported as menopausal skip the current transition questions; those not previously menopausal are routed through the current menopause-status branch. New respondents are asked the menarche and menopause history block. The direct `DA026_2` and `DA028_2` age components are mapped; `ZDA026_2`/`ZDA028_2` preload/history components are deliberately excluded pending release-level identity and value-format review.
- **2018:** The questionnaire explicitly routes new respondents to `DA026`–`DA028`; returning respondents with prior menopause skip the event timing item, while those not previously menopausal follow the current status route. `DA026` includes a separate never-menstruated response. Men and women on ineligible routes are not treated as having a numeric age.

## Interpretation and release gate

The Codebooks identify the direct `_2` components as age. The questionnaire shows that the sibling `_1` components record calendar year, so the site preserves the age field as a candidate without reconstructing it from year. The mapping is suitable for catalog search and future pair-availability review only. It does not establish eligible sample size, age-reporting completeness, longitudinal measurement equivalence, analytic readiness, or an estimated association. The source-specific crosswalk is [`reproductive_history_exposure_crosswalk_v1.csv`](reproductive_history_exposure_crosswalk_v1.csv); the idempotent catalog updater is [`apply_reproductive_history_exposure_review.py`](../scripts/apply_reproductive_history_exposure_review.py).
