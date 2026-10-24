# 2013 生殖史前波次预载字段复核

更新：2026-10-24。复核 2013 候选目录中的 `ZDA026_2` 与 `ZDA028_2`，使用 CHARLS 官方 2013 问卷与 Codebook，不读取受访者记录或 Codebook 频数。

2013 问卷将 `ZDA026` 定义为上一轮初潮时间，将 `ZDA028` 定义为上一轮绝经时间，并注明 `ZDA027` 的既往绝经状态。Codebook 将 `_2` 字段分别标为初潮年龄和年龄；`ZDA026_2` 的存储类型为字符串。故这些字段适合作为前波历史元数据保留，不能当作 2013 新测暴露/表型，也不能视作普通当前年龄协变量。

目录将两条记录留在 C 类测量/调查元数据中，不生成类别标签，不推断跳题值，也不加入同波 E/P 配对。未来纵向分析前仍需在获准发行版核实变量身份、解析规则、个体链接和特殊值。此审计不改变此前对直接 `DA026_2`/`DA028_2` 候选暴露的范围、女性限定、问卷路由或可分析性判断。

可复现更新器：`scripts/apply_reproductive_history_preload_metadata_review.py`。字段清单：`audit/reproductive_history_preload_metadata_crosswalk_v1.csv`。官方来源：`sources_official/CHARLS_2013_Questionnaire_extracted.txt` 与 `sources_official/CHARLS_2013_Codebook_extracted.txt`。
