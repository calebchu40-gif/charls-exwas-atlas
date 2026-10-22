# 家庭财务回答者字段的角色复核（2026-10-22）

## 结论

2018 `ga000_w4`（Financial Respondent）与2020 `gb001`（Family Financial Respondent）用于选择/记录家庭财务问题的回答者。两者描述数据由谁报告，不是家庭资源水平或个人暴露，现由自动E候选改为C类“家庭财务回答来源”元数据，并通过`household_financial_respondent_metadata`概念保留在可检索目录中。它们不进入E/P关联矩阵。

2018 Codebook为`ga000_w4`列出家庭成员名槽以及97/98特殊码；这些码的具体语义仍应以实际获批发行字典确认，因此未将频数表抄成值标签。2020问卷明确GB001从家庭成员列表中选取财务回答者，并列出1–25家庭成员、26主要受访者、27主要受访者配偶；Codebook的频数仅用于核对字段身份，未作样本统计解释。

## 来源与实现

- 2018问卷与Codebook：`sources_official/CHARLS_2018_Questionnaire_extracted.txt`、`sources_official/CHARLS_2018_Codebook_extracted.txt`。
- 2020英文问卷与Codebook：`sources_official/CHARLS_2020_Questionnaire_English_extracted.txt`、`sources_official/CHARLS_2020_Codebook_extracted.txt`。
- 映射进入`audit/measurement_protocol_crosswalk_v1.csv`；E→C精确波次角色修正在`audit/catalog_role_override_review_v1.csv`登记，并由`scripts/apply_catalog_role_overrides.py`应用。
- 没有读取受访者级回答，没有推导财务回答者身份、家庭成员关系或任何关联结果。

## 使用边界

家庭层级收入/资产结果解释时可记录回答者来源，或在有预先分析计划时用于报告来源差异/敏感性分析。不要将这些字段当作SES暴露，也不要因家庭财务回答者选择方式而推断个人特征。2018特殊码在发行字典核实前保持未标注。
