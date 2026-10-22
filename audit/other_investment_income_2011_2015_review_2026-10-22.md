# 2011–2015个人其他投资收入字段审计

更新：2026-10-22。2011与2013官方问卷均询问受访者过去一年是否取得此前未报告的其他投资收入（HC023）；答“是”后询问过去一年总金额（HC024，人民币元）。题意、分析层级和参考期一致，因此映射到两个跨波候选概念：`other_investment_income_past_year_status`及`other_investment_income_past_year_amount`。保留HC023类别回答、HC024仅在HC023=Yes后的分母，并将拒答/不知时的HC025区间展开作为另一种测量路径；区间端点不是精确金额，不得与直接金额相加或替代。名义金额跨波比较前需按预先规定的价格基期调整。

2011问卷对“其他投资收入”的访员说明涵盖金融市场/资本市场投资工具等来源，并举利息、股息、红利等例子；2013题干保持“此前未报告的其他投资收入”措辞。2011 Codebook给出HC023的Yes/No标签，并报告HC024最小值为-100,000元、最大值500,000元；2013 Codebook报告金额范围0–450,000元。2011负最小值的含义不能从摘要统计确定，可能涉及特殊码或字段问题；在取得获准发行版字段字典/数据验证前，保留原值并标记待核，不自行解释为真实负收入、亏损或缺失。所有特殊值和极端值也需在获准的数据处理中核对。

2015 Codebook对HC023、HC024及HC026均明确标为“No Observations”。因此保留2015 HC023/HC024字段索引并转列C类inactive legacy metadata，不新增E映射、不将空槽编码成0，也不把问卷仍有题页等同于发布数据存在观测。2013/2015目录中同名变量不能仅凭变量名合并；上述合并范围仅为问卷/Codebook证据一致的2011和2013。

来源：`sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`（HC023–HC025）、`sources_official/CHARLS_2011_Codebook_extracted.txt`（hc023–hc025）；`sources_official/CHARLS_2013_Questionnaire_extracted.txt`和`CHARLS_2013_Codebook_extracted.txt`（HC023–HC025）；`sources_official/CHARLS_2015_Codebook_extracted.txt`（hc023–hc026 No Observations）。实现见`scripts/build_personal_income_crosswalk.py`、`scripts/apply_catalog_role_overrides.py`及`audit/catalog_role_override_review_v1.csv`。只审阅官方问卷、Codebook与字段元数据，未读取个人级记录或运行关联模型。
