# 2011养老金分级展开区间字段映射复核

更新：2026-10-22。基线问卷说明，FN005/FN008/FN014/FN019/FN023在受访者拒答或不记得相应养老金月待遇金额时追问分级区间；FN037在FN034=Yes或FN035采取补缴路径后，补充FN036预期养老金金额。问卷明确金额单位和计划路由，字段目录的`_a`/`_b`标签标为Min/Max Bracket。

已将2011 `fn005_a/b`、`fn008_a/b`、`fn014_a/b`、`fn019_a/b`、`fn023_a/b`映射到既有`pension_monthly_benefit_amount`概念，将`fn037_a/b`映射到既有`pension_expected_monthly_benefit_amount_untyped_plan`概念；不新增概念。区间端点保留为区间上下界，不视为精确点估计、普通缺失填补或独立暴露。FN036父字段仍为月金额/末期工资比例单位选择器C类，FN037仅对应金额分支。

另查2011 Codebook对`fn045_a/b`标注“No Observations”；两条记录列为C类inactive legacy metadata并排除E/P矩阵，不据此推断DB预期待遇区间。

证据：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`，FN002–FN023和FN034–FN037段落；`sources_official/CHARLS_2011_Codebook_extracted.txt`中fn005/008/014/019/023/037/045标签。实现：`scripts/build_pension_supplementary_crosswalk.py`及`audit/catalog_role_override_review_v1.csv`。仅使用官方问卷、Codebook和公开字段目录，未读取个体记录。
