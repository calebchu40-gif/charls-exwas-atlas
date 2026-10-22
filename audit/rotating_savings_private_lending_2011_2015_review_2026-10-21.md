# 轮转储蓄与私人借贷字段审计（2011–2015）

> **来源身份更正（2026-10-21）：**本文旧版本引用的 `CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` 实际内容是2013随访问卷。本文涉及的2011题干或路由判断须对照正确的官方2011基线问卷复核；在复核完成前，不能把该旧摘录当作2011题意证据。处理范围及当前状态见 [`2011_questionnaire_source_identity_correction_2026-10-21.md`](2011_questionnaire_source_identity_correction_2026-10-21.md)。

核查日期：2026-10-21。依据CHARLS 2011基线、2013/2015官方问卷及对应Codebook公开字段标签进行元数据审计；未读取个体回答，也未把Codebook频数当作有效分析分母。

2011与2013 `HC036`询问过去一年是否参加轮转储蓄/信用协会，`HC037`询问仍需偿还给该组织的金额。分别映射为参与状态与当前债务金额，不把二元参加状态当作债务额度；金额字段的路由需在授权数据中核验。

2015问卷改问过去一年是否参与“民间借贷（如标会等）”；随后`HC037`询问当前还欠民间借贷多少钱。Codebook继续将`HC036/HC037`标为轮转储蓄/信用协会。因问卷用语更宽、Codebook用语较窄，2015状态与金额均保留为单独波次概念，不自动与2011/2013合并。问卷还在HC036后出现`HC036_W3`金额槽和`HC036_W3_1`区间追问，但2015公开Codebook和本项目发布变量目录均没有`HC036_W3`这一观测字段，故不生成数据字段映射、不把文本题槽当作有数据变量。

来源：`sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`及`CHARLS_2011_Codebook_extracted.txt`；2013问卷/Codebook；`sources_official/CHARLS_2015_Questionnaire.pdf`印刷页219（PDF页225）与`CHARLS_2015_Codebook_extracted.txt`约29834–29845行。构建器：`scripts/build_personal_income_crosswalk.py`；全量重建：`python scripts/build_ep_atlas_metadata.py`。
