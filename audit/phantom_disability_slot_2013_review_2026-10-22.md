# 2013 第六个残疾槽位复核

2013 Codebook包含`zda005_6_`（Having Disability of），但官方问卷DA005只定义五种残疾：躯体残疾、脑损伤/智力障碍、视力、听力、言语障碍。Codebook对额外槽位只列13条“No”，没有“Yes”类别。这不足以支持第六种残疾表型，不能把“No-only”源槽当作常规结局。

因此该字段保留在来源目录中，角色设为C类质量/测量元数据，明确排除E/P矩阵。字段级旧审计行仍保留于`unmapped_phenotype_review_v1.csv`作为历史判断记录；当前目录不再将其计为未映射P。目录构建的专用规则与覆盖记录分别见`../scripts/apply_catalog_role_overrides.py`和`catalog_role_override_review_v1.csv`。

证据：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`，DA005题干与五类选项；`sources_official/CHARLS_2013_Codebook_extracted.txt`，`zda005_6_`表仅列2=No、13条记录。未读取受访者微观记录。
