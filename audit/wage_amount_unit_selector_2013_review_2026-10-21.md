# 2013工资/奖金金额单位选择器审计

核查日期：2026-10-21。CHARLS 2013官方Codebook将`GA002`定义为工资/奖金金额回答格式：1=元/年，2=元/月；对应精确金额字段分别为`GA002_1`和`GA002_2`。因此，`GA002`本身只决定金额字段及单位，不能作为连续暴露或直接用类别码代替收入。映射表把`GA002`列为C类单位选择器，将两个金额字段保持为独立单位概念；需依据受访者当次路由只使用相应分支。

官方问卷印刷页221提到年收入和月收入两个输入槽，Codebook提供`GA002`选择类别和分支金额标签。Codebook频数未被当作分母或样本量。任何合并成年收入金额都需要明确换算/年化规则和对零、特殊缺失及不适用的处理，并在获准数据中验证真实字段结构。

依据：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`工资收入题组；`sources_official/CHARLS_2013_Codebook_extracted.txt`约33618–33629行。C类映射：`audit/measurement_protocol_crosswalk_v1.csv`；角色修订：`audit/catalog_role_override_review_v1.csv`。完整构建：`python scripts/build_ep_atlas_metadata.py`。
