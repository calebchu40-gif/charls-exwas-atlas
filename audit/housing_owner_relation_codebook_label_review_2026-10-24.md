# 2018 住房所有者关系标签逐字段复核（2026-10-24）

## 核查范围

对照`housing_exposure_variable_mapping_v1.csv`中的2018字段，逐字段读取官方提取版`CHARLS_2018_Codebook_extracted.txt`中所有215条`household_property_owner_relation_slots`映射，以及9条当前住房`i000_w4_4_s1`至`s9`字段。解析只抽取代码本中完整独立行的数值代码与`Do Not Own`/`Own`文字标签；不读取或输出`Freq.`、百分比或观察数。

## 发现与处理

原解析器仅接受`0/1`标签，漏掉了代码本明确列出的`2=Own`、`3=Own`等字段特异代码，并把相关标签留空。现改为转录每个字段在官方代码本中实际列出的关系类别代码，保留原始非二元码。例如`ha000_w4_2_2__s2`和`i000_w4_4_s2`均展示`0=Do Not Own; 2=Own`；若代码本该字段只列出`0=Do Not Own`，则只展示该标签，不推断未列出的正向类别。所有记录注明未列类别不作推断。

标签已同步至主字段目录、E/C角色分片、跨波概念—字段crosswalk及住房专题检索JSON。Finalization-only流水线现会在住房测量单位/路由补充步骤之前重建住房专题JSON，避免新标签漏到专题页，也避免重建覆盖随后加上的单位和限制。

## 验证

相关专项测试及全套329项Python测试通过；34个静态JSON可解析，JavaScript语法、Python编译及`git diff --check`通过。五波元数据配对数未变；不含微观记录、Codebook频数或分析结果。实际关联模型仍为0。

来源：`sources_official/CHARLS_2018_Codebook_extracted.txt`、`sources_official/CHARLS_2018_Questionnaire_extracted.txt`；机器可读逐字段结果：`audit/housing_owner_relation_value_label_review_v1.csv`及`audit/housing_current_owner_relation_labels_2018_v1.csv`。
