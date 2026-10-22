# 历史中间目录快照（2026-10-22，2018养老金残余复核后）

本文件记录当天较早阶段的中间构建状态，已被[`current_directory_snapshot_2026-10-22.md`](current_directory_snapshot_2026-10-22.md)中的后续完整构建状态取代；请勿将本文件中的计数当作当前值。

- 网站字段目录：7,454行（E 4,578、P 1,861、C 851、双角色E/P 164）。
- E/P候选概念：1,401个（E侧1,131、P侧279，双角色概念9）；E/P源字段映射6,534行。
- 全来源crosswalk：6,711行，6,699条匹配目录，12条目录外字段均为C元数据。
- 未映射E字段：2011、2013、2015、2018、2020均为0。
- 波次元数据概念对共现：2011 115,500；2013 119,778；2015 122,868；2018 95,993；2020 12,598。只代表目录元数据中可同时出现的概念对，不是有效样本量、模型N或分析结果。
- 2011养老金转入问题区分当前领取者FN015/FN016与已参保者FN065/FN066；2013/2015路线按题目对象、计划和条件跳题保留。2013六个字符串待遇Min/Max区间边界明确禁止转为数值金额。
- 2015 FN068问卷页复核更正：计划特定的初次开展年龄资格及子女参保要求作为E候选；子女名册槽位为C，不公开身份。
- 2018养老金残余审计完成：来源/参与地点的粗分类保留为E候选，并区分待遇领取与计划参保、生活保险与养老金以及每个正式计划循环。FN006_W4/FN007_W4带数字后缀字段依据Codebook类别确认为循环中的粗分类，不是个人详细地址。支付周期/金额形式选择器及展开区间边界改列C；不得把区间边界当作金额、均值或独立暴露。
- 官方样本设计/权重复核：Wave 4提供HH_weight、HH_weight_ad1、INDV_weight、INDV_weight_ad2，cross_section字段标识横截面样本；没有Wave 4 panel weight。2013另提供横截面biomarker weight；2018无生物标志物，HCAP为60岁以上专门认知测试。PSU信息沿用早期文件，但显式方差分层变量/完整SE方案尚待授权文件核实。详见[`charls_wave_sampling_and_weight_status_2026-10-22.md`](charls_wave_sampling_and_weight_status_2026-10-22.md)。
- 完整重建成功，`python -m py_compile scripts/build_pension_exposure_crosswalk.py scripts/apply_catalog_role_overrides.py`与`node --check site-prototype/dist/app.js`通过。映射仍属于候选目录，不代表已验证关联或分析资格。没有读取受访者微观记录，没有拟合模型。

详细审计：[`pension_2015_residual_review_2026-10-22.md`](pension_2015_residual_review_2026-10-22.md)、[`pension_2018_residual_review_2026-10-22.md`](pension_2018_residual_review_2026-10-22.md)。
