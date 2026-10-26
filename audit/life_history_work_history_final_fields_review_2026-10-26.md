# 2014 WORKHISTORY remaining fields and full disposition closure

## Sources and scope

Reviewed the remaining 2014 Life History Questionnaire and Codebook items: F124/F124a, F128, F129a–c, F131, F150–F153 and F_7. This is a metadata-only audit; no participant answers, counts, sample sizes or association results were inspected or generated.

## Candidate mappings

- F124/F124a: current/last-year position (15 slots) and conditional position-transition year (10 slots), preserving the comparison route against F110/F110_a.
- F128: 12 current/last-year monthly net-income fields for own-account self-employment (F_3=4); unpaid household-business help is not included.
- F129a–c: 7 current/last-year military income, 7 military rank, and 6 conditional rank-change-year fields (F_3=6).
- F131: four short-duration (under-five-year) job-type indicators for government in-staff, public institution, state-owned enterprise and military service. The questionnaire refers to the longest-duration eligible job when several qualify.
- F150–F153: separate retirement-procedure status, procedure year, initial monthly pension amount, pension-to-pre-retirement-salary percentage, and job referent (5 fields total). Follow-up items are conditional on F150=Yes.

These add 66 mapped candidate fields while retaining reference periods, units, episode slots and routed denominators. These are retrospective employment/retirement socioeconomic contexts, not direct environmental-agent/dose measurements. Nominal income/pension amounts are not harmonized across eras.

## F_7 route/quality exclusion

The 19 repeated F_7 fields ask whether another job lasting more than six months remains to be recorded. A Yes routes the interviewer back to F_2 to add that job; therefore these fields are excluded as `excluded_route_quality_metadata`, not treated as independent exposure/status variables.

## WORKHISTORY full disposition

All 2,024 Codebook fields now have an explicit disposition: 1,968 mapped candidate fields; 19 sensitive workplace-location fields excluded from the public crosswalk; 33 interviewer route/quality fields excluded (F_1, F_5 and F_7 checks); three linkage keys excluded; and one release-version field excluded. No substantive WORKHISTORY field remains deferred. Location text and participant data are not published.

Whole Life History catalogue rebuild: 159 concepts / 4,809 mappings (E=4,763, P=46). These are metadata mapping counts, not independent indicators, sample sizes or model results. Formal association models remain zero.
