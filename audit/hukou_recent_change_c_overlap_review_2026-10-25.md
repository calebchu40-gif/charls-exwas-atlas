# Recent hukou-change C/E overlap review (2026-10-25)

This batch links 11 exact E/C source fields about reported hukou change since a prior interview. They are historical social-context candidates. They are not geocoded migration histories, current residence measures, or pollutant doses. The exposure field must not be used to adjust for itself; no fixed covariate set is recommended.

| Wave | Field | Candidate concept | Questionnaire and Codebook |
|---|---|---|---|
| 2013 | `bc001_w2_1` | `hukou_change_since_prior_interview` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2013 | `bc001_w2_2` | `reason_for_hukou_change_to_agricultural_since_prior_interview` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2013 | `bc001_w2_3` | `reason_for_hukou_change_to_nonagricultural_since_prior_interview` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2013 | `bc005_w2_1` | `hukou_location_change_since_prior_interview_2013` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2013 | `bc005_w2_2` | `reason_for_hukou_location_change_since_prior_interview` | CHARLS_2013_Questionnaire_extracted.txt; CHARLS_2013_Codebook_extracted.txt |
| 2015 | `bc002_w3` | `hukou_change_since_prior_interview` | CHARLS_2015_Questionnaire_extracted.txt; CHARLS_2015_Codebook_extracted.txt |
| 2018 | `bc002_w3` | `hukou_change_since_prior_interview` | CHARLS_2018_Questionnaire_extracted.txt; CHARLS_2018_Codebook_extracted.txt |
| 2015 | `bc002_w3_2` | `reason_for_hukou_type_change_since_prior_interview` | CHARLS_2015_Questionnaire_extracted.txt; CHARLS_2015_Codebook_extracted.txt |
| 2018 | `bc002_w3_2` | `reason_for_hukou_type_change_since_prior_interview` | CHARLS_2018_Questionnaire_extracted.txt; CHARLS_2018_Codebook_extracted.txt |
| 2015 | `bc002_w3_5` | `reason_for_hukou_location_change_since_prior_interview` | CHARLS_2015_Questionnaire_extracted.txt; CHARLS_2015_Codebook_extracted.txt |
| 2018 | `bc002_w3_5` | `reason_for_hukou_location_change_since_prior_interview` | CHARLS_2018_Questionnaire_extracted.txt; CHARLS_2018_Codebook_extracted.txt |

## Wave and routing distinctions

- **2013:** the status-change item is yes/no. Its reason fields are conditional on the current hukou type. The questionnaire/codebook preserve a “No change” category inside two reason fields (code 5 for the agricultural-hukou item and code 6 for the non-agricultural item); retain those as distinct route categories, not reasons and not structural skips.
- **2013 location change:** the comparison is available on the reinterview route when prior hukou location is known. The reason field follows only a “Yes” response; do not infer a reason from current location.
- **2015:** `BC002_W3` uses four nominal categories and a prior-interview time reference. The questionnaire routes `ZBC001` nonresponse to follow-up items and skips the change item; do not code that structural route as unchanged.
- **2018:** the change section is asked on reinterview (`XRType=1`); the new-interview route skips it. Type/location reason questions follow the corresponding change categories.
- Preserve each wave’s labels and routes. The 2013 binary item and 2015/2018 nominal categories are not a common numeric scale; the 2015 location-reason set has five categories while 2018 has six.

The updater verifies the exact wave, field, module, E/C roles and official Questionnaire/Codebook field-code presence, then carries reviewed response labels and caveats into the C catalogue. The 2011/2013/2015/2018 field identities and routes are recorded in [`hukou_recent_change_crosswalk_v1.csv`](hukou_recent_change_crosswalk_v1.csv). Audit rows are in [`hukou_recent_change_c_overlap_review_v1.csv`](hukou_recent_change_c_overlap_review_v1.csv). No respondent data or Codebook frequencies are reproduced.
