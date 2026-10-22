# 2018 HCAP 认知代码本类别扩展复核

更新：2026-10-22。根据本地官方 CHARLS 2018 Codebook 原文扩展单题值标签；只整理类别文本，不复制频数、百分比或 Codebook 汇总统计。未读取个人级回答。

## 本次字段处理

- 时间/地点定向：`dc001_w4`、`dc002_w4`、`dc005_w4`、`dc006_w4`、`dc007_w4`、`dc008_w4`、`dc009_w4`、`dc010_w4`、`dc012_w4`补入正确、错误、未评估类别。
- 2018 CSI-D单题：`dc042_w4`、`dc043_w4`补入正确、错误、不能回答类别；`dc044_w4`、`dc045_w4`保留代码本列出的不同答案等级、不可适用和不能回答，不合成单一正确/错误总分。
- 连续减法：`dc014_w4_1`–`dc014_w4_5`记录缺答/作答状态，作为C类施测/非应答元数据；代码本列出的97=Don't Know、98=Refused仅是所见类别，其他编码不推断。对应`*_1`子字段是原始数值答案，代码本最大值异常，目录明确要求授权数据核验有效范围后才能派生或评分。
- 计算工具：`dc024`的1=Used、2=Not Used是是否使用纸笔等工具，已转为C类测量元数据，不当作认知表现。
- 动物流畅性：`dc032_w4`–`dc039_w4`保留每个官方15秒区间的总数/正确数连续计数语义。代码本Mean/SD/Min/Max/Obs只作为源文档摘要；其中出现的极端最大值不作为有效范围或分析QA结论。

## 解释限制

所有值标签是逐题官方类别，不是量表评分算法。未评估、不能回答、拒绝、不会/不知道及“不适用”维持独立含义。2018 HCAP年龄适用、识字/视力/语言影响及波次间测验结构差异，仍按[`hcap_wave4_cognition_bias_guidance_review_2026-10-22.md`](hcap_wave4_cognition_bias_guidance_review_2026-10-22.md)处理。原始数值答案、跳题分母和特殊码必须在获准的发行数据上核验；没有这些核验就不建立认知总分或跨波统一分数。

规则位于 `scripts/enrich_cognition_value_labels.py`、`scripts/build_charls_atlas_catalog.py`、`scripts/build_ep_concept_source_crosswalk.py`、`scripts/finalize_catalog_semantics.py`；网站中文提示由 `site-prototype/dist/app.js` 展示。
