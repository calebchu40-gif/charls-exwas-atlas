# CHARLS ExWAS Atlas 项目范围与剩余工期（2026-10-25修订）

## 2026-10-26 RESIDENCE module full-field review (local)

对官方2014 Residence模块935条Codebook字段逐项赋予唯一去向。新增T001a/b居住段迁入/迁出时间250字段与T003e跨区县迁移间隙原因169字段两个E候选概念；T003e与T003c逐处住所迁出原因区分。95个县区/位置字段排除公开映射，不做地理或PSU联结，也不发布个人日期。模块台账及来源审计见[`life_history_residence_full_coverage_2014_v1.csv`](life_history_residence_full_coverage_2014_v1.csv)及[`life_history_residence_full_review_2026-10-26.md`](life_history_residence_full_review_2026-10-26.md)。提交`607d28a`已上线并核验；本地及线上专题44概念、1,452字段（E 1,424、P 28），535项测试通过。

## 2026-10-26 FAMILYINFORMATION full-field disposition closure (local)

对2014 Life History `FAMILYINFORMATION` Codebook 473条字段建立全模块唯一去向台账：431条候选映射，30条兄弟姐妹状态/教育暂缓，8条亲代/抚养人身份与出生年元数据暂缓，4条联结键或版本字段排除。生成器对未分类或重复字段失败关闭；专项测试验证确切行数与类别数。台账与方法记录见[`life_history_family_information_full_coverage_2014_v1.csv`](life_history_family_information_full_coverage_2014_v1.csv)和[`life_history_family_information_full_review_2026-10-26.md`](life_history_family_information_full_review_2026-10-26.md)。未改变线上目录数据。

## 2026-10-26 sensitive childhood-history metadata (local)

官方问卷E7–E8与G1–G2新增2个E候选概念、4条元数据字段。亲密关系影响与警方拘留/指控均保留条件路由；逮捕/拘留不称为定罪。后者明确高度敏感，只展示通用字段元数据，不发布参与者值、频数或叙述，任何分析须另做伦理、隐私及披露审查。逐字段台账与审计见[`life_history_sensitive_history_coverage_2014_v1.csv`](life_history_sensitive_history_coverage_2014_v1.csv)及[`life_history_sensitive_history_review_2026-10-26.md`](life_history_sensitive_history_review_2026-10-26.md)。提交`17d0c5c`已上线并核验；专题42概念组、1,033字段（E 1,005、P 28），532项测试通过。

## 2026-10-26 caregiver employment re-review (local)

复核2014 C1/C2结构化字段后，对已有的童年抚养人就业/职业概念补充跳题和缺失语义，没有重复建概念。8个字段含工作时长、务农/非农类别、失业及条件性频次；职业部门/岗位/职责的自由文本不纳入公开元数据。字段覆盖表和审计见[`life_history_parent_employment_coverage_2014_v1.csv`](life_history_parent_employment_coverage_2014_v1.csv)和[`life_history_parent_employment_review_2026-10-26.md`](life_history_parent_employment_review_2026-10-26.md)。专项测试通过，等待全套验证及发布。

## 2026-10-26 2014 parental social-context extension (local)

官方问卷C1_g1–g3与Codebook字段核对新增4个E候选概念、36条映射，涵盖父母/抚养人党员身份、少数民族身份、被选中亲属的民族类别及宗教信仰。所有相对索引字段保留家庭背景定位，不推断个人身份；C1_g3中英文选项8的抚养人指代冲突记录在字段说明和审计。2014 Life History本地目录现为40概念组、1,029字段（E 1,001、P 28）；覆盖台账与来源审计见[`life_history_parent_social_context_coverage_2014_v1.csv`](life_history_parent_social_context_coverage_2014_v1.csv)和[`life_history_parent_social_context_review_2026-10-26.md`](life_history_parent_social_context_review_2026-10-26.md)。530项测试与公共包/锁校验已通过，待部署。

## 2026-10-26 age-restricted historical family-class item

对照官方2014 Life History问卷和Codebook，将C5–C5f七种亲属形式的189个WEALTHHISTORY选项字段映射到1个E候选概念。受访者C5只问80岁及以上；亲属分支保留各自条件路由。与FAMILYINFORMATION模块中代码相似的饥荒逃荒c5严格区分。Life History目录本地增至36概念组、993字段行（E 965、P 28）；覆盖台账及解释见[`life_history_historical_family_class_coverage_2014_v1.csv`](life_history_historical_family_class_coverage_2014_v1.csv)和[`life_history_historical_family_class_review_2026-10-26.md`](life_history_historical_family_class_review_2026-10-26.md)。本批待全套验证和部署。

## 2026-10-26 parent/caregiver module extension (local)

官方2014问卷A模块复核新增3个亲代/抚养人概念和34条字段映射；47个结构化Codebook字段全部有候选映射或明确暂缓去向（8条身份/出生年字段暂缓）。Life History目录现为35概念组、804字段行（E 776、P 28），Pages线上JSON已核验。亲代死亡、离婚后再婚与丧偶后再婚分别保留；字段级台账及解释见[`life_history_parent_module_coverage_2014_v1.csv`](life_history_parent_module_coverage_2014_v1.csv)和[`life_history_parent_module_review_2026-10-26.md`](life_history_parent_module_review_2026-10-26.md)。

## 2026-10-26 sibling module expansion (local)

对照官方2014 Life History问卷和Codebook完成Section B字段审计：271个B模块Codebook字段均有明确去向，241条进入6个候选概念组，30条兄弟姐妹生存状态/最高学历字段暂缓。姓名和开放式死因不进入目录。Life History专题现为32概念组、770条字段映射（E 742、P 28）；Pages线上JSON已核验更新。完整性台账和解释见[`life_history_sibling_module_review_2026-10-26.md`](life_history_sibling_module_review_2026-10-26.md)及[`life_history_sibling_module_coverage_2014_v1.csv`](life_history_sibling_module_coverage_2014_v1.csv)。

