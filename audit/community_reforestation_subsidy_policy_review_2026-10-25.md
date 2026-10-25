# 2011 CHARLS村级退耕还林补贴计划候选映射（2026-10-25）

## 来源与字段

CHARLS 2011 Community Questionnaire的JG021–JG024是村级退耕还林补贴计划条目：JG021询问村里是否实施，回答“No”跳至JG025；“Yes”后询问JG022开始年份、JG023在2010年领取补贴的户数和JG024平均补贴标准。问卷标明JG021为V-only（村级路线）。官方Codebook确认JG021的1=Yes、2=No；JG022为年份，JG023为户数，JG024为平均补贴标准。目录只保留该类别标签，没有抄录Codebook频数、均值、极值或观察数。

已把四个来源字段加入`community_reforestation_subsidy_program`环境政策背景候选，单位分别为无离散单位、year、households和Yuan/mu。字段级说明保留条件路线与层级；分析资格仍待核实。这个候选描述地方政策及其报告的实施/受益规模，不等于森林覆盖或恢复成效，不证明抽中家庭实际领取，也不是个人层面的生态暴露或污染剂量。它应与其他村级社区变量一样，先满足社区链接键、调查方差设计和定义明确的估计目标，不能自动分配成每位受访者的暴露。

## 构建改进

新增字段由社区交叉表生成器要求同时在官方问卷和Codebook中命中对应代码，并检查题目措辞。审查同时发现社区值标签提取器的Codebook前缀清单遗漏`jg`模块；已补入该前缀，使JG021官方类别可正确抽取为`1=Yes; 2=No`，频数依旧剔除。回归测试覆盖来源、四字段、单位、路由、解释边界和类别标签。

## 官方来源

- CHARLS 2011 Community Questionnaire，Part G，JG021–JG024；项目内核验文本：`sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt`。
- CHARLS 2011 Codebook，Community模块JG021–JG024；项目内核验文本：`sources_official/CHARLS_2011_Codebook_extracted.txt`。

尚未读取获批发行版中的相关值、验证受益户数字段的发行版编码，也未执行任何关联分析。
