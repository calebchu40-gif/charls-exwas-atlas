# 2014 WORKHISTORY F_5/F_6 interval status and F120 slot review

## Sources and scope

This review uses the public 2014 CHARLS Life History Questionnaire and Life History Codebook already stored in `sources_official/`. It maps questionnaire/codebook metadata only. It does not inspect participant-level responses, estimate frequencies, or produce association results.

## F_5 and F_6 between-job routing

F_5 is an interviewer completeness check for a gap between recorded jobs. If the respondent worked during the interval, the interviewer returns to F_2 to add the omitted job. The 12 repeated F_5 fields (`f_5_2_`–`f_5_12_`, `f_5_14_`) are therefore excluded as `excluded_route_quality_metadata`; they are not respondent exposures or nonwork outcomes.

F_6 records the respondent's reported status during intervals where F_5 confirms there was no work. The 144 structured fields (`f_6_2_`–`f_6_12_`, `f_6_14_`, with select-all options 1–12) map to the candidate concept `life_history_between_job_nonwork_status`. Categories include unemployment, illness, childbirth, family care, leisure/travel, training, prison, schooling and other. The interval suffix and multiple-response structure are retained. A blank or routed skip is not interpreted as “no”; free-text “other” detail is not mapped. These are retrospective life-course socioeconomic/context variables, not measured environmental exposures or clinical diagnoses.

## F120 episode-slot completeness

The former F120 pattern covered suffixes 0–13 and omitted suffix 15 (suffix 14 has no Codebook fields). The Codebook contains 17 reason fields for each of 15 existing numbered job slots (0–13 and 15), so slot 15 adds 17 mappings. The corrected pattern covers all 255 structured nonmilitary job-cessation fields. Military service remains a separate eight-field F120a concept and route; it is not pooled with F120.

## Resulting WORKHISTORY disposition

The 2,024 Codebook fields now have the following local dispositions:

- 1,629 mapped candidate fields;
- 358 substantive fields deferred for source/construct review;
- 19 sensitive workplace-location fields excluded from the public crosswalk;
- 14 interviewer route/quality fields excluded (F_1_0/F_1_1 and the 12 F_5 checks);
- 3 linkage keys excluded; and
- 1 release-version field excluded.

The generated whole Life History catalog now contains 128 concepts and 4,470 field mappings (E=4,424, P=46). Mapping-row counts are not independent scientific indicators, eligible sample sizes, or fitted models. Formal association models remain zero.

## Analysis constraints

Do not treat F_6 categories as mutually exclusive; the question is select-all. Do not infer work status from missing F_6 values. Keep each interval distinct and preserve the F_5 eligibility route. F120 reason fields are conditional on an ended job and should not be analyzed without a defined eligible denominator and validated response coding. All fields remain catalog candidates pending authorized-release data QA and an explicit estimand/design plan.
