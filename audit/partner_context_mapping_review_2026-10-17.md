# 伴侣背景字段映射审阅（2026-10-17）

本次依据CHARLS官方问卷、代码本和原始字段目录新增3个候选社会背景概念、11条波次字段映射。只使用公开变量元数据，不读取受访者记录，也不引用代码本频数。

|候选概念|波次—字段|官方含义/值码|路由和比较边界|
|---|---|---|---|
|是否与伴侣以配偶身份共同生活|2011/2018 `be002`；2020 `ba012`|当前是否与伴侣同居；1=Yes，2=No|2011问未婚者是否与伴侣同居；2018问是否有伴侣以配偶身份共同生活；2020问当前是否有共同生活伴侣。2011/2018按婚姻状态路由。2020代码本回答分母较窄，但现有英文问卷提取未显示具体触发条件；保留路由待核，结构性跳题不能编码为No。|
|当前婚姻状态|2011/2013/2015/2018 `be001`；2020 `ba011`|六类：与配偶同住、已婚暂时异地、分居、离婚、丧偶、从未结婚|保留暂时异地与分居的区别；不把代码数字当作有序分数，也不在没有估计目标时擅自合并类别。|
|配偶/伴侣最高受教育程度|2011/2013/2015 `bf004`|配偶/伴侣最高学历；按波次展示教育类别|只适用于有配偶/伴侣且到达题目的路由；不代表受访者本人教育。2011类别止于9类，2013/2015扩展至硕士/博士；不强行把各波折叠为同一数值等级。2018没有直接等价BF004字段。|

配偶学历可能是家庭社会经济暴露，也可能是具体研究问题中的混杂因素；不得机械加入每一个调整模型。不同波次代码本的频数/百分比没有进入值标签。

2020 `ba013`“过去一年与配偶共同居住月数”暂未映射：官方代码本显示的观测分母明显小于婚姻状态字段，现有英文问卷提取中没有找到明确触发条件；在适用人群及跳题分母核清前，不把缺失推断为0。

## 来源

- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` / `CHARLS_2011_Codebook_extracted.txt`
- `sources_official/CHARLS_2013_Questionnaire_extracted.txt` / `CHARLS_2013_Codebook_extracted.txt`
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt` / `CHARLS_2015_Codebook_extracted.txt`
- `sources_official/CHARLS_2018_Questionnaire_extracted.txt` / `CHARLS_2018_Codebook_extracted.txt`
- `sources_official/CHARLS_2020_Questionnaire_English_extracted.txt` / `CHARLS_2020_Codebook_extracted.txt`
- 字段级crosswalk：`audit/partner_context_crosswalk_v1.csv`（3概念、11字段）；复建脚本：`scripts/build_partner_context_crosswalk.py`。
