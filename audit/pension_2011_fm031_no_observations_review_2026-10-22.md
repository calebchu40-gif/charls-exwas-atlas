# 2011 FM031正式退休时待遇金额字段停用审计（2026-10-22）

2011基线问卷在FM011=3“先内退、后正式退休”路由下，FM031询问正式退休时（含补贴）的月待遇金额，单位为元/月；FM032是受访者不愿回答或不记得时使用的展开区间追问。

官方2011 Codebook对`fm031`明示`No Observations`。因此问卷题意只能证明该题曾被设计，不能证明该发布字段有受访者观测。目录现将`fm031`移至C类“inactive legacy questionnaire slots with no observations”，保留Codebook来源和题意用于搜索与追溯，不把它列入E/P矩阵，也不推断为零。

`fm032_a`/`fm032_b`仍单独保留为FM031的展开区间端点，但Codebook端点摘要含极端值，授权发行数据中的存储值、特殊码及区间顺序仍需核验；父字段No Observations不构成端点可用的证据。故FM032继续标记DO NOT ANALYZE，不能当作月待遇点值。FM033是不同的退休金来源字段，不受FM031的No Observations状态自动影响。

依据：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`（FM011、FM030–FM036）；`sources_official/CHARLS_2011_Codebook_extracted.txt`（fm031及fm032_a/b）。Codebook统计摘要未作为样本量或分析结果。

实现：`scripts/build_retirement_history_exposure_crosswalk.py`不再将fm031连入退休待遇金额概念；`audit/catalog_role_override_review_v1.csv`将其列为`legacy_no_observations`，由`apply_catalog_role_overrides.py`转C。
