# 继承经历、来源及金额字段审计（2011、2013）

审计日期：2026-10-21。依据CHARLS官方2011/2013问卷和Codebook逐题映射；未读取微观记录，也不将Codebook频数用作分析样本量。

两波均先问是否曾继承（HD005）。回答是后，询问所有继承财产在继承时的总价值（HD006），并通过可多选HD008选项询问来源：父母、岳父母/公婆、子女、亲戚、其他。HD008s1–s5映射到一个“继承来源类别”概念，逐字段保留来源选项且说明非互斥；底层0/1、缺失或未选项编码须由获准个体数据验证。回答无继承者会跳过金额与来源题，结构性未问不是0或否。

HD009记录最大一笔继承发生年份；HD010记录这笔最大继承在发生时的金额。它们与HD006全部继承财产的累计历史价值含义不同。金额都是事件发生时的名义人民币，不是访谈时当前财富；跨年份分析须预设通胀调整方式。HD007和HD011分别是总额/最大一笔金额在拒答或记忆困难时的区间追问，不以区间中点替代准确值。HD009具体年月/特殊值、各金额特殊缺失码和真实分析分母待在获准数据环境核验。

## 官方依据与复现

- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`及`CHARLS_2011_Codebook_extracted.txt`（2011 HD005–HD011）。
- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`及`CHARLS_2013_Codebook_extracted.txt`（2013 HD005–HD011）。
- 可复现规则：`scripts/build_personal_income_crosswalk.py`；完整重建：`python scripts/build_ep_atlas_metadata.py`。
