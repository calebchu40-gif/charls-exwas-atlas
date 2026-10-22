# 人口学预载、出生日期来源与访谈地点派生字段角色复核（2026-10-22）

## 角色调整

以下字段由自动关键词分类的E类候选转为C类元数据/协变量来源，不进入暴露—表型关联矩阵：

- 2013 `zbc001`、`zbc005`、`zbd001`：问卷将其作为当前户口类别、户口地点及最高学历的预载记录，供访员向返访者核对；回答或更正内容在独立题项中。它们记录的是预载/核验来源与问卷路线，不应当作当前回答或额外暴露。
- 2018 `zbc004`：上一轮户口类型的预载确认字段；若不正确，另有历史户口类型题。
- 2015 `ba004_w3`及其年、月、日组件：身份证或户口本记载的生日/日期来源。2018 `ba005_w4`：实际生日是否与证件登记相同的比较字段。它们服务于年龄协变量及访谈核验，应遵从CHARLS年龄推导和特殊值规则；目录不发布任何个体生日值。
- 2020 `xrresidencesurveyhome`：官方CAPI说明依据访谈地址和住所类型生成的调查地点匹配标记，属于访谈地点/地址路线元数据，不是社区环境暴露。底层详细地址不用于公开关联目录。

这些判断只依据官方问卷/CAPI公式与公开字段目录。2015出生日期字段保留在C类协变量来源，不能仅凭字段类型推断适用样本或最终年龄变量；正式分析需另行按官方年龄参考规则选择证件生日与实际生日，并验证有效值。`xrresidencesurveyhome`保留为C类，不能作为“居住在调查地”的一般环境暴露。

## 官方来源

- 2013：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`、`sources_official/CHARLS_2013_Codebook_extracted.txt`
- 2015：`sources_official/CHARLS_2015_Questionnaire_extracted.txt`、`sources_official/CHARLS_2015_Codebook_extracted.txt`
- 2018：`sources_official/CHARLS_2018_Questionnaire_extracted.txt`、`sources_official/CHARLS_2018_Codebook_extracted.txt`
- 2020：`sources_official/CHARLS_2020_Questionnaire_English_extracted.txt`（其中含`XRResidenceSurveyHome`的官方CAPI定义）

逐字段更正登记在`audit/catalog_role_override_review_v1.csv`，由`scripts/apply_catalog_role_overrides.py`按波次应用。未读取个体回答或生成个体生日/地址值。
