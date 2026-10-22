# 2018 HCAP 认知字段类别与施测元数据复核

更新：2026-10-22。范围限于 CHARLS 2018 官方 Codebook 明确列出的认知项目类别、非应答原因和测验施测条件字段。没有读取个人级回答；Codebook 的频数和百分比未转录到目录或网站。

## 核验结果

官方 2018 Codebook 为 `dc018_w4`（短句复述）、`dc019_w4`（阅读并按指令操作）、`dc020_w4`–`dc022_w4`（多步骤动作）、`dc023_w4`（书写句子）及 `dc024_w4`（五边形临摹）列出正确、错误和未评估类别。已将类别写入认知字段映射和网站字段目录。`dc019_w4`另有“受访者闭眼后正确”与“访员读出后正确”两种正确路径，保留为独立类别，不压成单一二元分数。`97=Not Assessed`单列，不当作错误。

同一 Codebook 为 `dc028_w4_1` 列出类别1、3、4、5（拒绝、年老后无法作答、耳聋、其他）；代码本没有列出编码2，因此页面只显示这四个明示类别，并注明代码2及类别完整性未获确认。四个 `dc031_w4_s1`–`s4` 多选槽分别记录“口头施测”“施测中断”“受访者阅读词语困难”“以上皆无”。这些回答描述非应答原因或测验条件，不是认知表现。已将这五个字段由 P 候选改列 C 类认知施测/非应答元数据，排除于 E/P 关联矩阵；网站仍保留编码供解释缺失机制和施测差异。

## 方法边界

- 类别根据 2018 官方 Codebook 原文转录；`dc019`将 Codebook 的“read out loudly”简写为“instruction was read aloud”，仅用于类别显示。`dc028_w4_1`仅显示 Codebook 明列类别，不推断未列出的编码2。
- 没有从相邻波次推断类别，也没有依据代码本样本频数判断可分析性。
- 2018 HCAP 的年龄适用、识字/视力/语言影响及记忆测验跨波限制，继续遵循[`hcap_wave4_cognition_bias_guidance_review_2026-10-22.md`](hcap_wave4_cognition_bias_guidance_review_2026-10-22.md)。
- 该复核只完善字段语义，不批准认知总分、跨波合成、样本限制或关联模型。题目路由、问卷施测和授权发行数据中的缺失码仍须在分析方案阶段核验。

## 可重复构建与验收

规则位于 `scripts/enrich_cognition_value_labels.py`、`scripts/build_charls_atlas_catalog.py` 和 `scripts/build_ep_concept_source_crosswalk.py`，均由 `scripts/build_ep_atlas_metadata.py` 调用。构建后 12 个目标字段（7 个认知表现题、1 个非应答原因字段、4 个施测条件槽）均有官方类别标签；`dc028_w4_1`及4个 DC031 槽为 C 类，明确标记排除于 E/P。28 个网站 JSON 均可解析，`node --check site-prototype/dist/app.js` 通过，分析锁定清单仍为 33 条且逐项校验通过。
