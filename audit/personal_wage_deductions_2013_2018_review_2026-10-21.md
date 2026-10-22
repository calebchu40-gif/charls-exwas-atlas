# 个人工资扣款金额与单位选择器审计（2013–2018）

审计日期：2026-10-21。依据2013、2015、2018官方问卷和可用Codebook响应类别映射；Codebook频数没有用作样本量，未读取受访者个人记录。

## 问卷结构

`GA002_W2_1`询问上一题工资报告是否已扣除保险、个人所得税、住房公积金及其他杂费；这是理解工资金额定义的范围元数据，不是扣款额。`GA002_W2_2`及2013/2015的子选择器分别记录金额单位/形式：年人民币、月人民币、工资百分比或“无”。2018另给不知道/拒答码。所有父选择器均归C类，仅用于解释子字段和保留路由，不进入E/P关联矩阵。

## 候选数值指标

总扣款金额分别按年度、月度、工资百分比建立三个独立概念。2013/2015还分别询问所得税、各类保险、住房公积金的金额，因此这三项也按年度、月度、工资比例拆分成不同概念；2018没有相同的逐项拆分，不能跨波伪造这些分项。金额字段通过问卷对应的父选择器解释，条件性范围依赖受访者报告工资并适用扣款题。月/年金额为名义人民币，跨波比较需事先设定通胀调整基年；百分比不能与货币金额合并。

本映射不计算“净工资”，不把总扣款与收入字段自动相减，也不从“无”、跳题、拒答或未提供的子字段推断金额零值。各字段特殊缺失值、分支有效分母以及工资收入与扣款是否严格对应，须在获准的个人级数据环境进一步核验。

## 官方依据与复现

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`与`CHARLS_2013_Codebook_extracted.txt`：总扣款及所得税、保险、住房公积金的年/月/%字段和单位选择器。
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`与`CHARLS_2015_Codebook_extracted.txt`：同类结构，明确包括“无”选项。
- `sources_official/CHARLS_2018_Questionnaire_extracted.txt`：总扣款年/月/%/无及不知道/拒答选项；2018无题干支持的细分扣款候选。
- 数值映射：`scripts/build_personal_income_crosswalk.py`；范围/单位选择器：`audit/measurement_protocol_crosswalk_v1.csv`与`audit/catalog_role_override_review_v1.csv`；完整重建：`python scripts/build_ep_atlas_metadata.py`。
