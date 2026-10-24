# 候选概念按网站检索类别分布

数据来源：当前网站主目录 `site-prototype/dist/catalog.json`。按Concept ID在每个角色和类别中去重；一个Concept ID可出现在多个类别或角色中，因此类别计数是非互斥的，不能相加为总概念数。字段行和波次—变量码也不是独立分析指标或样本量。

|角色|检索类别|候选Concept ID数|字段—角色—类别行|不同波次—变量码|
|---|---|---:|---:|---:|
|e|social determinants|599|2134|2132|
|e|social protection|314|1331|1331|
|e|community context|104|198|198|
|e|behavior|47|315|267|
|e|housing and built environment|40|480|480|
|e|food and household environment|29|161|161|
|e|internal biomarker|15|19|19|
|e|healthcare access|7|109|109|
|e|family and intergenerational context|6|6|3|
|e|early-life and family socioeconomic context|5|5|3|
|e|behavioral exposures|1|2|2|
|e|environmental perception|1|1|1|
|p|chronic disease ancillary|115|664|664|
|p|health and symptoms|40|174|171|
|p|physical function|38|266|260|
|p|chronic disease|33|248|248|
|p|cognition|24|338|338|
|p|healthcare access|22|217|217|
|p|biochemistry|16|32|32|
|p|internal biomarker|15|19|19|
|p|mental health|10|50|50|
|p|anthropometric|5|24|15|
|p|social wellbeing|4|10|10|
|p|blood pressure|3|54|27|

总量（去重）以 `audit/directory_scope_counts_v1.json` 为准：E/P候选概念共1442个（E=1150、P=301，9个兼具角色）。本表为检索分类浏览，不是正式分析变量冻结表。
