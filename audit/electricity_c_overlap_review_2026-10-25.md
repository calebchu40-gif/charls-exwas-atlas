# 住宅电力可及性 C/E 重叠字段同步（2026-10-25）

将2011、2013、2018年精确波次 `I016` 的 C 目录行链接至已审核的 `electricity_access` 暴露候选。更新器要求字段同时存在于 E 与 C 角色，并核验对应官方问卷、Codebook文件以及既有来源交叉表的问卷措辞、家户指称、Yes/No类别和限制说明。

此字段只表示住宅/家户是否有电，不代表受访者个人剂量、用电可靠性、时长、电力来源或室内空气污染。参与者与家户链接、符合条件的分母、授权发行版特殊缺失码和跨波可比性仍需后续核验。C角色保留用于来源与测量设计查询，不是默认协变量；该字段本身作为目标E时不得用于调整自身。2015字段在已有交叉表中没有逐字段代码本证据，2020项没有进入本批E/C精确重叠集合，因此未同步。

字段级记录见 [`electricity_c_overlap_review_v1.csv`](electricity_c_overlap_review_v1.csv)，已有E来源定义见 [`food_environment_crosswalk_v1.csv`](food_environment_crosswalk_v1.csv) 和 [`electricity_bathing_source_review_2026-10-25.md`](electricity_bathing_source_review_2026-10-25.md)。
