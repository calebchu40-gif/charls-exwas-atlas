# CHARLS 吸烟/饮酒编码与组件字段复核（2026-10-17）

本次复核针对网站中按“概念—原始字段—波次—编码/单位”检索的行为暴露目录。只读本地官方问卷/codebook 的字段说明与汇总标签，未读取受访者记录。

## 复核发现与实现

| 概念/题目 | 官方字段与波次 | 解释 | 网站处理 |
|---|---|---|---|
| 吸烟规律起始时间 DA065 | 2011直接分列年龄与年份组件；2013/2015选择码为 `1=Age; 2=Year`；2018为 `1=Year; 2=Age` | 2011/2013/2015 组件 `_1`/`s1` 是年龄、`_2`/`s2` 是年份；2018 `_1` 为年份、`_2` 为年龄。2018 的 codebook 汇总中年份组件出现异常范围/均值，不能按数值摘要擅自改单位。 | 只在实际存在的波次展示选择字段；组件字段单列其年份或年龄单位，不把选择码当作有序暴露，也不跨波拼接或派生吸烟起始年龄。 |
| 戒烟/减少饮酒及开始饮酒 DA070/DA071 | 2011：`1=Age; 2=Year`；2013、2015、2018：`1=Year; 2=Age` | 这是主字段的答案格式选择码。组件槽 `_1` 在各波记录年份，`_2` 记录年龄；2011 codebook 将变量显示为带空格的 `da070 1`/`da070 2`，发布文件目录中的字段名为 `_1`/`_2`。 | 主字段的选择码按波次校正；组件独立保留年份/年龄单位。日期/年龄都保留原题口径，不合并为单一数值。 |
| 每20支卷烟价格 DA064 | 2011、2013、2015 | 问卷问每包20支卷烟“多少钱”，提示价格指当时/戒烟前对应时点，不是当前价格；题目按吸烟状态与戒烟前后题目路由。 | 新增候选暴露 `cigarette_price_per_pack`，作为连续金额（元/20支），保留个人参照时间与条件性分母限制；不解释成市场烟价、地区价格或普遍价格暴露，不给连续量伪造分类值标签。 |

## 数据来源

- `sources_official/CHARLS_2011_Codebook_extracted.txt`：`da070` 的汇总值为 1 Age、2 Year；组件 `da070 1` 的描述为戒酒年份，`da070 2` 为戒酒年龄；`da071` 同理。
- `sources_official/CHARLS_2013_Codebook_extracted.txt` 与 `sources_official/CHARLS_2015_Codebook_extracted.txt`：DA070/DA071 为 1 Year、2 Age；组件 `_1=Year`、`_2=Age`。DA065 为 1 Age、2 Year；2011 的 DA065 在 codebook 中分别列年龄/年份字段，而非同样的选择字段结构。
- `sources_official/CHARLS_2018_Codebook_extracted.txt`：DA065、DA070、DA071 均为 1 Year、2 Age；DA065 的 `_1=Year`、`_2=Age`。
- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc`，DA064 Word p.74；`sources_official/CHARLS_2013_Questionnaire_extracted.txt` 与 `sources_official/CHARLS_2015_Questionnaire_extracted.txt`，DA064 原题及提示。问卷说明价格是20支一包并提示按对应时点作答。

## 可用于后续建模的限制

1. 这些字段目前是可检索的候选字段映射，并不意味着已经确定了统一的目标人群、暴露定义或分析模型。
2. 起始/停止饮酒问题、起始吸烟年龄会受生存者回忆、问卷路由和既往访谈预载影响；年份与年龄两个组件不得混作同一量表。
3. DA064 只覆盖2011/2013/2015且对受访者有条件地询问。跨波联用前必须先统一目标状态/参照时间、处理缺失路由，并验证数值缺失码、极端值及单位；不允许把未询问编码为零。
4. 2018 codebook 中部分连续组件的汇总统计呈现可疑极值/单位摘要；网站保留原始 codebook 标签和警示，不据汇总表自行纠值。拿到合法授权的分析数据后，需先按用户指南核对特殊码和数据分布，再决定是否分析。

实现脚本：`scripts/build_behavior_exposure_crosswalk.py`、`scripts/enrich_behavior_value_labels.py`。行为字段与逐波编码/组件语义见 `audit/behavior_exposure_variable_mapping_v1.csv` 和 `site-prototype/dist/behavior_exposures_v1.json`。
