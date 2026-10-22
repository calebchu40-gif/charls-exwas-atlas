# 2015停用收入、住房及资产字段复核（2026-10-22）

## 结论

2015 Codebook明确将下列18个旧字段标为“No Observations”。它们保留在字段目录中用于说明问卷版本和字段来源，但统一转为C类停用元数据，不能从同模块其他字段借值、不能把空缺理解成零，也不能进入E/P矩阵：

- 个人工资回答单位旧字段：`ga002_1`、`ga002_2`。2015实际过去一年工资金额由`ga002`记录。
- 家庭成员收入单位/来源父项：`ga008_1a`、`ga008_3a`、`ga008_9a`。这些父项无观测不代表相应的家庭成员子字段都无值；子字段依Codebook各自的标签和观测状态保留。
- 住房旧字段：`ha018`、`ha022`、`ha023_1`、`ha023_2`、`ha025`、`ha043`、`ha045_check`。当前波次的家庭住房问项和另行发布的字段按各自观测状态处理，不能把旧字段的无观测状态外推给其他字段。
- 住房补偿旧字段：`ha026_w2_14`、`ha026_w2_14_25_`。
- 耐用品与家庭资产旧字段：`ha065_1`、`ha065_1_19_`、`ha074`、`ha075`。

此外，`ha065_1_18_`与问卷/Codebook存在无法直接调和的身份冲突：2015问卷HA065将第18项列为“None”，耐用品金额问题只覆盖第1–17项；Codebook却在`ha065_1_18_`给出一个金额统计值（70）。该字段单独转为C类并标记`DO NOT ANALYZE`，不作为“其他耐用品”或任何资产价值。

## 官方依据

- `sources_official/CHARLS_2015_Codebook_extracted.txt`，第8章“Individual Income”、家庭收入及住房资产、耐用品章节：逐字段“No Observations”标签及`ha065_1_18_`单条统计记录。
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`，GA002、HA018–HA045、HA065：2015个人工资实际金额、住宅和耐用品题目及第18项None。
- CHARLS官方[2015 Wave 3发布页](https://charls.pku.edu.cn/en/Data/a2015_CHARLS_Wave_3.htm)列出的2019-06-20版Codebook SHA1与本地`CHARLS_2015_Codebook.pdf`一致（`92E413C887C946A9D5C939CAB736FF96D05FC020`）；页面列出的问卷SHA1也与本地问卷一致（`DFFE2DB15D6E13CBE5499D5BF2556B17CDC8C729`）。官方发布页及发布说明没有提供`ha065_1_18_`冲突的勘误，因此它继续锁定，不按Codebook单条统计记录推断字段语义。
- `audit/personal_income_mapping_review_v1.md`已记载2015工资金额实际字段为`ga002`；本次覆核将其明确落实为目录角色处理。

## 可复现处理

`audit/catalog_role_override_review_v1.csv`增加18条精确波次停用字段规则和1条问卷/Codebook冲突规则。生成器对停用项标记`legacy_no_observations`，对`ha065_1_18_`保留专门冲突状态及`DO NOT ANALYZE`。这只影响所列2015字段，不改变其他波次同名变量或仍有官方观测记录的子字段。
