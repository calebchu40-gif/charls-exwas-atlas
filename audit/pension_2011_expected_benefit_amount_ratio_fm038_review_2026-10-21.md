# 2011 FM038预期待遇金额与工资比例分支（2026-10-21）

官方2011基线家庭问卷确认：当退休类别 `FM011=4`（内部退职但尚未正式退休）时询问FM037–FM040。FM038问“正式退休第一年”预计待遇，并把响应分成两个明确单位：`FM038_1` 元/月，或`FM038_2` 为退休前工资的百分比。将两者接入已存在的`expected_formal_retirement_benefit_monthly_amount`及`expected_formal_retirement_benefit_salary_ratio`概念，不互换单位，也不将比率当成金额。

2011 Codebook将FM038父项列为“Amount or Percent”，子项列为“Amount Per Month”和“Percentage”；父项 `fm038` 本身不是待遇值，应作响应格式/路径元数据待核，而非另一个暴露。FM039的区间展开题只显示金额档位，但在获批数据中尚未确认该区间是否适用于FM038_1而不是百分比分支，因此本次不把FM039_a/b连到某个金额构念，也不以频数表推断。

需在获批发布文件中验证FM038父项的编码、两子项在互斥/空值时的含义，以及特殊缺失。问卷单位与条件分支清楚，不代表个体值有效，也不代表已完成跨波可比性审核。未读取个体数据、未估计关联。

实施：`scripts/build_retirement_history_exposure_crosswalk.py`；目录应分别保留FM038_1元/月、FM038_2工资比例和FM038父项待核状态。
