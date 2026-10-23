# 2011吸烟起始时间年龄/年份固定标记复核（2026-10-23）

2011全国基线问卷的DA065题将实际回答直接分成`DA065_1`年龄和`DA065_2`日历年。官方Codebook另列`DA065S1`（唯一类别1=Age）及`DA065S2`（唯一类别2=Year）；这两个固定类别字段是组件类型标记，不是受访者的吸烟起始年龄/年份。目录只保留标签、不复制Codebook频数，将标记归C类；实际时间回答仍为E候选且年龄和日历年分列。

该规则与同期戒烟题DA062S1/S2相同。脚本自动将2011四个固定标记字段纳入C类，每次完整流水线会重复应用该判定。核验只用官方问卷和Codebook，没有读取参与者级数据。来源：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`（DA065题）；`sources_official/CHARLS_2011_Codebook_extracted.txt`（DA065_1/2及DA065S1/S2）。