## 2026-10-26 guardian-context local extension

官方2014问卷Section H来源审计新增4个童年抚养人背景概念和48条字段行，独立Life History目录现为26组/529行（E 516、P 13）。提交 `c433529` 已推送，线上首页和专题JSON核验26概念/529字段。女性/男性抚养人按A4a/A4b题意定义，不默认是生母/生父；条件跳题、勾选存储和男女H16罪名选项集差异均保留。详见[`life_history_guardian_health_context_review_2026-10-26.md`](life_history_guardian_health_context_review_2026-10-26.md)。

## 2026-10-26 本地增补记录

官方2014 Life History C4–C8饥荒序列来源审计新增4概念组、10字段行，独立目录由18组/471行增加至22组/481行（E 468、P 13）。提交 `1f21885` 已推送，线上首页和专题JSON已实时核验。C8选项5的双语冲突和C5–C8发布文件路由/存储验证仍开放；家庭层结局不等同个体临床表型。详见[`life_history_famine_sequence_review_2026-10-26.md`](life_history_famine_sequence_review_2026-10-26.md)。

## 状态补记（2026-10-26；提交 `0d064f1` 已部署并核验）

最新完整元数据流程 159/159 步通过，耗时7.3分钟；本地 E/P/C=6,331/2,133/1,048，E/P候选概念1,625，E/P概念—来源映射8,341条，明确标签行3,927。已修复主目录先于字段审核覆盖写盘的问题。随后对照官方2011 Codebook进一步明确：四个通用CA009槽位存在，但后缀与亲属关系未映射；问卷11项选项与Codebook类别尚未对到授权发行版编码。频数未使用或展示。该精确修订在本地目录和各JSON分片一致，提交`0d064f1`已推送并由Pages部署，线上JSON已重新获取核验四条状态。GitHub Actions API受访问频率限制，远端Validate状态暂不可查；本机526项测试及公开包、92条锁和前端校验通过。仅数据/元数据变化，应用代码缓存标记仍为v134。正式关联模型仍为0；配对共现计数不是样本量或结果。

因此，估算应分开：**目录更新与来源文档发布/核验是几天量级**；若目标仍包括完整结果型 ExWAS 分析及结果查询平台，则其开放工作不因目录建成而完成，需另外按可用数据、抽样设计和模型核验情况估时。先前几个月的说法将不同交付范围混在一起，不应作为当前目录网站的剩余工期。

## 最新进度（2026-10-26；v134 已上线并完成实时核验）

补充医疗保险候选映射已加入完整构建：17 个字段覆盖2011、2013、2018，保留方案条件路由。v134 已由 Pages 提供：主页和专属 JSON 均返回 HTTP 200，线上 JS 标记为 `app.js?v=134`，实时 JSON 中字段数、波次和标签均与审核记录一致。该确认是对静态发布内容的实时核验；本次没有独立核实远端 Validate workflow 状态。

当前网站/目录交付约完成 90%；剩余工作集中在最后的来源覆盖抽查、跨波语义和页面行为复核、交接文档同步及清理过时状态。按专注工作时间估算约 2–4 天，不按日历连续运行时间计算。结果型 ExWAS 是独立的后续扩展，当前正式关联模型仍为 0，不能将其算作目录网站尚未完成的比例。

本地完成 2015 Wave 3 养老金 payer 字段家族复核：FN074 的 option 28、FN076 的方案分支多选槽、FN075_W3_5 的补缴后年度缴费承担者、FN072_W3_5 的上年缴费承担者分别保留；修正了年度缴费字段此前被标为补缴款承担者的概念错配。新增来源审计与 4 项专项测试，补入可重复生成器，并消除了标签传播的固定行数假设。完整 159 步元数据终审耗时 7.5 分钟通过；全套 517 项测试、公开包校验、92 条锁校验和前端语法检查通过。

最新目录快照：E/P/C=6,278/2,116/1,013；1,622 个 E/P 候选概念（E=1,316，P=331，含双角色）；8,288 条 E/P 概念—来源映射；按波次的元数据候选配对=145,456/141,920/143,854/105,493/21,630。概念数和候选配对均为目录共现统计，不能当作可分析样本量或结果。提交 `67050d9` 已推送；GitHub Validate #524 与 Pages Deploy #260 成功，线上目录已核验含该批来源映射。正式关联模型仍为 0。细节见[`active_work_status_2026-10-26.md`](active_work_status_2026-10-26.md)和[`pension_2015_payer_item_context_review_2026-10-26.md`](pension_2015_payer_item_context_review_2026-10-26.md)。

## 先区分当前目标与扩展目标

用户质疑“还需数月”的估算后，重新核对了当前目标记录。原定工作重点是：按 NHANES PE Atlas 的方法结构扩展 CHARLS 候选暴露/表型目录、逐波映射官方变量和来源标签、更新可查询的网站与交接文档；不得违反 CHARLS 数据许可，也不得发布未经验证的关联结果。**这不是要求在没有权重/设计资料时先跑出关联结果。**

此前提到的“数月”把完整的结果型 ExWAS 研究扩展目标也算进来了，作为当前目录网站任务的剩余时间不准确，现予更正。

## 当前公开交付

截至 2026-10-26，网站 v134 已部署并核验；最新状态和验证结果见 [`active_work_status_2026-10-26.md`](active_work_status_2026-10-26.md)。下列较早统计是历史快照，不代表当前目录状态。

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
