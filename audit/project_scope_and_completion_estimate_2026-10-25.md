# CHARLS ExWAS Atlas 项目范围与剩余工期（2026-10-25修订）

## 先区分当前目标与扩展目标

用户质疑“还需数月”的估算后，重新核对了当前目标记录。原定工作重点是：按 NHANES PE Atlas 的方法结构扩展 CHARLS 候选暴露/表型目录、逐波映射官方变量和来源标签、更新可查询的网站与交接文档；不得违反 CHARLS 数据许可，也不得发布未经验证的关联结果。**这不是要求在没有权重/设计资料时先跑出关联结果。**

此前提到的“数月”把完整的结果型 ExWAS 研究扩展目标也算进来了，作为当前目录网站任务的剩余时间不准确，现予更正。

## 当前公开交付

截至 2026-10-26，网站 v127 已部署；当前本地 Part H/K 更新尚待发布。最新本地状态和验证结果见 [`active_work_status_2026-10-26.md`](active_work_status_2026-10-26.md)。

- 本地 E/P/C 目录行：6,008 / 2,107 / 982。
- 本地 E/P 候选概念：1,554（E 1,251、P 328，含 25 个双角色概念）；概念—来源映射 8,009 条。
- 本地 E/P 目录记录 8,115 条、波次—字段 7,902 个；明确标签 3,763 条，通用待审核标签状态为 0。
- 2020 疫情模块：E 52 个字段/25 个概念，P 25 个字段/25 个概念；100 个字典字段均有覆盖去向（77 个 E/P 候选，23 个非 E/P 字段逐项说明）；2020 候选配对 21,006 是目录共现，不是样本量或模型结果。
- 正式分析锁 92 条，未改变；关联模型和参与者层面的结果仍为 0。
- 本机与干净检出476项测试、公开包校验、前端语法、延迟加载检查及精确92条分析锁校验全部通过；GitHub Validate #500、Pages Deploy #247 均成功。没有上传参与者数据或 Codebook 分布统计。

## 完成度和估算

下面的比例按工作包主观估算，不按字段/概念条数直接换算：

| 范围 | 当前完成度 | 预计剩余 |
|---|---:|---:|
| 候选变量元数据图谱、官方来源映射、查询网站和交接资料 | 约 85–90% | 约 2–4 个专注工作日 |
| 完整结果型关联图谱（含调查设计、模型、复核和网站结果接入，不含论文写作） | 约 50–55% | 约 3–6 个专注工作周，前提是分析所需数据和设计输入到位；外部等待另计 |

当前目录目标剩余工作主要是发布并核验 Part H/K 更新、完成最后的来源覆盖核对、复核跨波映射与页面呈现、补齐版本与交接记录。目录站点进度与真实关联模型进度分开报告，避免再次混为一个工期。若覆盖审计发现新主题或原数据字典冲突，估时应相应调整。已完成的公开目录和网站不需要从头重做。

扩展目标的主要开放闸门是 CHARLS 官方 2013 `Weights.dta` / 样本标记、2015 独立 Blood Data 发行文件，以及各波 PSU/方差分层或可接受方差方案。文件可得并且设计方案明确后，才能确定一对变量在某波次是否能估计。未取得这些输入时，不能把分析阶段的时间写成确定的完成日期。

## 为什么前次估算偏大，以及耗时点

之前的数月估算覆盖了更宽范围：恢复所有原始发行包、完整候选变量扩展、调查设计闭环、真实模型、多重检验/敏感性、结果披露和网站接入。它不等于当前元数据网站的剩余工期，也不包括用户本次明确排除的论文写作时间。

当前工作慢的主要是源级核对和反复的细粒度迭代，而非网页本身。CHARLS 候选字段跨个人、家庭、社区、体测和血检模块；同名变量可能因波次、路由、参照期或测量单位不同而不等价。NHANES 代码和页面结构可作为模板，但不能代替 CHARLS 的正式文件、链接键、权重或调查设计判断。流程问题确实存在：早期在字段覆盖检查中分散发现遗漏，导致重复全量终审；后续改为按完整问卷模块批次审计，一批结束后再做一次全量构建，纯文档或界面调整只跑定向验证。

2026-10-25 这轮因为在完整性检查中先后发现 VA007、VB009、VB012，重复跑了几次约 9–10 分钟的全量目录终审。这是流程可以改进之处。后续先成批完成一个主题的来源覆盖审计，再集中运行一次终审；局部文档变化只运行相关校验，避免无必要的重复全量构建。


2026-10-25 后续增补：根据五波原始字段清单与 2011/2013/2015/2018 官方问卷、Codebook，加入家庭经济支持收支 6 个候选概念，跨波保留家属槽位、货币/实物、定期/非定期及区间端点差异；完整复核后 E 目录行增至6,008，候选概念增至1,554，E/P概念—来源映射增至8,009。全量终审耗时8.6分钟。


## 2026-10-25 后续审计修复

