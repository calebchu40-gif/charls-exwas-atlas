# 2020年疫情相关工作影响变量映射复核（2026-10-17）

## 目的与纳入边界

本轮将CHARLS 2020问卷F模块中7个FG疫情工作模块题和1个FF退休计划题作为单波候选暴露目录。它们是受访者自报的疫情期间工作经历或反事实归因，不是五轮通用工作条件，也不代表感染或客观封控暴露。FG模块须保留抽样资格标志 `xfgsample`；不能将未抽中或未问编码为“无影响”。FF005位于FF工作预期模块，须保留其自身FF004路径；没有证据前不套用FG模块的 `xfgsample`。代码本展示的频数/百分比未纳入网站或值标签文件。

## 概念与源字段

| 候选概念 | 2020字段 | 题意/组件 | 主要限制 |
|---|---|---|---|
| `pandemic_remote_work` | `fg001` | 疫情期间是否远程/居家工作 | 是自报经历；适用2020疫情工作模块样本 |
| `pandemic_employer_paid_closure` | `fg002`, `fg002_1`, `fg002_2` | 单位停工期间是否仍获工资；工资比例、周数为条件组件 | 金额/时长组件按 `fg002` 回答路径解释 |
| `pandemic_household_farm_work_change` | `fg003`, `fg003_1`, `fg003_2` | 家庭农业工作相较“若无疫情”的增减；多/少工作周数 | “本来不会做农业”不是零周数，保留独立类别 |
| `pandemic_paid_employment_change` | `fg004`, `fg004_1`, `fg004_2` | 有偿就业工作日变化及周数组件 | 与农业和自营工作分别保留 |
| `pandemic_self_employment_change` | `fg005`, `fg005_1`, `fg005_2` | 非农自营、自由职业及无偿家庭企业工作变化 | 问卷明确不包括农业；“春节后没工作”需单列 |
| `pandemic_work_hours_change` | `fg008`, `fg008_1`, `fg008_2` | 每周工时变化与增减小时数 | 问卷要求整日未工作记入工作日减少，不能在工时重复计数 |
| `pandemic_unemployment_benefit` | `fg009`, `fg010_1`, `fg010_2` | 疫情期间失业保险领取、月份及月金额 | 月份/金额仅在领取路径后询问；很稀疏的金额不得公开小单元 |
| `pandemic_retirement_plan_shift` | `ff005`, `ff005_1`, `ff005_2` | 计划停止工作时间是否提前/推迟及年数 | 主观预期而非实际退休；保留FF004路径，不假定FG专属xfgsample适用；问卷将“健康允许就一直工作”归为未受影响 |

问卷答案分类按 CHARLS 2020 English Questionnaire 提取文本录入；代码本频数没有复制。主字段保留官方类别值，金额/时长/年数使用条件组件，不把子字段拆成更多概念。各来源行、标签、单位和状态见 `audit/pandemic_work_impact_variable_mapping_v1.csv`；选择标记见 `audit/pandemic_work_module_selection_metadata_v1.csv`；网站工作暴露目录 JSON 也按概念呈现这些波次字段。

## 官方来源与统计使用

- `sources_official/CHARLS_2020_Questionnaire_English_extracted.txt`：F模块FF005及FG001–FG010题目、类别、访员说明与条件组件。
- `sources_official/CHARLS_2020_Codebook_extracted.txt`：字段名、变量描述和测量摘要；代码本公布的频数未用于展示。
- `audit/raw_variable_catalog_v1.csv`：确认各源字段存在于CHARLS官方2020发布目录及Work_Retirement模块。

这些变量目前仅是候选检索映射。正式分析前仍需核对FG模块 `xfgsample` 的官方跳转/抽样定义及FF005的FF004目标人群、问卷版本适用对象、特殊缺失码、代理回答情况、权重/设计变量和可公开统计的披露阈值。不得仅凭代码本汇总频数估计个体关联。
