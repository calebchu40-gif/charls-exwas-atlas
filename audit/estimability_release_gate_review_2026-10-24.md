# 逐对可估计性审查放行门槛

日期：2026-10-24  
范围：结果schema与放行验证规则；不包含CHARLS逐对数据审查或任何正式模型。

## 为什么需要这一门槛

`svy` 0.35.0 的隔离合成审计发现，一个只有两个事件的二分类结局fixture在暴露两组均有事件时可返回有限系数、标准误和P值，且没有引擎警告。该现象只能说明“有限输出且无警告”不是足够的模型放行条件；它不提供 CHARLS 的事件支持阈值，也不验证真实调查设计下的稀少事件推断。

## 已落实规则

- `audit/EXWAS_result_schema_v2.csv` 新增必填 `estimability_review_status`，取值为 `pending`、`reviewed_pass`、`blocked_support`、`blocked_separation`、`blocked_design` 或 `unresolved`。
- 新增条件字段 `estimability_review_id`。仅 `reviewed_pass` 可以附引用；成功结果必须同时有 `reviewed_pass` 和审查编号。
- `scripts/validate_exwas_result_table.py` 强制执行上述约束。验证器只核查审查状态和引用是否齐全，不会自行判断模型是否足够稳定。
- 中文分析规约要求逐对/逐对比留存受控审查：规则版本、类别支持情况、分离和拟合诊断、权重与设计自由度/有效样本量、模型复杂度及审查结论。
- Added the blank controlled-record checklist [`estimability_review_record_template_v1.md`](estimability_review_record_template_v1.md); only a sanitized status/reference may enter public result metadata.
- 不制定没有预先方法依据或外部验证的通用事件数/样本量硬阈值。公开结果不得通过审查编号暴露小单元或可回推的支持细节；审查明细需留在受控本地环境。

## 验证

新增成功行缺失审查状态或引用时的拒绝测试，并验证补齐为 `reviewed_pass` 及引用后才通过。专门验证器测试13项通过；全仓库 unittest 268项通过。该规则是软件放行检查，不代表现有CHARLS变量或模型已通过审查。当前正式关联模型数和实际分析N仍为0。
