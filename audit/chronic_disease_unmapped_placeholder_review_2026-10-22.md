# 慢病剩余字段占位/路由元数据复核

2026-10-22，按官方2013、2018问卷和相应Codebook逐项复核原目录中34条未连接P概念的字段。结论是这些字段不能作为独立表型保留：

- 2013 `ZDA008`在上一轮问卷中只对疾病索引1（高血压）、5（慢性肺病）、11（情绪/精神问题）定义既往自知问题；这三项已有独立慢病自知Concept映射。其余15个发布槽在Codebook中为No Observations或仅有“No”而无“Yes”，没有问卷定义的有效正向构念，转C类源占位/质量元数据。
- 2018 `ZDA009[i]`只表示受访者上一轮是否回答过“首次诊断或本人知晓时间”问题，不代表疾病状态，也不携带首次诊断/知晓时间。2018官方问卷前载定义和Codebook字段标签一致；14个槽转C类答题历史/路由元数据。
- 2013额外疾病索引15不在DA007官方14病种列表中。`DA007_W2`验证/医生告知字段及`DA009`父格式、年龄、年份字段均保留为C类未定义索引占位项，不从问卷相邻病种借用含义。

字段仍可按原码搜索和追溯，但排除于E/P矩阵。旧逐码复核记录`unmapped_phenotype_review_v1.csv`作为历史决策日志保留；当前目录重算应显示零条未映射P概念字段。精确波次—字段—角色更正见`catalog_role_override_review_v1.csv`的`chronic_disease_auxiliary_metadata`记录，生成规则见`../scripts/apply_catalog_role_overrides.py`。

来源：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`（DA007 14病种、ZDA008仅1/5/11、DA009路由）；`sources_official/CHARLS_2013_Codebook_extracted.txt`（ZDA008逐字段No Observations/仅No，以及索引15字段）；`sources_official/CHARLS_2018_Questionnaire_extracted.txt`（ZDA009上一轮答题状态定义）；`sources_official/CHARLS_2018_Codebook_extracted.txt`（ZDA009字段标签）。未读取受访者微观记录。
