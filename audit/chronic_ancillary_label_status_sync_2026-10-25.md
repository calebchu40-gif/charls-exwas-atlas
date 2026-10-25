# 慢病辅助表型官方答案标签状态同步（2026-10-25）

## 核查范围

核对 `audit/chronic_disease_ancillary_variable_mapping_v1.csv` 中总状态仍为“item-level value labels/routing review pending”的记录，与同一行的 `value_label_status`、已转录 `value_labels` 及来源字段一致性。共发现83项已有官方问卷/Codebook答案类别转录或选项核对记录，却仍被总状态描述为标签未核对。

## 状态修订

仅对这83项更新总状态为“官方响应类别已核对/转录；保留来源特异的路由与时间窗；发行版编码、路由分母和分析资格仍需QA”。其余112项没有明确逐项标签证据的记录保持原状态；已有 `DO NOT ANALYZE` 的禁分析状态不变。未复制Codebook频数，未推断未列出的类别或未选择选项如何存储。

## 可复现性和边界

`scripts/apply_chronic_ancillary_label_status.py` 只按行内显式标签状态与非空类别标签选择记录，要求恰好83项，覆盖变化时失败退出；已加入完整与finalization-only构建。专项测试检查目标数、限制语句、禁分析行和幂等性。本修订只纠正元数据审核进度，不代表这些字段已达到分析就绪状态。
