# 2014 Life History respondent hukou-history review (2026-10-26)

## Scope and source basis

Reviewed the official Life History Questionnaire Hukou Section, HK001–HK006 (printed pp. 28–30; extracted pp. 32–34), against the `DEMOGRAPHICBACKGROUNDS` Codebook. This section refers to the respondent's first registered hukou and later type/location changes. The review uses question text, routing, option wording and Codebook identifiers only; it uses no response values or Codebook frequencies.

## Candidate concepts and full coverage

| Concept | Fields | Count | Content |
| --- | --- | ---: | --- |
| `life_history_initial_hukou_context` | HK001, HukouType | 2 | Initial hukou type and coarse first-location category. |
| `life_history_hukou_change_history_and_reasons` | HK002/HK002_1/HK003/HK004/HK005/HK006 | 268 | Repeated change screen/year, type/location distinction, new type, new coarse location, and multi-select reasons. |

All 270 Codebook fields are now explicitly mapped: HK001 1, HukouType 1, HK002 and HK002_1 22, HK003 10, HK004 6, HK005 10, and HK006 220. HK006 contains 10 event slots × 22 option indicators (options 1–20, 23 and 24); an `Other` option is represented, but no open-text response is copied.

## Route, release and interpretation limits

Questionnaire routes are retained: HK002_1 follows a Yes change screen; HK004 follows HK003=1/2 (type changed); HK005 follows HK003=1/3 (location changed); HK006 asks reasons for each change. Codebook capacities differ: 11 HK002/change-year slots, 10 HK003, six HK004, 10 HK005, and 10 HK006 reason slots. Suffixes are not assumed to align event-by-event across families. The authorized release must validate slot ordering, response coding, special missing values and blank-vs-No behavior before derivation.

These are respondent-level retrospective hukou/social-status candidates, not address histories, current urbanicity or environmental doses. HK001/HK005 locations are coarse county/district categories; no geography, PSU or participant values are published or geocoded. Reasons remain multi-select; blank option flags are not No, and no transition count, duration, destination or reason frequency is derived. The 2014 Life History release note states no survey weight; these data remain outside regular-wave weighted analysis pending a justified target population and design.

The generated 1,920-field DEMOGRAPHICBACKGROUNDS ledger assigns a unique disposition to every Codebook field. Following this review, the 270 hukou fields are mapped; 765 general child/family fields remain deferred for source/referent review, 90 sensitive relative-identity fields remain held, and 38 linkage/route/date/interview/release fields have explicit non-candidate dispositions.
