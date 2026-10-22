# 2015年GA004无观测单位槽位审计

更新：2026-10-22。2015 Codebook将旧式年度/月份拆分槽位`ga004_1_1_`–`ga004_1_9_`和`ga004_2_1_`–`ga004_2_9_`逐项标为“No Observations”。同一份Codebook为本波实际转移收入列出`ga004_1_`–`ga004_9_`等现行金额字段；不能把没有观测的旧单位组件当作零收入或额外收入来源。

目录保留18个字段名供版本核对，但从自动E候选改为C类“无观测旧问卷槽位”，排除E/P矩阵。对应字段的代码本标签保留为检索来源，未复制频数/统计值。此处理仅依据发布Codebook，不声称本地存在或检查了个体数据。

来源：`sources_official/CHARLS_2015_Codebook_extracted.txt`，GA004字段段落约第29657–29689行；规则见`audit/catalog_role_override_review_v1.csv`（`legacy_no_observations`）及` scripts/apply_catalog_role_overrides.py`。
