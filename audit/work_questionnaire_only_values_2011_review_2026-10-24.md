# 2011 work-module questionnaire-only values review

Reviewed 2026-10-24 against `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` and the work-field crosswalk. This review concerns metadata display only. No respondent data or Codebook frequencies were inspected.

The extracted 2011 Codebook does not provide category labels for the following mapped source fields. The questionnaire does provide option wording for FI004, FI008, FL001 and FL013, but does not print numeric answer-value codes beside those options. The catalogue therefore presents the wording as questionnaire options and explicitly marks numeric codes as unverified. The response order is not silently converted to 1, 2, 3, etc.

FL004 is different: the questionnaire explicitly numbers workplace locations 1–4 and tells the interviewer to mark 0 when there is no fixed address. These questionnaire categories are shown with a warning that released-data coding and storage of the no-fixed-address instruction remain unverified. City/county/province write-in fields remain separate fields and are not folded into these categories.

The questionnaire documents these non-categorical measures and handling notes:

| Field | Questionnaire detail | Interpretation boundary |
| --- | --- | --- |
| FI009 | Work unit's total social-insurance contribution, Yuan/month | Continuous/open response; route follows FI008 and codebook identity must be checked in authorized release. |
| FI012 | Planned work-stop age, 0–120 years; 0 means continuing while physically able | Continuous response with a substantive 0; not a missing-value label. |
| FL008 | Usual hours/week, 0–168; soft check above 80; employed route only | Continuous response; do not turn the soft check into a hard exclusion. |
| FL009 | Monthly wages, bonuses and subsidies before leaving; interviewer marks 0 for no net income and 999997 for a deficit | These are questionnaire instructions, not verified released-data special-value codes. The field also has unfolding-bracket follow-up. |
| FL022_1 | Compensation amount in Yuan | Conditional on the compensation route; refusal/don't-remember bracket follow-up. |
| FL022_2 | Years of work used for compensation, 0–120 | Conditional continuous response. |
| FM051 | Grandchildren below age 6 at retirement, 0–50 persons; interviewer fills 0 if none | Count response; route is conditional on retirement history. |

The public metadata now records units, bounds, special interviewer instructions and routes where the questionnaire states them. Numeric-range and special-value details remain questionnaire evidence, not a claim that the authorized release uses those exact codes. These fields remain candidates pending data-owner-compliant, release-level validation. No analyses or associations are claimed.
