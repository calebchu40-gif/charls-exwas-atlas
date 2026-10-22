# 2011商业养老保险按年缴费字段审核

日期：2026-10-21。根据CHARLS 2011基线家庭问卷与代码本；未读取个人级数据。

官方问卷将商业养老保险缴费方式分为按年（FN052=1）与一次性缴费（FN052=2）。按年缴费路径记录`fn053`年度保费（元/年）及`fn054`需要缴费的年数；一次性缴费者跳过这两个字段，转到`fn055`一次性总保费。现将fn053、fn054分别映射为年度缴费金额与所需缴费年限，保持单位分离，并记录结构性路由。不得将FN052=2导致的跳题解释成0或未参保；实际范围、特殊码与可分析分母仍须使用许可数据核对。

来源：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`（FN052–FN055）和`CHARLS_2011_Codebook_extracted.txt`。规则位于`scripts/build_pension_supplementary_crosswalk.py`。
