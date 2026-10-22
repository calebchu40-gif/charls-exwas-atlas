# 残余睡眠时点与家户待客行为映射复核

更新：2026-10-17。按逐波公开变量目录、问卷与代码本复核。仅处理问卷元数据，不读取受访者记录；两项均为候选E概念，不是正式分析变量。

## 新增候选

新增两个概念、15条字段—波次映射：

| 候选概念 | 波次/字段 | 构念与测量层级 |
|---|---|---|
| `household_meals_provided_to_guests` | 2011、2013、2015、2018 `ge005`；2020 `gf005` | 过去一周家户为客人提供的餐次数，按人次计；家户层社会互惠/待客行为 |
| `previous_day_sleep_schedule` | 2013 `wb03`–`wb03_4`、`wb04`–`wb04_4` | 昨日起床及就寝时间的AM/PM、小时、分钟组件；单波、前一日回忆 |

## 官方定义与编码

- 2011全国问卷的`GE005`问“最近一周，您家的客人在您家吃了几顿饭（按人次计算）”；2013、2015、2018问卷保留“上周为客人提供多少餐”的定义。2020 `GF005`表述为家户上周为客人提供的餐数。五波均是家户回答，不是受访者个人饮食摄入；不同波次编码字段名按原样保留。
- 2013问卷WB03/WB04分别询问“昨天几点起床”和“昨天一天结束时几点睡觉”，问卷明确使用12小时制并记录小时、分钟和AM/PM。代码本给`wb03`、`wb04`的选择码为`1=AM; 2=PM`；另外列有`_1`至`_4`精确报告组件。本目录保留全部字段组件，但不自行拼接时间、填补缺失或推导睡眠时长。
- 代码本中的分布频数和百分比没有进入值标签或样本量。待客次数题的软检查阈值不是有效值定义，也没有据此截断或排除。

## 限制与分析前要求

1. 待客餐次数是家户层社会互惠候选量。只有在分析方案清楚说明家户暴露如何链接到目标受访者并处理同户受访者时才可纳入模型；不能拆成家庭成员个人指标，也不能称为食物摄入或食物安全指标。
2. 睡眠时点是2013年单日回忆字段；不得称为平常作息、睡眠时长或多日平均。AM/PM与精确报告字段的路由及实际字段存储需用授权数据字典核实后，才可构造统一钟点。
3. 两项均需独立确认目标分母、特殊缺失码、波次分析资格和调查设计；元数据目录收录不表示数值可直接建模。

## 来源

- 2011：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`，GE005。
- 2013：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`，WB03/WB04、GE005；`sources_official/CHARLS_2013_Codebook_extracted.txt`，WB03/WB04值码和时间组件、GE005。
- 2015：`sources_official/CHARLS_2015_Questionnaire_extracted.txt`，GE005。
- 2018：`sources_official/CHARLS_2018_Questionnaire_extracted.txt`，GE005。
- 2020：`sources_official/CHARLS_2020_Questionnaire_English_extracted.txt`，GF005。

复现脚本：`scripts/build_residual_behavior_exposure_crosswalk.py`；主流程：`python scripts/build_ep_atlas_metadata.py`。
