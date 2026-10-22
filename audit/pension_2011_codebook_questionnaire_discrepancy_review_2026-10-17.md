# 养老金2011问卷/代码本码值差异核查（2026-10-17）

> **来源身份更正（2026-10-21）：**本文旧版本引用的 `CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` 实际内容是2013随访问卷。本文涉及的2011题干或路由判断须对照正确的官方2011基线问卷复核；在复核完成前，不能把该旧摘录当作2011题意证据。处理范围及当前状态见 [`2011_questionnaire_source_identity_correction_2026-10-21.md`](2011_questionnaire_source_identity_correction_2026-10-21.md)。

## 结论

Harmonized CHARLS D将Wave 1变量`FN024`列为养老金参保字段，支持把代码本字段`fn024`定位到该题目家族；原始基线问卷将条件性问题标为`FN022_w2`。变量身份有官方对照，但代码本与问卷的答案编码仍存在冲突。目录保留候选Concept ID `pension_past_basic_plan_participation_when_not_currently_enrolled`，状态标为“DO NOT ANALYZE”。候选只用于检索和审计留痕，不能据此重编码或进入关联模型。

## 官方材料证据

- 2011基线问卷第194页：`FN006_w2`问当前是否参加政府/事业单位养老金或企业职工基本养老保险；回答“都没有”(4)时跳至`FN022_w2`。
- 2011基线问卷第197页：`FN022_w2`题干说明受访者刚报告当前未参保，追问此前是否参加过；选项为1=政府和事业单位、2=企业职工基本养老保险、3=两种都参加过、4=两种都没有。
- 2011官方代码本第926页：字段`fn024`标签为“Enrolled in Pension”；代码为1=政府和事业单位养老金、2=企业基本养老保险、3=No，代码本摘要计数为465、340、14,199，总计15,004。
- Harmonized CHARLS D的Section J把Wave 1 `FN024`列为养老金参保变量，并概述Wave 1的条件路径：有工作经历、尚未办理退休或内退的受访者中，按问卷路由询问是否参加政府/事业单位或企业基本养老保险；回答是后再问养老保险关联工作单位。

问卷题号与分析数据变量名不同，但Harmonized CHARLS D提供了其属于同一Wave 1题目家族的证据。仍未解决的是答案类别：代码本“3=No”与问卷“3=两种都参加过、4=两种都没有”存在实质差异。不能自动把码3重编码为未参加，也不能把问卷码3视为否。

另一个容易混淆的编号是代码本`fn035`“What do You Plan to Do”，而基线问卷`FN035_w2`题干为本人和雇主每月合计缴费金额。变量家族和题干不同，不互相映射，直至数据版本对照能解释差异。

## 对目录与分析的处理

- `fn024`纳入为条件性候选指标，清楚显示题目路由和问卷/代码本值码冲突；此项必须排除在正式分析之外，直到CHARLS发布版本的准确存储码和标签得到确认。
- 不根据`fn024`近似题号推断其与其他波次字段一致；2013/2015/2018题目需逐波独立审核。
- `fn035`与`FN035_w2`保持分开；未确认前不连接代码本“计划安排”与问卷“合计月缴费金额”。
- 本轮只使用公开问卷、代码本与Harmonized CHARLS D变量目录；未读取受访者级数据或估计关联。代码本频数仅用于定位冲突。

## 来源

- `sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`：第194、197页附近，`FN006_w2`、`FN022_w2`。
- `audit/CHARLS_2011_Codebook_extracted.txt`：第926页附近，`fn024`；第928页附近，`fn035`。
- [CHARLS官方2011基线资料页](https://charls.pku.edu.cn/en/Data/a2011_CHARLS_Wave1__Baseline_.htm)：列出用户指南、代码本及2013-03-12更新的养老金模块。
- [Harmonized CHARLS D, Section J](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/harmonized_charls/application/Harmonized_CHARLS_D.pdf)：Wave 1变量列表和路由摘要。
- 未映射家族统计：`audit/unassigned_catalog_series_review_v1.md`；目录源字段：`audit/charls_atlas_candidate_series_v0.csv`。
