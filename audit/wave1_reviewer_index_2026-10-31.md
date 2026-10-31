# Wave 1 预分析审阅索引：历史快照（2026-10-31）

> **状态更新（2026-10-31）：**本索引记录模型运行前拟交审的事项，不是当前任务队列。用户已确认官方来源及使用授权、选择方案 A，并授权在私人服务器运行。K=150/K=90 的240项主分析、三套240项敏感性及48项尿酸肾功能敏感性已完成；当前结果整理和公开汇总表工作见[`EXECUTION_PLAN_ACTIVE_2026-10-31.md`](EXECUTION_PLAN_ACTIVE_2026-10-31.md)。

**给独立审阅人：按这张表从上到下签字即可；每一行都指向可核对的具体文件。**
凡标"已关闭"的，是有可复现证据的技术门；凡标"待裁决"的，是需要人或方法判断的门。

---

## A. 已关闭（有证据，可复核）

| # | 门 | 证据 | 状态 |
|---|---|---|---|
| A1 | Wave 1 四件套来源身份 | `private/incoming_2011_official/intake_manifest.json`（2026-10-30 04:15 UTC，含用户确认与逐文件 SHA-256） | ✅ 已记录 |
| A2 | 农历↔公历转换是否与官方一致 | 官方 `.mmat` 与 `lunardate 0.1.4` 逐格对照：普通 49,949 + 闰月 1,521 = **51,470 映射，0 处不一致**；[`lunar_conversion_lookup_and_parity_2026-10-31.md`](lunar_conversion_lookup_and_parity_2026-10-31.md) | ✅ 已验证 |
| A3 | 项目侧转换实现与许可 | 改用 **MIT 官方查表**（`scripts/lunar_lookup.py`，7 项测试含全表往返）；GPLv3 的 lunardate 仅外部交叉验证，不 vendor | ✅ 已实现 |
| A4 | 引擎输出 → 正式结果契约 | `scripts/engine_to_schema_v3.py`，要求已复核溯源、失败即停，出口跑生产校验器；10 项测试 | ✅ 已实现 |
| A5 | 引擎与 K=150/90 执行器设计语义 | 无官方分层列时**强制**在结果说明里写 `limitation:`；8 项测试 + [`engine_executor_consistency_2026-10-31.md`](engine_executor_consistency_2026-10-31.md) | ✅ 已对齐 |
| A6 | 15 项血液结局的单位与官方参考统计 | [`wave1_outcome_rule_review_packet_2026-10-31.md`](wave1_outcome_rule_review_packet_2026-10-31.md)（Table 4/5 逐项） | ✅ 已彙整 |
| A7 | 试点 105 项不新增假设 | [`wave1_pilot105_freeze_draft_2026-10-31.md`](wave1_pilot105_freeze_draft_2026-10-31.md)：7×15，ID 全部来自 K=150 登记表；7 项测试 | ✅ 已派生 |

## B. 待裁决（需要人或方法判断）

| # | 门 | 需要你决定什么 | 材料 | 影响 |
|---|---|---|---|---|
| **B1** | **方差方案** | 批准哪种近似：①无 strata + WR Taylor（已选 A 方案）②县级前缀作最高层簇 ③两者并存（主 + 敏感性） | [`wave1_variance_review_recommendation_2026-10-30.md`](wave1_variance_review_recommendation_2026-10-30.md)、[`engine_executor_consistency_2026-10-31.md`](engine_executor_consistency_2026-10-31.md)、[`wave1_design_cluster_support_diagnostic_2026-10-30.md`](wave1_design_cluster_support_diagnostic_2026-10-30.md) | 决定所有系数能否报告 SE/CI |
| **B2** | **目标估计量与年龄域** | 主分析是"45+ 域"还是"完整血检目标框"；配偶 <45 如何处理 | [`wave1_pilot105_freeze_draft_2026-10-31.md`](wave1_pilot105_freeze_draft_2026-10-31.md)、[`lunar_conversion_lookup_and_parity_2026-10-31.md`](lunar_conversion_lookup_and_parity_2026-10-31.md) | 决定分母与可解释人群 |
| **B3** | **空腹编码** | 三选一：A 授权聚合诊断 / B 向 CHARLS 索取编码 / C 维持阻断 | [`wave1_fasting_code_review_packet_2026-10-31.md`](wave1_fasting_code_review_packet_2026-10-31.md)；核验脚本 `scripts/audit_wave1_fasting_code_distribution.py`（**已备好、未运行**） | 决定 14 项代谢结局能否进入 |
| **B4** | **主模型是否冻结** | 是否把 M1（年龄、年龄²、性别）定为主模型；M0/M2 作为敏感性 | 登记表 `primary_model_id` 仍为 `not_frozen` | 决定 91 项的计算口径 |
| **B5** | **105 项与 K=240 的多重检验关系** | 确认"试点不单独发布 q 值，最终在 K=240 全族重算" | [`wave1_household_environment_pilot_execution_design_2026-10-30.md`](wave1_household_environment_pilot_execution_design_2026-10-30.md)、[`wave1_pilot105_freeze_draft_2026-10-31.md`](wave1_pilot105_freeze_draft_2026-10-31.md) | 决定结果能否称为"发现" |
| **B6** | **两处结局范围不一致** | `qc1_vb004`（血红蛋白）、`newtg`（甘油三酯）观测框与官方表不一致：保留 / 按官方做敏感性 / 排除 | [`wave1_outcome_rule_review_packet_2026-10-31.md`](wave1_outcome_rule_review_packet_2026-10-31.md) §3 D2 | 影响 2 项结局 |
| **B7** | **右偏指标是否变换** | CRP、甘油三酯、肌酐、BUN、HbA1c：主分析 log 还是原尺度 | 同上 §3 D3 | 影响效应尺度解释 |
| **B8** | **披露与发布** | 何时、以何种聚合粒度公开 | [`public_association_release_contract_v1.md`](public_association_release_contract_v1.md) | 决定网站能否出现结果 |

## C. 签完 B1–B7 之后会发生什么

1. 用已核验的官方文件重建/核对的 2011 表已是现成输入；
2. 冻结 `wave1_analysis_plan_v2.json`（估计量、域、权重、方差、模型、族）；
3. 运行 `run_2011_household_environment_scaleup.py --run --batch pilot105`；
4. 经 `engine_to_schema_v3` 出正式结果表 → 生产校验器 → 披露审查 → 才谈发布。

## D. 本索引自身的信息

- 生成于 2026-10-31，对应代码提交见 GitHub `main`；
- 所有引用路径都可用 `git show <commit>:<path>` 复核；
- 本索引不含任何参与者取值；正式关联模型数仍为 **0**。
