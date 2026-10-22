# 人口学记录标记与历史户口位置字段复核（2026-10-22）

## 角色校正：记录核验/路由元数据

按官方问卷与Codebook复核，以下字段是上一轮预载信息的确认或分路，不是独立暴露：

- 2013 `bd001_w2_1`：确认上一轮最高学历记录是否正确；答“否”转入更正题。
- 2013 `bd001_w2_2`：确认上一轮最高学历是否含成人教育，用于正确解释/更新此前学历记录。
- 2015 `bc001_w3_1`：核对上一轮预载户口类型/位置是否正确；回答“否”进入修正路线。
- 2018 `bc001_w3_3`：上一轮户口地址记录是否存在/是否无户口的条件分流标志；实际地点信息属于条件字段，不把这个路由标记当成地理暴露。

以上四条由自动E候选改列C类，官方是/否或路线标签已记录；个体回答未读取。

## 2015上一轮户口地点关系：独立保留

2015 `bc001_w3_3`是另一字段：问“上一轮访谈时”的户口地点相对常住地址的位置。问卷/Codebook列出的代码包括与常住地址相同、常住地址所属县市区内另一村/社区，以及国外。现作为单独的历史社会位置候选`prior_interview_hukou_location_relation_2015`，不并入当前户口所在地或2013当前地点，也不发布细粒度地点值。其代码是粗关系类别，不要从Codebook频数表推断分析样本量；实际问卷适用路由与获批发行编码仍需验证。

## 来源及实现

依据：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`、`sources_official/CHARLS_2013_Codebook_extracted.txt`、`sources_official/CHARLS_2015_Questionnaire_extracted.txt`、`sources_official/CHARLS_2015_Codebook_extracted.txt`、`sources_official/CHARLS_2018_Questionnaire_extracted.txt`、`sources_official/CHARLS_2018_Codebook_extracted.txt`。E→C逐波修正登记于`audit/catalog_role_override_review_v1.csv`并由`scripts/apply_catalog_role_overrides.py`应用；2015历史地点候选加入`scripts/build_demographic_social_exposure_crosswalk.py`。目录仅保存变量级元数据，不含受访者答案。
