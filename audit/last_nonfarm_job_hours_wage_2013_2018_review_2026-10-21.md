# Last non-farm job hours and wages: 2011–2018 mapping review

> **来源身份更正（2026-10-21）：**本文旧版本引用的 `CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` 实际内容是2013随访问卷。本文涉及的2011题干或路由判断须对照正确的官方2011基线问卷复核；在复核完成前，不能把该旧摘录当作2011题意证据。处理范围及当前状态见 [`2011_questionnaire_source_identity_correction_2026-10-21.md`](2011_questionnaire_source_identity_correction_2026-10-21.md)。

Date: 2026-10-21

## Decision

Add two retrospective candidate concepts for the last non-farm job in the 2011, 2013, 2015 and 2018 waves: usual weekly hours (FL008) and monthly wage before stopping that job (FL009). These are past-job characteristics, not current employment conditions. They should not be combined into one exposure or substituted for current work-hours/income measures.

## Official questionnaire evidence

The 2011 baseline questionnaire uses the same FL008 and FL009 wording, route, range and special codes as the later waves: FL001=4 agricultural self-employment skips the non-farm branch; FL008 is asked for FL001=1/2/3 and records 0–168 usual weekly hours; FL009 is asked only for employed work (FL001=1), reports monthly wages/bonuses/subsidies before stopping, and uses 0 for no net income and 999997 for deficit. The extracted 2011 codebook has no FL008 or FL009 entry, so this wave is supported by the official questionnaire alone and its catalog status records that limit.

In the 2013 and 2015 questionnaire, FL001=4 (farmer/agricultural work) skips the non-farm employer branch; FL005–FL008 are asked for work types FL001=1/2/3. FL008 asks usual hours per week and gives a 0–168 range. FL009 is asked only for employed work (FL001=1) and asks monthly wages, bonuses and subsidies before stopping the job. The questionnaire instructs interviewers to record 0 for no net income and 999997 for a deficit. Unfolding brackets are separate fields, not replacements for FL009.

The 2018 questionnaire has the same split: FL008 applies to non-agricultural work types 1/2/3 and asks usual weekly hours; FL009 applies only to employed work (FL001=1) and asks monthly wages, bonuses and allowance before stopping. It gives the same 0 and 999997 special values. Its wording differs slightly from 2013/2015, so preserve the source wording and wave label. Agricultural self-employment (FL001=4) skips these fields.

Sources: `sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` (FL001 and FL005–FL010, around lines 7626–7651); `sources_official/CHARLS_2013_Questionnaire_extracted.txt` (FL001 and FL005–FL010, around lines 6576–6601); `sources_official/CHARLS_2015_Questionnaire_extracted.txt` (FL001 and FL005–FL010, around lines 5622–5646); `sources_official/CHARLS_2018_Questionnaire_extracted.txt` (FL001 and FL005–FL009, around lines 7187–7269); The 2013, 2015 and 2018 official codebooks list FL008 and FL009 as continuous fields; the extracted 2011 codebook entries were not located. Codebook frequencies were not copied into the atlas or treated as analytical N.

## Mapping and analysis limits

The two concepts are in `audit/work_exposure_crosswalk_v1.csv`, `audit/charls_atlas_candidate_fields_v0.csv`, the concept-source crosswalk and `site-prototype/dist/work_exposures_v1.json`. FL008 has the broader eligible non-farm job route; FL009 has the narrower employed-work route. A structural skip does not mean zero. Preserve 999997 as a source special value until release-specific data conventions are confirmed; do not treat it as a real wage. Keep unfolding-bracket variables separate unless an analysis protocol specifies how to use them.

These are metadata candidates only; no respondent records or frequencies were analyzed.
