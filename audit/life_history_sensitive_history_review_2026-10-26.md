# 2014 Life History sensitive childhood-history review (2026-10-26)

## Source review

Reviewed the official CHARLS 2014 Life History Questionnaire E7–E8 and Section G1–G2, with matching `FAMILYINFORMATION` Codebook labels. The four structured fields map to two E-role historical-context candidates. Codebook response frequencies and participant data are intentionally excluded from the crosswalk, coverage ledger, and public site.

## E7–E8: relationship history

E7 asks whether the respondent had a romantic partner or dated someone before age 17; a No response skips E8. E8 asks whether the most important relationship had a mostly positive, negative, or neutral influence. This is sensitive retrospective self-report, not a validated relationship-quality scale. The conditional E8 field must not be interpreted as No when blank.

## G1–G2: police custody and reported charge

G1 asks whether the respondent was arrested or taken into police custody by police before age 17; a No response skips G2. G2 asks for the charge category, and if there were multiple events, the questionnaire instructs interviewers to ask about the last one. Arrest/custody is not proof of conviction or guilt. The charge field is conditional and highly sensitive.

The public catalog exposes only the generic variable metadata and questionnaire description: no participant-level answers, no response counts, no narratives, and no derived criminality measure. Any analysis requires separate ethics review, legal/privacy review, authorized-release coding validation, and disclosure-risk review. No claim is made that these fields are analytically suitable for association models.

## Reproducibility and disposition

`scripts/build_life_history_exposure_crosswalk.py` creates the four-field ledger `life_history_sensitive_history_coverage_2014_v1.csv`; tests assert the routes, metadata-only disposition, and absence of frequencies. The 2014 Life History survey remains a special unweighted survey, separate from regular-wave weighted analyses.
