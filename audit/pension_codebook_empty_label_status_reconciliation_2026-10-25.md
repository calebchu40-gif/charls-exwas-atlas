# 养老金 Codebook 无离散标签字段状态回写修正（2026-10-25）

## 发现

逐键比对 `pension_exposure_variable_mapping_v1.csv` 与 `pension_codebook_value_labels_v1.csv` 的1,159条波次—字段记录，发现类别提取审计本身已区分字段在官方 Codebook 中定位为连续/计数/无离散菜单，与标题匹配不足/响应标签未定位；但生成器只将非空类别标签写回源映射，导致无离散类别字段被统一误写为“响应标签未找到”。其中，1,051项的 Codebook 审计状态为“field located; continuous/count or no categorical labels”，52项为“response label not located or title match insufficient”。

## 修正

`build_pension_codebook_value_labels.py` 现在检查两份表的波次—字段键完整且唯一后，将完整的 `value_label_status` 和来源引用写回源映射，即使 `value_labels` 为空也保留字段定位结果。值标签文本不由该状态同步函数修改；因此不会从频数或数值摘要推造类别。另有23项已有离散类别标签的候选状态通过独立、受限的 `apply_pension_label_status.py` 同步，仍保留发行版编码、路由和分析资格限制。

在这次回写基础上，后续逐域审核覆盖了17项状态并给出更具体结论：1项FN069得到官方Yes/No码核对，12项2011养老金括区端点及4项缴费括区端点有比通用解析状态更具体的来源审核。最终源映射为1,046项标准“Codebook字段已定位但无离散类别”状态、40项标题匹配不足/答案类别未定位状态及17项更具体的逐域状态；Codebook解析审计表仍保存原始的1,051/52分类作为可复现解析结果。差异是更具体的审核叠加，不是字段漏失。

## 解释边界

“Codebook字段已定位、无离散类别菜单”不代表特殊缺失值、值域、单位或分析样本资格已验证。52项标题匹配不足仍待人工回查。该修正只改善来源审计状态，不增加暴露概念，不拟合关联模型，也不处理参与者级记录。
