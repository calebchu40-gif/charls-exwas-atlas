# 2014 Life History pregnancy-history source review (2026-10-26)

## Scope and evidence

Reviewed the pregnancy-history section in the official 2014 CHARLS Life History Questionnaire (printed pp. 26–27; extracted questionnaire pp. 30–31) against the `DEMOGRAPHICBACKGROUNDS` Codebook fields. The questionnaire says these questions are asked of female respondents only, organized before/between/after biological-child births, and intended to collect induced abortion, miscarriage/natural abortion, and stillbirth histories. This review uses question wording, interviewer instructions, field names and Codebook labels only. It uses no respondent-level data or Codebook frequencies.

## Candidate groups

| Candidate concept | Field families | Interpretation and route |
| --- | --- | --- |
| `life_history_pregnancy_outcome_history` | C025a, C028, C030a | Interval-level report of whether a pregnancy ended in induced abortion, miscarriage/natural abortion, or stillbirth; C030a repeatedly screens for additional events. |
| `life_history_pregnancy_termination_timing_duration` | C026, C027 | Event-slot year of pregnancy termination and recalled duration in months. The interviewer instruction codes less than one month as 1. |
| `life_history_induced_abortion_reported_reason` | C029 | Multi-select reasons asked only after C028 identifies induced abortion; categories include family-planning policy, not wanting a child, sex preference related to ultrasound result, ultrasound indication of poor fetal health, and other. |

The questionnaire routes C026–C029 only after a positive pregnancy-loss screen; C029 is conditional on induced abortion. C025a slots refer to periods before the first biological child, between births, and after the last birth. C030a is a separate repeated additional-event screen. These structures remain components of retrospective history, not independent observations or derived event counts. The C024a_1 child-order slots are excluded as roster-order/linkage keys.

## Interpretation and safeguards

These items refer to the respondent's pregnancy history, so they are plausible life-course/reproductive E candidates in a metadata atlas. They are not current environmental measurements, clinical phenotypes, or direct causal exposures. The three groups are sensitive reproductive-health metadata, particularly C029. The public catalogue contains only official question/field metadata: no names, dates from participants, responses, frequencies, or association results. Any analysis or broader public display requires separate ethics, privacy, disclosure-control, target-population and design review. Routed/blank fields cannot be recoded as No.

The 2014 Life History release note says no weight is provided. These records therefore remain outside regular-wave weighted E/P pair-coavailability and association analysis unless a defensible estimand, linkage and design are separately established. The Codebook's event-slot layout must be verified in the authorized data release before deriving counts or aligning an event to a respondent's age or health outcome.

## Coverage status

The reproducible builder now maps the reviewed C025a, C026, C027, C028, C029 and C030a field families to three candidate concepts and excludes C024a_1 slots as roster-order keys. Other child/family fields remain explicitly deferred until their respondent/relative referent, route, sensitivity, and role are source-reviewed. The 1,920-field module ledger remains exhaustive and unique.

Rebuild metadata with `python scripts/build_life_history_exposure_crosswalk.py`; the builder deliberately ignores Codebook frequency tables.
