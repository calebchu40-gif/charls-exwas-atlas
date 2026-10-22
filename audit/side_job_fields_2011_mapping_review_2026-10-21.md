# 2011 side-job fields: route and cross-wave scope review

> **来源身份更正（2026-10-22）：**2011 FJ题组已按正式`CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`复核；旧来源路径实际指向2013随访问卷。题意、FC019=1路由和单位与原结论一致，映射脚本也已使用正确来源。

Date: 2026-10-21

## Decision

Add three wave-specific 2011 candidate concepts for the number of side jobs, hours per week at those jobs, and average monthly income from those jobs. Keep them separate from the analogous 2018 fields. Do not treat this as a harmonized repeated measure or assume a skipped response means zero.

## Official evidence

The extracted official 2011 baseline questionnaire, section FJ, states that the side-job section is asked when FC019=1 (“more than one job”). FJ001 asks how many jobs the respondent currently holds excluding the main job (1–20); FJ002 asks average hours per week at side job(s), excluding the main job (0–168); FJ003 asks average monthly income/wage from side job(s), in yuan/month. FJ004 is an unfolding bracket path for unwillingness or recall difficulty on FJ003. The 2011 codebook separately lists `fj001` Num. of Jobs Excluding Main Job, `fj002` Hours Per Week Worked Excluding Main Job and `fj003` Average Monthly Income from Side Job.

Sources: `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` lines 4975–4985 (FJ/FC019 route, count, hours, income and unfolding brackets); `sources_official/CHARLS_2011_Codebook_extracted.txt` FJ001–FJ004 entries around lines 79137–79180.

## Mapping and analysis limits

The fields are included as candidates in `audit/work_exposure_crosswalk_v1.csv`, `audit/charls_atlas_candidate_fields_v0.csv`, the concept-source crosswalk and `site-prototype/dist/work_exposures_v1.json`. Units are count, hours/week and yuan/month. FJ001–FJ003 are conditional on the multiple-job route; structural skips are not zero. Do not derive an income value from FJ004 brackets without a prespecified missing-data protocol.

2018 FJ001–FJ003 are asked on a different instrument route and explicitly exclude household agricultural work; its income/hours framing refers to the past year. The 2011 questionnaire does not state that same agricultural-work exclusion or past-year averaging qualifier. Accordingly, preserve separate 2011 and 2018 concepts and field-specific wording. Before any pooled analysis, inspect release-specific routing and observed denominators in authorized respondent data.

These are metadata candidates only; no respondent records or frequencies were analyzed.

## 2011 source-identity review (2026-10-22)

The correct baseline household questionnaire confirms that the side-job section is asked when FC019=1 (more than one current job). FJ001 counts current jobs excluding the main job (1–20); FJ002 asks average weekly hours excluding the main job (0–168); FJ003 asks average monthly side-job wage in Yuan; FJ004 is the refusal/recall bracket follow-up. The 2011 Codebook contains entries for FJ001–FJ003; this supports field identities and units, not respondent-level distributions or analytic eligibility. No cross-wave harmonization was made. The generator `scripts/build_work_exposure_crosswalk.py` already cited the correct baseline source; this update corrects the audit citation and line references.
