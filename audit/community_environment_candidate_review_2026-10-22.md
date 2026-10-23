# CHARLS community and housing environment candidate review (2026-10-22)

## Purpose and scope

This review checks whether CHARLS can contribute environment-related candidates to an NHANES-style exposome–phenome lookup. It uses only the project’s official questionnaire/codebook extracts and metadata crosswalks; it does not inspect respondent-level records or estimate associations.

The current community crosswalk contains 194 source-field mappings across 100 concepts, all from the 2011 Community module. The education-profile concept includes six exact percentage fields and six conditional `_1` bracket fallbacks; see `audit/community_education_and_context_review_2026-10-24.md`. The separate food/housing crosswalk contains repeated household and residence fields across 2011–2020. These are distinct measurement levels and must remain distinct in the site and any later analysis.

## What CHARLS actually measures

The 2011 Community Questionnaire asks a community informant to report household counts by drinking-water source (JB006) and fuel source (JB007), whether the community has central winter heating and which fuels it uses (JB008–JB009), sewerage, waste handling and toilet infrastructure (JB010–JB014), electricity coverage and supply (JB017/JB020/JB021), and industrial pollution ratings and distance (JB018/JB019/JB027). The water and fuel items are village/community household counts, not the sampled respondent’s household use. JB019 and JB027 are explicitly village-only CAPI routes. These details are in `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt` around printed questionnaire pp. 7–9 (PDF pp. 10–12).

The same questionnaire asks the prior calendar year’s community-reported minimum/maximum temperature and rainy/snowy days (JA039–JA041; printed p. 3, PDF p. 6). These are informant estimates, not linked weather-station observations. Natural-disaster histories are also community-informant reports and should stay separate by event and response component.

The household Housing/Housing_Characteristics module supplies a different class of candidates: residence-level toilet access/type, running water, heating and fuel, cooking fuel, gas/electricity access, and later-wave air-cleaner presence, indoor cleanliness/temperature, and water-treatment items. The 2020 questionnaire places I016 (tap water), I017 (in-house shower/bath type), I018 (gas supply), I019 (heating), I020 (heating source), I021 (cooking fuel), I024 (air cleaner), and I029 (waterworks treatment) in the household income/housing section. The 2020 item instructions allow interviewer recording only when the interviewer is in the home and clearly knows the answer; otherwise ask the respondent. Air-cleaner presence is not evidence of use, filtration performance, or measured indoor pollution. I029 includes “Don’t know,” which must not be recoded as “No.” See `sources_official/CHARLS_2020_Questionnaire_English_extracted.txt` around pp. 86–88.

## Interpretation and harmonization rules

1. Keep respondent, household/residence, and community-informant levels explicit in every search result. A household/community association is not an individual exposure association unless the linkage and estimand justify that interpretation.
2. Keep every source field visible when a concept groups several questionnaire components. Community water-source counts, fuel counts, weather measures, and industrial pollution indicators are different fields and should not be collapsed into an ordinal score or treated as a dose without a prespecified validated construction.
3. Do not treat community-level household counts as percentages unless a compatible denominator is documented and verified. Do not derive respondent exposure from community counts by ecological assignment alone.
4. Preserve conditional routes and structural missingness. For the V-only community items and selected facility routes, blank/unasked is not a negative response.
5. Preserve nominal cooking/heating fuel categories and wave-specific codes. “No cooking,” “no heating,” “heating provided,” and “other” are meaningful categories where present; they are not numeric severity levels.
6. Treat housing services and indoor observations as proxies, not measured contaminants. CHARLS does not provide NHANES-like repeated panels of blood/urine environmental chemicals in these modules.
7. The community module is 2011-only in the current documented crosswalk. Any later-wave community linkage requires a documented official file, release, and stable identifiers; do not silently carry forward the 2011 value.

## Implication for the atlas

CHARLS can support a broad Chinese household/community environment and social-context discovery layer, but its strongest environment-related candidates are housing services, cooking/heating fuel, sanitation, community infrastructure, self-reported community pollution, weather, and disaster context. They are not a substitute for measured chemical exposome data. Keep the website in a metadata-only state until release eligibility, linkage keys, survey design, item-level denominators, and analysis permission are independently confirmed. The present crosswalks are candidate inventories, not approved analysis variables or evidence of any association.

## Verification commands

```powershell
python scripts/build_community_exposure_crosswalk.py
python scripts/build_food_environment_crosswalk.py
```

The source crosswalk and this audit should be updated together when item wording, wave coverage, or route interpretation changes.

## Drinking-water and fuel count units (2026-10-24)

The official 2011 Community Questionnaire, Part B p.7 (PDF p.10), says JB006 asks how many households used each drinking-water source at the end of calendar year 2010 and labels the response unit as households. JB007 asks the analogous household count by fuel source. The questions list several sources without defining them as mutually exclusive and provide no total-household denominator in those tables. The public catalogue therefore labels JB006_1–JB006_8 and JB007_1–JB007_6 as `households`, records the 2010 reference period in the concept caveat, and does not convert the counts to percentages or assign a single household-level source. This must remain a community-informant context measure, not an individual exposure or measured water/fuel quality value. Source extracts: `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt` and `sources_official/CHARLS_2011_Codebook_extracted.txt`; no Codebook frequencies or extrema were copied.

## Questionnaire-anchor reconciliation for industrial pollution (2026-10-22)

The Codebook value labels for JB018 and JB019 say `Poor`, `Fair`, `Good`, and `Very good`, which can reverse the apparent direction if read literally as pollution severity. The official Community Questionnaire supplies the substantive bilingual anchors: 1=`Very severe` (很严重), 2=`Some pollution` (有一些), 3=`Almost none` (基本没有), and 4=`Completely absent` (完全没有). The website lookup labels now use those questionnaire anchors and explicitly state that higher codes indicate less reported pollution. JB019's village-only route remains visible. The raw Codebook labels are retained in source evidence; frequencies were not copied. Regression coverage checks the override and source anchors.
