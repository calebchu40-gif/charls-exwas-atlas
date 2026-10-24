# 协变量可用性汇总的公开披露审阅（2026-10-24）

## 审阅范围

审阅了公开仓库中的 `audit/covariate_candidate_availability_v1.csv`、其生成脚本 `scripts/summarize_covariate_candidates.py`、项目许可摘要和 `.gitignore`。CHARLS 官方用户条款允许发布不暴露参与者身份的学术统计/分析结果；项目许可审计见 `audit/charls_data_access_license_review_2026-10-24.md`。

## 结论与边界

该 CSV 仅含波次、候选协变量概念/来源字段、状态、总体行数、字段非空数量，以及两条明确标记为“未最终年龄”的年份差候选摘要。没有受访者 ID、逐人记录、类别响应频数或地理细分。它用于说明数据准备与缺失覆盖，不是暴露—表型配对样本量、分析资格判定或关联结果。年份差候选值不得作为正式年龄或模型结果引用。

复跑生成脚本后，公开 CSV 与本机受控 QA 输出的 40 条概念—波次记录及其汇总字段一致。私有的 `covariate_candidate_value_counts_v1.csv`、配对完整样本量及其他数据派生 QA 仍由 `project_paths.py` 写入 `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs`；它们不得进入 Git 或 Pages。

已扩展 `tests/test_repository_privacy_inventory.py`：拒绝追踪值频数、配对完整样本量及指定私有 QA 文件，并锁定公开可用性汇总的字段白名单；任何候选值摘要只能出现在明确标注为未最终年龄的行。该检查不替代 CHARLS 的逐项披露审查，也不批准任何协变量或统计模型。
