# 2013 GA004 个体转移收入单位选择字段复核（2026-10-22）

## 结论

2013 个体收入模块的 `ga004_1_`（养老金）、`ga004_3_`（养老金补贴）和 `ga004_9_`（其他收入来源）是回答单位选择字段。官方 Codebook 对这些字段的标签为 `1 Yuan/Year`、`2 Yuan/Month`；金额分别储存在 `ga004_1_1_`/`ga004_2_1_`、`ga004_1_3_`/`ga004_2_3_`、`ga004_1_9_`/`ga004_2_9_`。实际是否领取另由 GA003 来源选择题表达。

因此，三个父字段保留在目录中作为 C 类测量/路由元数据，不进入 E/P 关联矩阵。配对的年金额和月金额子字段仍使用 `individual_transfer_income_source_amount` 概念，并按原字段单位保留；不得只凭单位选择器自动年化、月化或把不同单位的原始金额相加。未读取任何受访者记录，也未根据 Codebook 的汇总频数推断关联结果。

## 官方依据

- `sources_official/CHARLS_2013_Codebook_extracted.txt`，个体收入第1088–1092页：GA004父字段的值标签为年/月份；年、月金额是分开的连续金额字段。父字段与金额组件的 Codebook 观测数不同，说明不能把父字段当作数值金额本身。
- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`，个体收入 GA003–GA004 路由：先记录来源，再询问来源对应金额及其报告单位。
- `audit/individual_transfer_income_crosswalk_v1.csv` 已把来源对应金额组件映射到共同的源特异转移收入金额概念，并明确保留原单位和来源项目。

## 目录处理

在 `audit/catalog_role_override_review_v1.csv` 增加三个精确波次字段覆核规则，标记 `individual_transfer_income_unit_selector`。生成器将其转为 C 类“个体转移收入金额单位选择器”，展示 `1=元/年；2=元/月`，并明确排除出 E/P 矩阵。该处理只作用于2013对应父字段，不覆盖其他波次同名字段或金额子字段。
