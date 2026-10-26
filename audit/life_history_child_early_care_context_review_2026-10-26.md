# 2014 Life History offspring early-care context review (2026-10-26)

## Scope and evidence

Reviewed the official Life History Questionnaire's C034a1–C034g2 child-care and preschool section (printed pp. 20–23; extracted questionnaire pp. 24–27) against the `DEMOGRAPHICBACKGROUNDS` Codebook. Source review used question wording, route instructions, response categories and Codebook field identities. No child names, participant values, Codebook frequencies or association results were accessed or published.

## Candidate groups and coverage

| Candidate concept | Official field families | Fields | Referent and key route |
| --- | --- | ---: | --- |
| `life_history_maternal_employment_and_leave_at_childbirth` | C034a1 | 54 | Female respondent's employment and conditional leave/maternity-leave days at the birth of a biological or unclassified child. |
| `life_history_childcare_service_availability` | C034a2 | 18 | Whether a creche/kindergarten was available in the child's residence community or a parent's work unit before age five; the question combines sources. |
| `life_history_child_early_education_access` | C034b1/C034b2 | 38 | Offspring's creche/kindergarten provider/attendance category, entry age and full-day attendance before age five. |
| `life_history_child_residence_and_care_under_age2` | C034e1/C034f1/C034c1 | 209 | Offspring's main household, conditional coarse locality and multi-select caregiver types before age two. |
| `life_history_child_residence_and_care_age3to5` | C034g1/C034g2/C034d1 | 210 | Same constructs for ages three to five. |

All repeated child slots and caregiver options remain source components under concept groups. The questionnaire limits C034–C038a1 to children born before 12 December 1998; it skips the block for children who died before age one and skips selected age-3–5 items for deaths before age three. The under-age-two locality question follows a non-own-home response, and the age-3–5 locality question likewise follows the household response. Missing routed responses are not No.

## ExWAS role and limits

These are family/offspring-context E candidates reported by a CHARLS respondent. They are not the respondent's own childhood exposures, child phenotypes, objective community service measurements, or direct environmental-agent doses. `C034a1` is the one group directly describing the female respondent's work and leave; it is still a retrospective special-wave measure tied to a child's birth. The remaining groups concern the offspring's caregiving, residence or preschool context and need a clearly defined respondent-level estimand before association analysis.

The fields are metadata only. No child names, exact locality, participant-level values or frequencies enter the public payload. The special 2014 Life History release has no weight; these candidates remain outside the regular-wave weighted pair matrix. Authorized-release route/storage, analytic target population, disclosure risk and any linkage to regular CHARLS waves require separate verification.

## Rebuild and disposition

The builder maps 529 Codebook fields to the five concepts above. Other offspring biography fields (such as education, marriage, religion, minority identity, military service, residence-migration history and health/death details) remain deferred until separately reviewed for referent, sensitivity and target estimand. The full 1,920-field module ledger remains exhaustive and unique.

Rebuild with `python scripts/build_life_history_exposure_crosswalk.py`; the builder ignores frequency tables.
