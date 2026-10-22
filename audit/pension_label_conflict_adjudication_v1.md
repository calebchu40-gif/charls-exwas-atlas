# 养老金值标签冲突裁定（2026-10-22）

目录构建曾发现15条养老金波次—字段值标签冲突。逐项对照官方波次CodeBook与问卷后，14条属于英语翻译/单位格式差异或审计副本间的标签差异，类别编码一致；机器可读裁定表`pension_label_conflict_adjudication_v1.csv`统一采用经审核的对应波次CodeBook标签，并保留CodeBook来源路径。2011 `fn024`三类编码与正确基线问卷FN024逐项一致；先前冲突来自误用2013随访问卷。

原唯一冲突——2013 `fn056_w2_5`——已于2026-10-22依据官方问卷和CodeBook核对解除“标签冲突”状态。问卷明确给出1=Monthly、2=Quarterly、3=Half a year、4=Annually；CodeBook响应类别表列出1、3、4，未列问卷选项2。CodeBook对季度金额子字段`FN056_W2_6_2`另标“无观测”，与季度类别未出现在类别表相符。当前将题目保留为候选分类暴露，并在字段标签及来源说明中标注该差异；若获准发行版中出现代码2，按问卷解释为Quarterly；不从CodeBook表缺项推断实际发行值，也不把它当成与其他类别定义冲突。依旧需要在拟分析的获准数据版本中核对实际值域、缺失和路线。

CodeBook类别表的聚合频数没有复制到网站、交接包变量标签或分析结果。本次没有读取个体记录，也没有拟合关联模型。2011 `fn024`仍按已核实一致标签处理。

构建器在`build_charls_atlas_catalog.py`中按精确波次与字段码应用裁定，不做跨波推断。来源均为本地`sources_official`下CHARLS官方问卷和CodeBook摘录；未使用频数作为标签或做任何个体层分析。

## 2013 Wave 2 官方文件版本复核（2026-10-22）

在CHARLS官方[2013 Wave 2发布页](https://charls.charlsdata.com/pages/Data/2013-charls-wave2/en.html)核对当前列出的文档后，本地官方PDF SHA-1与页面完全一致：Codebook `C9C5714DBFFEE02050343F9B100ABA501050B7A3`、Household Questionnaire `D1132A289BB3A37B955EBC3F9D42D56DC072A1E4`、Release Note `8F4A90C3DBADB49711333AB1E689BF2756583932`。Release Note标注版本 `VersionID: 20151118`，并说明可从发布Codebook查变量概要。官方页面列出Release Note、问卷、体检问卷、退出/死因问卷和Codebook；未见针对`fn056_w2_5`的勘误或字段映射说明。CodeBook同时把季度缴费金额子字段`FN056_W2_6_2`标为“No Observations”，支持将类别表缺项解释为该版本未列出此响应类别，而非问卷选项含义相反。

因此此次核验排除了“本地PDF版本落后于官网”的解释。类别含义由2013问卷直接定义，故无需由2015/2018同名题反推；CodeBook类别表未列出选项2且对应季度金额子字段无观测，本次将其记为“问卷选项/CodeBook类别表覆盖差异”，解除标签冲突和仅由该冲突导致的禁用状态。实际分析仍须在目标获准发行文件中验证字段值域、缺失和适用路线。
