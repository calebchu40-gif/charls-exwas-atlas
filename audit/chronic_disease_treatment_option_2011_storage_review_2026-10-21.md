# 2011糖尿病、癌症和中风治疗选项字段身份复核

只审阅CHARLS 2011 Baseline Household Questionnaire与Codebook公开文本，没有读取个人级回答。

- 糖尿病治疗 `DA014` 条件为DA007=3，询问当前中药、西药、胰岛素及“以上都没有”。癌症 `DA018` 条件为DA007=4，询问过去两年治疗选项；中风 `DA019` 条件为DA007=8，询问当前中风/并发症治疗。
- 依据Codebook将缺失的10个option字段（DA014S3/S4、DA018S3–S6、DA019S3–S6）映射至已经存在的疾病特异治疗候选概念，作为可检索源字段；每项保留原始选项索引和独立字段，不新增治疗概念，也不把索引拆成二元答复。
- 不能用Codebook频数还原个体值。Codebook文本中这些字段以“3=胰岛素”“4=无上述项”等选项索引呈现，并列出汇总频数；问卷则称逐项询问1=是、2=否。现有公开元数据无法确认已发布个体文件的字段存储方向、未选项编码或合法分析分母，因此这些新链接均标记 `DO NOT ANALYZE`，直到获准发布数据/变量说明完成验证。
- 源映射由 `scripts/build_chronic_disease_ancillary_crosswalk.py` 自动生成，值标签只作为选项身份索引，不是受访者回答类别。疾病路由限制保留在 `audit/chronic_disease_ancillary_variable_mapping_v1.csv` 和网站字段目录。
