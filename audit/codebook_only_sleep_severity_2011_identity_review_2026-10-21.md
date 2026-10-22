# 2011 DE010–DE012睡眠情景题身份更正（2026-10-22）

此前“2011问卷未找到题干”的结论引用了误标为2011、实际内容属于2013随访的问卷文件。改用正确的CHARLS 2011基线家户问卷后，DE010–DE012均能在Sleep Domain中逐题定位：三项要求受访者评价具名假设人物过去一个月的睡眠困难，选项为None/Mild/Moderate/Severe/Extreme。它们不是受访者自身睡眠表型。

处理决定：三字段从P候选矩阵移至C类`hypothetical health anchoring vignette`测量元数据；按睡眠领域保留与其他情景题一致的1–5响应标签，不创建个人睡眠结局，也不与DE002本人睡眠困难题合并。原来的三个`codebook_only_sleep_severity_item_*`候选概念撤销。

证据：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`，Sleep Domain及DE010–DE012；`sources_official/CHARLS_2011_Codebook_extracted.txt`，de010–de012值标签。该问卷还在DE007–DE024题组说明这些是对与受访者年龄/背景相同的虚构人物的标准化评价，并通过家户内姓名性别随机化实施。值标签与题意一致。不得使用Codebook频数估计患病率或样本量。

构建：`scripts/build_health_anchoring_vignette_metadata_crosswalk.py`现包含de010–de012；`scripts/build_health_symptom_crosswalk.py`移除三项P映射；`audit/catalog_role_override_review_v1.csv`将其角色固定为C。完整构建后应验证三字段不再出现在E/P候选概念映射中，且保留C类标签。未读取受访者记录、未拟合模型。
