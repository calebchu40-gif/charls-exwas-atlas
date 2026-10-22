# 2011/2013首次工作时间单位选择器审计

2011基线与2013问卷/代码本将`FB001`定义为“Age or Year Start Working”，取值1=Age、2=Year；实际首次工作时间分别存放于`FB001_1`（年龄）或`FB001_2`（日历年）。因此父项只决定回答单位，不能把它本身作为工作暴露，也不能将两个子字段的原始数值混作同一单位。

现将2011、2013的`FB001`从E候选改列C类测量/量纲元数据，并保留子字段已有的`first_work_start_timing`候选映射。跨波推导工作起始年龄时需制定预先规则，使用出生年份计算年龄可能需要舍入/调查时间口径核对；当前不自动换算。2020的`FB001`是农业工作地点，不属于本选择器。

依据：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`、`sources_official/CHARLS_2013_Questionnaire_extracted.txt`及对应Codebook。字段级C映射见`audit/measurement_protocol_crosswalk_v1.csv`，角色修正见`audit/catalog_role_override_review_v1.csv`。未读取个人记录。
