# 家户住房装修/装饰支出候选（2011、2013）

核查日期：2026-10-21。2011基线与2013官方家户问卷的HA025均询问过去一年家户名下所有住房的装饰或装修支出，家具费用除外，单位人民币元；各波Codebook均有该字段的观测分布摘要。它是家户层过去一年支出候选，不是个人收入、房屋价值、房屋质量或全部住房投资。不同波次金额先按名义值保留；跨波实质金额分析须另行预先规定价格指数和基年。

2015字段目录虽含HA025，但该波Codebook将其标记为“No Observations”。因此只列2011/2013可核实字段，不把2015目录占位当作已发布观测字段。装修/装饰费用与另问的“翻盖/重建且不含装饰”费用属于不同构念，不合并。实际分母、特殊缺失和发布数据文件内可用性仍须在获准的个人/家户微观数据中核对。

依据：2011基线家户问卷住房模块HA025及2011 Codebook；2013 Questionnaire与Codebook HA025；2015 Codebook HA025为No Observations。变量目录与复现脚本：`audit/household_renovation_expenditure_crosswalk_v1.csv`、`scripts/build_household_renovation_expenditure_crosswalk.py`；完整入口`python scripts/build_ep_atlas_metadata.py`。未读取个人回答。
