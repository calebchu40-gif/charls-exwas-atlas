# 2018养老金缴费单位父项复核

更新：2026-10-22。2018官方问卷FN035_W4_a先询问当前养老金计划是否要求缴费；若Yes，FN035_W4_b询问单位当前缴费额（FN035_W4_b_1为元/月，FN035_W4_b_2为工资比例），FN035_W4_c询问个人当前缴费额（FN035_W4_c_1为元/月，FN035_W4_c_2为工资比例）。官方Codebook为父项`fn035_w4_b`和`fn035_w4_c`分别列出1=Yuan/Month、2=Percent。

父项只选择子字段的计量形式，已从E候选改列C类元数据，分别标明单位缴费与个人缴费路径。4个有单位区分的子字段继续作为既有月缴金额/工资比例概念来源；不能把父项值当作金额、也不能将单位金额和工资比例直接合并。区间展开字段的条件路由仍由问卷题干分别注明：拒答/不记得，或单位金额为0时追问；需在获批个体数据和发布版缺失码下验证该路由。

来源：`sources_official/CHARLS_2018_Questionnaire_extracted.txt`第7955–7975行；`sources_official/CHARLS_2018_Codebook_extracted.txt`第63403行及第63459行。映射角色规则：`audit/catalog_role_override_review_v1.csv`（`pension_amount_unit_selector`）；`scripts/apply_catalog_role_overrides.py`。未读取个人记录。
