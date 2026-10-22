# 家庭其他资产租赁收入逐波映射与题义边界（2026-10-21）

## 核对结论

CHARLS公开字段目录显示，2011、2013、2015、2018都有`ha064`/`ha064_1`；2020对应`ge014`/`ge014_1`。它们询问房屋和土地以外的家庭资产（如树木、生产性固定资产、耐用品、牲畜）租赁收入，适合加入网站候选目录，但波次响应格式和金额时段并非完全一致。

- 2011、2013、2015：Codebook把`ha064`列作“Any Rental Income”或“Income for Renting Out Other Assets”，选项为`1=Yuan`、`2=Not applicable`；`ha064_1`为租金金额。故`ha064`进入C类响应格式/适用性元数据，不把码1当作二元收入状态。三轮题干缺少可确认的统一时间窗说明，金额留在统一搜索概念中但保留波次，并明确禁止直接合并或年化。
- 2018：问卷明确询问过去一年，范围排除住房和土地；`ha064`为Yes/No/Don't know/Refused状态，`ha064_1`为条件金额。状态可以与2020 `ge014`放在同一候选状态概念下，仍保留各波标签和状态定义。
- 2020：官方英文问卷的`GE014`询问同一类其他家庭资产，答案包括Yes（`GE014_1`金额）、Not applicable、Don't know和Refuse。金额题干没有明确过去一年时间窗，故单列2020金额概念，不擅自与2018年度金额合并。Codebook所列类别频数未复制或用于分析。

本批新建2个E概念（2011–2018金额、2018/2020状态），新增5条E字段映射和3条C类选择器字段映射。2020 `ge014`/`ge014_1`从原单波概念调整到新的跨波状态/金额概念组织中；概念总数净增加2，E/P链接净增加7。所有字段仍是待核验候选，缺失/跳题不等同于无收入或零金额；金额估计需在合规获批数据中逐波核对路由、特殊缺失、家庭层级和有效分母。

## 官方来源

逐波Codebook文件：`sources_official/CHARLS_2011_Codebook_extracted.txt`、`CHARLS_2013_Codebook_extracted.txt`、`CHARLS_2015_Codebook_extracted.txt`、`CHARLS_2018_Codebook_extracted.txt`和`CHARLS_2020_Codebook_extracted.txt`。问卷题页已核对2013、2015、2018和2020英文问卷；2011基线问卷对应文件为`CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`，2011字段/响应格式判断仅据Codebook与公开变量目录，不主张该摘录中已有逐字可核的英文题页。

可重建脚本：`scripts/build_household_other_asset_rental_income_crosswalk.py`，并由`python scripts/build_ep_atlas_metadata.py`自动执行。结果分别写入金额、状态和C类选择器crosswalk，以及网站JSON元数据。