家庭经济支持的字段级 caveat 曾在逐字段循环中累积到约 28 KB；改为每字段从概念级基础说明独立生成后，单行最大 515 字符。重建后 E/P/C 目录数、概念数与配对共现总数保持不变，明确标签增加至3,763；交叉表、候选配对 JSON 和 E 分片分别减少约19.5 MB、19.4 MB 和39.1 MB。另修正 Markdown 摘要器对未声明 `tabulate` 的隐式依赖。测试新增 caveat 防膨胀断言；完整终审 157 步、476 项本地测试均已通过。v126 已由 GitHub Validate #500 和 Pages Deploy #247 验证并发布。


## Current state update (2026-10-26, v127 prepared)

The 157-step metadata finalization now includes 11 exit-module mortality field mappings (2013 and 2020 only) and an explicit catalog synchronizer for their source-specific value-label state. Final local shards are E/P/C=6,008/2,116/984; the concept mapping audit reports 1,557 E/P candidate concepts and 8,018 E/P concept-source mappings. Mortality calendar metadata is C, the other fields are P candidates, and all remain decedent/proxy-reported with no formal model or survival denominator. Metadata pair availability is not analytic N. The website update is deployed as app v127 (commit `7b00491`); Validate run `40213942542` and Pages Deploy run `40213942548` succeeded and live mortality fields were verified.


## 2026-10-26 local directory update

A source review of the 2011 Community Questionnaire and Codebook added two provisional community-level elder-care exposure concepts (12 wave-field mappings). The finalization workflow now has 158 steps. Local counts are E/P/C=6,020/2,116/984, 1,559 E/P concepts, 8,030 E/P concept-source mappings, and 3,740 explicitly labeled E/P rows; the 2011 metadata pair index is 132,889 (co-availability only). The website currently deployed as v127; this verified local update is pending commit/deployment. Current verification: 482 tests and 90 subtests pass; public payload, 92 analysis locks, JavaScript syntax and diff checks pass. The two elder-care concepts are not respondent-level service-use measures or approved adjustment covariates.

## 2026-10-26 second community source-review batch

Reviewed official 2011 Community Questionnaire Part J and Codebook. Added three provisional community-level E concepts and 13 fields: economic/fiscal context (JJ011-JJ016), housing-market context (JJ026-JJ030), and formal-credit access (JJ031-JJ032). Preserved reference year, field-specific units, village-only routes, the exclusion of household income from JJ014, and the English/Chinese lender wording difference for JJ032. These are contextual aggregates, one-wave candidates; they are not the respondent's own income, housing, credit or debt. Full review: `audit/community_economic_housing_credit_source_review_2026-10-26.md`.

The complete 158-step rebuild now contains E/P/C=6,033/2,116/984 rows, 1,562 E/P concepts, 8,043 E/P concept-source mappings, and 3,741 explicitly labelled E/P rows. The 2011 metadata co-availability count is 133,528; this is not analytic N. Exact 92 analysis locks remain; formal models and pairwise-complete N remain 0. Local unittest suite: 480 tests pass; public-payload, 92-lock, JavaScript/deferred-loader and diff checks pass. The new economic/housing/credit batch is locally verified and awaits push/deployment; the public site currently contains the prior elder-care update.

## 2026-10-26 Part J coverage follow-up

The economic/fiscal, housing-market and credit batch was published by GitHub Pages Deploy #250 (commit d40a4fa); Validate #507 and Deploy #250 both succeeded. The subsequent official-source sweep found JJ005 missing from the 2011 community agricultural-context mapping. Added it as a conditional, nominal service-supply context candidate and documented all 49 substantive Part J source fields (JJ001–JJ032) as mapped, while excluding direct identifier/admin fields JJ033–JJ035. The conditional JJ005 locality text is not treated as standardized geography. The value-label propagation rule now applies official questionnaire categories rather than leaving a false generic-pending status.

Current local rebuild: 158/158 steps; E/P/C=6,034/2,116/984; 1,563 E/P candidate concepts; 8,044 concept-source mappings; 3,742 explicitly labeled E/P rows; zero generic pending E/P/C labels; 2011 metadata co-availability=133,741 (not analytic N). Exact 92 analysis locks remain. Formal models and pairwise-complete N remain 0. Full pytest: 485 passed, 90 subtests passed; public-payload, 92-lock, JavaScript syntax and deferred-loader checks pass. The JJ005 update and Part J audit await commit/deployment.


## 2026-10-26 FN097 and full-rebuild propagation update

Reviewed official FN097 source wording, categories and routing for 2013/2015/2018. The five response labels now persist through the codebook-label builder; 2018 wording and pension-screen denominator are kept distinct. Also fixed final propagation for continuous community household counts and alcohol C context metadata. Full rebuild: 230 steps in 8.1 minutes; E/P/C=6,034/2,116/984; 1,563 concepts; 8,044 concept-source mappings; 3,774 explicitly labeled E/P rows; generic pending E/P/C labels=0. Local unittest suite: 483 passed; public payload and exact 92-lock checks passed. This update has not yet been pushed. The completion estimate for the current metadata website delivery remains approximately 80% / 3–7 focused days (1–2 calendar weeks); the full result-producing ExWAS remains a separate downstream scope gated by survey design inputs.
