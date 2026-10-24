# 主观预期寿命题目来源审阅（2011–2018）

官方问卷和 Codebook 显示，2011、2013、2015、2018 均有五级“达到某个年龄的主观可能性”题，源变量为 `DA081`。页面将其补入已有 `subjective_life_expectancy` 候选概念，并保留各波来源文件与题目类别。2020 的同一概念来自 `DA029`，而 2011–2018 的 `DA029` 是前列腺疾病诊断题；不得根据字段码跨波联结。

各波问卷把目标年龄呈现为 `[...]`，本地核验的问卷文本没有给出实际目标值，也未核定展示卡片/CAPI年龄阈值生成规则。因此目录只保留 1–5 原始有序选项，不将阶梯值换算成百分比，不宣称跨波目标年龄一致，也不称为实际生存或客观寿命预测。2018 问卷另列 997“不知道”，作为单独类别保留；授权发行版特殊缺失码仍需核实。正式分析前须恢复每条记录适用的目标年龄，并确定有资格的目标人群与缺失处理。

本次只增加元数据候选映射，没有读取或发布受访者观测、Codebook 频数、样本量或关联估计。该题不自动批准任何协变量选择，也不代表可以直接把五级阶梯视作连续概率。

## 官方来源

- `sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`；`CHARLS_2011_Codebook_extracted.txt`。
- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`；`CHARLS_2013_Codebook_extracted.txt`。
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`；`CHARLS_2015_Codebook_extracted.txt`。
- `sources_official/CHARLS_2018_Questionnaire_extracted.txt`；`CHARLS_2018_Codebook_extracted.txt`。
- 2020 `DA029` 与年龄阈值 `XFAgePossibility` 的单独审阅：`audit/health_symptom_variable_mapping_v1.csv` 和 `audit/ep_concept_source_crosswalk_v1.csv`。
