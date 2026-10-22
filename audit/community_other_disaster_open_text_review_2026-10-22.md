# 2011 JI002 “Other disaster”开放文本字段角色复核

更新：2026-10-22。官方社区问卷显示，JI001先筛查过去五年村/社区是否发生重大自然灾害；JI002分别记录洪水、干旱、火灾、地震、台风、冰雪灾害及“其他自然灾害”。“其他”仅在肯定回答后要求注明类型，后续次数、最严重事件年月和死伤人数同属条件追问。原目录字段`ji002_other`的官方标签为“Other Disaster”。

该字段不是标准化灾害类别，文本含义无法按公开问卷与代码本稳定归类，且回答单位是社区告知者报告的社区事件，不是受访者个人测量。因此不新增E概念；将其从自动E候选改列C类开放文本元数据，禁止将回答文本公开展示或用于暴露—表型矩阵。其余标准灾害类型及计数/时间/伤亡字段继续按既有社区自然灾害crosswalk逐项保留，并须遵守社区—个人连接、调查设计和披露限制。

证据：`sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt`，JI001–JI002（提取文本约第1705–1800行，含第36页“Other disasters”路由与请注明项）；`audit/raw_variable_catalog_v1.csv`中2011 `ji002_other` 官方字段标签为 `Other Disaster`。未读取个体记录或自由文本。

目录修订：在`audit/catalog_role_override_review_v1.csv`记录准确波次/字段身份及`unstructured_other_specify_text`元数据类型；构建后字段仍可按码检索，但归类为C类，不分配Concept ID。
