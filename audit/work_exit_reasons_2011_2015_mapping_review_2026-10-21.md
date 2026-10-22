# FL020 last-work exit reasons: 2011–2015 option-level mapping review

> **来源身份更正（2026-10-21）：**本文旧版本引用的 `CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` 实际内容是2013随访问卷。本文涉及的2011题干或路由判断须对照正确的官方2011基线问卷复核；在复核完成前，不能把该旧摘录当作2011题意证据。处理范围及当前状态见 [`2011_questionnaire_source_identity_correction_2026-10-21.md`](2011_questionnaire_source_identity_correction_2026-10-21.md)。

Date: 2026-10-21

## Decision

Add 16 option-specific candidate concepts for the FL020 “check all that apply” reasons for leaving the last work activity, with one source field per option in 2011, 2013 and 2015. Keep the options as separate, potentially nonexclusive indicators; do not convert them into a single categorical reason. Exclude 2018 FL020_W4 because its item wording and response set changed.

## Official evidence and limits

The official 2011 baseline questionnaire says not to probe and to select all applicable options. Its prompt covers leaving an employer, stopping a business or farm work, or ending unpaid work for a family business. The 16 options are business closed, quit, laid off, fired, went to school, went abroad, health reason, family reason, transfer, sent to countryside for manual labor, started local off-farm work, went to work away from home, better local job, better job elsewhere, retired, and other. The 2013 and 2015 questionnaires list the same 16 FL020s1–FL020s16 fields and instruct interviewers to check all that apply. The 2013 and 2015 codebooks list those option-specific fields and response-option text; reported frequencies are not used as sample sizes or answer-label evidence.

2018 FL020_W4 asks why the respondent is no longer working at the prior job and uses a shorter, different response set; it is not mapped into these 16 concepts. The `Other` follow-up free text (FL020_1) is not included as an atlas exposure.

Sources: `sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` (FL020 around lines 7740–7758); `sources_official/CHARLS_2013_Questionnaire_extracted.txt` (FL020 around lines 6678 onward); `sources_official/CHARLS_2015_Questionnaire_extracted.txt` (FL020 around lines 5708–5726); the 2013/2015 official codebook FL020s1–s16 entries.

## Mapping and analysis limits

Option-specific fields are linked in `audit/work_exposure_crosswalk_v1.csv`, the candidate field catalog, the concept-source crosswalk and `site-prototype/dist/work_exposures_v1.json`. The unit is an option-specific multi-select field; released-data selected/unselected/missing storage must be verified before analysis. The eligible FL020 route and respondent's last-work context must be respected. These are candidate mappings only; no respondent records or codebook frequencies were analyzed.
