# 2014 Life History offspring historical-experience candidates (2026-10-26)

## Official sources and questionnaire route

Reviewed CHARLS 2014 Life History Questionnaire pages 24–25 and the `DEMOGRAPHICBACKGROUNDS` Codebook fields for C040 and C041. C040 asks whether any child joined the army; C041 asks whether any child was sent down to the countryside during or before the Cultural Revolution. The questionnaire shows child-slot choices 1–25 and a “None” choice; C041 has one additional “Not applicable (Agricultural Hukou at that time)” choice. A procedure says C037–C041 are asked for child records satisfying the child-finished route, so these fields are not a complete history for all children.

## Candidate fields

| Candidate | Official field family | Fields | Preserved structure |
| --- | --- | ---: | --- |
| Offspring military-service history context | `c040s1`–`c040s26` | 26 | Child-slot options 1–25 and explicit None option.
| Offspring sent-down-to-countryside history context | `c041s1`–`c041s27` | 27 | Child-slot options 1–25, explicit None, and separate not-applicable category.
| **Total** |  | **53** | Historical family context only.

The choice fields are roster-slot selection categories; they are not 53 independent exposures or observations. Keep the C040 and C041 concepts separate. Do not infer No from a blank or combine child slots. C041 not-applicable is not No.

## Exact event-year fields excluded

The questionnaire records start and end years in four C040/C041 numeric field families (`c040_1_`, `c040_2_`, `c041_1_`, `c041_2_`) across up to 18 child slots each. All 72 year fields are explicitly classified as excluded child event dates in the full ledger and are not exposed in the E/P map. No dates, child identities, values, counts or response frequencies are published.

## Interpretation limits

These E-role candidates are intergenerational/historical family-context metadata. They describe the respondent's children, not the respondent's own service, political history, exposure, or clinical phenotype, and they are not direct environmental measurements. Their historical setting and child referent may matter scientifically, but they cannot be treated as respondent-level exposure without a prespecified estimand, authorized-data validation, route/eligibility handling and appropriate sensitivity review. The retrospective 2014 Life History survey has no released weight; these candidates remain separate from regular-wave weighted analyses.

## Output state

The definitions are in `scripts/build_life_history_exposure_crosswalk.py`. The deployed build is app v190 / JSON v56 with 192 concepts / 6,098 source-field rows (E=6,037, P=61). In the 1,920-field module ledger, 1,246 fields are mapped candidates; 131 are C-only interview/roster/family-context metadata; 204 sensitive relative-identity fields remain deferred; 293 are child date components; 18 child-parent linkage fields, 12 roster-order keys, 12 relative birth-date fields, 3 join keys, and 1 release field are excluded. Deploy #322 and Validate #643 succeeded; public homepage and JSON returned HTTP 200 with both C040/C041 concepts and 53 fields present. The website assets contain no microdata or association results.
