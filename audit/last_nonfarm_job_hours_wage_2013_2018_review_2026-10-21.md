# Last non-farm job hours and wages: 2011–2018 mapping review

> **来源身份更正（2026-10-22）：**已用正式2011基线家户问卷核对FL001非农工作分支、FL008工时范围/核查及FL009工资定义、路由和特殊值。2011对应摘录见`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`；2011 Codebook未检出FL008/FL009，故该波依据明确限于问卷。

Date: 2026-10-21

## Decision

Add two retrospective candidate concepts for the last non-farm job in the 2011, 2013, 2015 and 2018 waves: usual weekly hours (FL008) and monthly wage before stopping that job (FL009). These are past-job characteristics, not current employment conditions. They should not be combined into one exposure or substituted for current work-hours/income measures.

## Official questionnaire evidence

For 2011, FL001=4 skips to FL018; FL005–FL008 are asked for non-farmer work types FL001=1/2/3. FL008 asks usual weekly hours, records a 0–168 range, and prompts verification above 80. FL009 is asked only for employed work (FL001=1), asks monthly wages/bonuses/subsidies before stopping, and instructs 0 for no net income and 999997 for a deficit; it also prompts verification below 100. Unfolding brackets follow only if the respondent is unwilling or does not remember. The extracted 2011 codebook has no FL008 or FL009 entry, so this wave is supported by the official questionnaire alone and its catalog status records that limit.

In the 2013 and 2015 questionnaire, FL001=4 (farmer/agricultural work) skips the non-farm employer branch; FL005–FL008 are asked for work types FL001=1/2/3. FL008 asks usual hours per week and gives a 0–168 range. FL009 is asked only for employed work (FL001=1) and asks monthly wages, bonuses and subsidies before stopping the job. The questionnaire instructs interviewers to record 0 for no net income and 999997 for a deficit. Unfolding brackets are separate fields, not replacements for FL009.

The 2018 questionnaire has the same split: FL008 applies to non-agricultural work types 1/2/3 and asks usual weekly hours; FL009 applies only to employed work (FL001=1) and asks monthly wages, bonuses and allowance before stopping. It gives the same 0 and 999997 special values. Its wording differs slightly from 2013/2015, so preserve the source wording and wave label. Agricultural self-employment (FL001=4) skips these fields.

Sources: `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` (FL001 and FL005–FL010, lines 5024–5072); `sources_official/CHARLS_2013_Questionnaire_extracted.txt` (FL001 and FL005–FL010, around lines 6576–6601); `sources_official/CHARLS_2015_Questionnaire_extracted.txt` (FL001 and FL005–FL010, around lines 5622–5646); `sources_official/CHARLS_2018_Questionnaire_extracted.txt` (FL001 and FL005–FL009, around lines 7187–7269); The 2013, 2015 and 2018 official codebooks list FL008 and FL009 as continuous fields; the extracted 2011 codebook entries were not located. Codebook frequencies were not copied into the atlas or treated as analytical N.

## Mapping and analysis limits

The two concepts are in `audit/work_exposure_crosswalk_v1.csv`, `audit/charls_atlas_candidate_fields_v0.csv`, the concept-source crosswalk and `site-prototype/dist/work_exposures_v1.json`. FL008 has the broader eligible non-farm job route; FL009 has the narrower employed-work route. A structural skip does not mean zero. Preserve 999997 as a source special value until release-specific data conventions are confirmed; do not treat it as a real wage. Keep unfolding-bracket variables separate unless an analysis protocol specifies how to use them.

These are metadata candidates only; no respondent records or frequencies were analyzed.
