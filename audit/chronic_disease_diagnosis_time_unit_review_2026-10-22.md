# 慢病首次诊断/知悉时间字段单位复核（2026-10-22）

2011、2013、2015、2018四轮官方CHARLS Codebook均将慢病`DA009`的两个字段组件分别标为日历年份（`da009_1_<病种>`）和诊断时年龄（`da009_2_<病种>`）。四轮各有14种疾病，合计112个唯一波次—字段；其中部分字段还按P候选和C类调整候选两种目录角色展示，因此主目录共168个角色/类别行。单位按源字段相同显示，不把重复目录角色当作新变量，也不把年与年龄合成一个连续指标。2013第15占位索引不属于14种Codebook所列病种，不套用此单位规则。

这些字段记录受访者报告的首次被诊断或本人得知患病时间，不等同于生物学发病时间；需保留问卷路由和特殊值。Codebook的摘要最小值/最大值不定义合法范围或缺失码。因它们是数值/时间单位字段而非离散回答类别，目录将审校状态标为`numeric/time unit metadata available; no discrete labels assigned`，不生成类别标签。

实现位于`scripts/build_charls_atlas_catalog.py`和`scripts/build_ep_concept_source_crosswalk.py`，并由`scripts/finalize_catalog_semantics.py`同步到系列视图。官方来源：`sources_official/CHARLS_2011_Codebook_extracted.txt`、`CHARLS_2013_Codebook_extracted.txt`、`CHARLS_2015_Codebook_extracted.txt`、`CHARLS_2018_Codebook_extracted.txt`；背景审计见`audit/chronic_disease_ancillary_mapping_review_v1.md`与`audit/chronic_disease_concept_audit_v2.md`。未读取个体回答或用Codebook频数估计样本量。
