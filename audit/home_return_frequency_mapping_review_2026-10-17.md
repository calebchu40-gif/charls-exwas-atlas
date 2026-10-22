# 离家上学/工作期间回家条目复核

更新：2026-10-21。先前版本把一份误标为2011基线的2013随访问卷当作2011问卷，错误地称2011 `BA005`也包含三档回家频率，并因此记录问卷/Codebook冲突。该判断已撤回。以下结论依据正确的2011官方基线家户问卷、2011官方Codebook以及2013官方随访问卷和Codebook；不读取个人记录、不使用Codebook频数。

## 2011：二元的每周返家状态

2011基线问卷 `BA005` 问：“是否平时在外上学/上班，但通常每周回家？”答案为`1=Yes`、`2=No`。官方Codebook将其列为“Return Home Every Week”，答案标签同为二元是/否。两份官方材料在题义与选项结构上相符。当前映射为独立的波次专属候选 `away_school_work_weekly_home_return_2011`，不是三档回家频率指标。

## 2013：三档返家频率

2013随访问卷 `BA005` 询问几乎每天回家、每周末回家、或两周及更久回家一次，Codebook列出三档有序选项：`1=Go home almost every day`、`2=Go home almost every weekend`、`3=Go home once every two weeks or more`。当前单独映射为 `away_school_work_return_home_frequency`。不与2011二元字段直接合并或视为同一量尺。

两条记录都只描述受访者外出上学/工作期间的返家情况，不测量距离、离家时长、外出原因或迁移。应用于模型前仍须审查适用人群、逐波缺失/结构跳题和实际分析分母。

## 波次编码边界

2020也有名为`BA005`的字段，但它测量访谈地址类型；2018 `BA005_W4`核实的是出生日期与证件信息是否一致。必须以“波次+变量码”定位字段，不能仅凭同名代码合并。

## 来源与可复现材料

- 2011官方基线问卷：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`，BA005。
- 2011官方Codebook：`sources_official/CHARLS_2011_Codebook_extracted.txt`，BA005。
- 2013官方问卷与Codebook：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`、`sources_official/CHARLS_2013_Codebook_extracted.txt`。
- 构建脚本：`scripts/build_home_return_frequency_crosswalk.py`。
- 输出：`audit/home_return_frequency_crosswalk_v1.csv`、`audit/home_return_frequency_value_label_review_v1.csv`。

本轮把原先1个概念的2条映射修正为2个波次专属概念、2条映射。旧结论与其引用的误标摘录不再有效；`sources_official/SOURCES.md`记录了文件身份更正。


2026-10-22 status correction: the current catalog builder retained a stale DO NOT ANALYZE flag from the superseded misidentified-questionnaire review. The official 2011 baseline questionnaire and Codebook both verify the binary 1=Yes/2=No item; the builder now emits it as a single-wave candidate while preserving the requirement to verify respondent denominator and eligibility. It remains separate from 2013 three-level frequency.
