# 2013/2015 前波慢病诊断年龄预载字段复核

更新：2026-10-24。复核 2013 与 2015 候选目录中的 33 个 `ZDA009_2*` 字段（2013 为19条，2015为14条），仅使用官方问卷、Codebook 和本项目字段元数据。

两波问卷都把 `ZDA009[i]` 列在前波健康记录/预载上下文中，题意为“该状况何时首次诊断或由本人知悉”，并引用上次访谈时间 `ZIWTime`；各波 Codebook 将匹配的 `ZDA009_2*` 字段标为 `Age`。因此这些记录是上一波该诊断/知悉时间答案中的年龄分量，不是当前波新测的结局，也不能因代码标签含 `Age` 就当作普通年龄协变量。2018 的同名家族已经改为“上一波是否回答过该题”的历史标记，不能跨波直接套用同一语义。

目录将这33条从自动协变量关键词线索改为 C 类“前波诊断时间预载值”测量元数据；不生成类别标签、不加入同波 E/P 配对，也不把不同疾病索引合并为单一构念。正式纵向使用前，仍须在获准发行版核实预载值、ID链接、特殊码与疾病索引。没有读取个人回答或 Codebook 频数。

可复现更新器：`scripts/apply_prior_wave_diagnosis_age_preload_review.py`。字段清单：`audit/prior_wave_diagnosis_age_preload_crosswalk_v1.csv`。来源：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`、`CHARLS_2013_Codebook_extracted.txt`、`CHARLS_2015_Questionnaire_extracted.txt`、`CHARLS_2015_Codebook_extracted.txt`。
