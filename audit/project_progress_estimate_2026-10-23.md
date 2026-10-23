# CHARLS ExWAS Atlas 项目进度与剩余工作估算（2026-10-23）

## 结论

按“完成五波候选目录审计、预先定义分析方案、按正确调查设计估计ExWAS关联、完成质控并将获准发布的结果接入交互网站”作为完整目标，目前总体约完成 **25%–30%**。这是按里程碑和工作量作的项目估算，不是能从字段行数直接计算的精确比例。若交付范围仅为可公开访问的候选元数据查询网站，则该首版已完成并上线；这不等于统计关联图谱已完成。

## 当前证据

- 首版公开站点已部署：<https://calebchu40-gif.github.io/charls-exwas-atlas/>。GitHub Pages工作流已多次成功；最近一次部署见Actions run #32。站点首页、JavaScript和候选配对元数据均通过外部HTTP 200检查。
- 五波候选目录当前包含7,542条波次字段记录、1,408个去重E/P候选概念（E侧1,130、P侧287、双角色9）和6,598条E/P概念—源字段映射。已生成候选配对检索页，但目录层配对不代表实际同一受访者样本量或统计模型。
- E/P字段目录当前有3,207行非空已审/官方类别标签文本、覆盖3,181个波次—字段码；633个目录角色行仍显示`not yet reviewed`。该指标只覆盖类别标签文本，不衡量连续变量的问卷、测量、路由或分析资格审查完成比例；慢病自知/疾病变化/控制字段已有逐波类别，但未关闭它们的发行版编码与适用分母审核。
- 公开站点当前正式关联模型数为0；没有公布任何效应估计、显著性或发现。
- 测量与设计元数据（C）目录共913条，其中427条为协变量候选、486条为测量元数据。`Value.Label.Review`中331条显示`not yet reviewed`。网站所见2011筛选结果70条，是2011年协变量候选子集，不是全项目待办数。C类中的仪器/流程/路由/选择器记录本来就不属于E/P配对；717条C记录没有E/P候选Concept ID，也不能全部视为漏映射。
- [`audit/current_directory_snapshot_2026-10-23.md`](current_directory_snapshot_2026-10-23.md)记录当前仍有35条逐波字段保持`DO NOT ANALYZE`。权重、方差分层/替代方差方法、目标人群、各模块样本资格及跨波构造均须在实际分析前逐项关闭。

## 完成情况按阶段拆分

| 阶段 | 当前状态 | 对完整目标的解释 |
|---|---|---|
| NHANES方法/CHARLS官方材料梳理及工作规则 | 已建立第一版依据与审计流程 | 仍需按新增变量领域持续补充 |
| 五波目录、候选E/P概念和来源映射 | 已有完整第一轮宽目录 | “已映射”不等于人工确认题意、编码和分析资格 |
| 逐变量标签、路由、测量对象、波次可比性审计 | 持续进行 | 大量字段仍是自动发现或待人工核验；C类示例见上 |
| 抽样设计与分析计划冻结 | 未完成 | 是开展推断分析的前置门槛 |
| 合成数据管线验证和正式关联扫描 | 尚未完成；正式模型数0 | 当前没有结果可展示或解释 |
| 公开交互网站 | 元数据原型已公开上线 | 真实结果界面、披露审查和结果接入尚未完成 |

## 剩余工期估算

按一名研究者每周约5个工作日的专注投入，并假设可及时使用合规数据、官方调查设计材料能解决关键疑点：

- 收敛并冻结核心E/P变量、波次构造、答题路由和特殊缺失规则：约2–4周。
- 关闭目标人群、权重、PSU/方差处理和模块样本资格，完成可复核的分析计划：约1–2周；如需等待官方答复则另计。
- 合成数据验证、核心扫描、设计/模型诊断、敏感性分析和结果复核：约3–6周。
- 扩展完整候选目录、处理长尾变量并为网站完成结果级说明/披露审查：约4–8周或更久。

综合估计，从当前状态到较完整、可解释的结果型ExWAS Atlas，约需 **4–6个月全职有效工作**；若兼职推进，约 **6–12个月**。如果数据版本/模块缺失、统计设计限制无法解决或需要额外审批，日历时间会更长。首版网站已上线，因此上述剩余时间重点在变量审计、设计闭环、模型分析和结果验证，不是网站静态托管设置。

## 当前优先顺序

1. 继续按领域审计E/P候选，先冻结一批有清楚题意、目标人群、响应定义和可用权重的核心变量；对不清楚的字段维持锁定或排除。
2. 重新核对当前可用的合规数据发行版、波次模块与权重；不从公开Codebook摘要或访员/社区代理信息推算个体暴露。
3. 关闭设计和变量闸门后，用合成数据验证统一结果表及错误处理，再开始核心关联扫描。
4. 复核估计、有效样本、缺失/路由、权重与多重检验后，只向网站接入允许披露的汇总结果；保留元数据页和结果页的状态区分。

## 2026-10-23续记：网站更新与批处理队列

- C类目录说明已改为中文，并解释“尚未逐项核验”不等于每个字段都应有离散值标签；连续变量可能没有类别标签，协变量候选也不是自动调整建议。公开站点已更新并验证可访问。
- GitHub Pages现会在`main`分支的`site-prototype/dist/**`或部署工作流发生变化后自动发布，同时保留手动触发入口。此次提交`d6ea37b`已推送；本地回归测试51项全部通过。
- 为提高审计效率，按目录字段行而非独立构念分组待办：E侧1,452行待值标签核验，其中养老金419、收入/财富196、就业/职业140；P侧467行，其中疾病治疗响应260、医疗利用151、自知疾病17、医生诊断时间8。它们不能直接解释为1,919个新指标，也不能全部按“缺标签错误”处理：连续量、年龄/日历年、复选框和条件性治疗题需要不同核验规则。
- 下一批优先按官方题组与波次批量核对P侧疾病治疗和医疗利用，再处理E侧养老金、收入财富、就业题组。每批先把问卷题意、答案结构、跳题和代码本呈现一起核，再判断应补标签、保留连续单位、转C类或继续锁定；不把已审构念的重复槽位当新增指标。



## 2026-10-23 follow-up: methods transparency and navigation

The published homepage now has a dedicated survey-design disclosure covering wave-specific weight/sample-flag gates, the 2013 source-flag rebuild requirement, the provisional `communityID` PSU match, and the lack of a verified variance-stratum/replicate-weight field in currently reviewed project sources. The C-class catalogue navigation is labeled “measurement/design metadata” so it is not confused with the methods note. Both changes are live on GitHub Pages; the full result atlas remains at 0 fitted association models. Overall completion against the full result-atlas objective remains approximately 25%–30%; this website clarity work does not close analysis or data-access milestones.

2026-10-23续记：目录构建器通过预建波次—字段查找索引，同一`cProfile`方法下从107.8秒降至53.6秒，输出记录语义相同；性能审计见[`metadata_builder_performance_2026-10-23.md`](metadata_builder_performance_2026-10-23.md)。此前补入2013/2015/2018的48个疾病控制/既往访谈变化字段，修复2020既往访谈变化18个字段的目录标签传播，并为2011/2020的6个自知疾病字段补入逐波标签。本轮又补入2013–2018的11个自知疾病字段，并为22个连续残疾发生年份字段注明calendar year。E/P非空标签行现为3,207（3,181个波次—字段码），仍有670行通用待核状态；C类331行仍为通用待核状态。全目标完成度仍估25%–30%，因正式关联模型数仍为0、抽样设计与个体变量审核闸门未解决，这类目录补全不代表结果图谱已接近完成。后续继续审阅候选目录，并优先处理调查设计闭环、变量冻结和合成数据验证。

私有派生表权重覆盖QA续记：2015/2018/2020横截面标记与正个体权重覆盖一致；2011个体权重全覆盖但没有独立横截面标记。2013现存派生表中18,605人只有18,256人有正的个体权重，且缺少`crosssection`/`longitudinal`资格变量。验证器已加强为将2013标记为`CHECK`，70项测试通过；2013官方原始Weights源包须恢复后才能重建与解释。逐波权重覆盖计数见[`survey_design_weight_review_v1.md`](survey_design_weight_review_v1.md)。这是调查设计闸门证据更新，不改变完整结果型Atlas约25%–30%的里程碑估算。


## 2026-10-23 follow-up: behavior continuous-measure synchronization

A full metadata rebuild found that 73 already-audited continuous behavior fields had remained labeled `not yet reviewed` in the main catalog. The catalog builder now propagates the source review status only to blank-label rows still in that generic pending state, preserving conflicts and analysis locks. The E/P catalog has 3,102 rows with nonempty reviewed/official labels (3,076 wave-fields) and 978 E/P rows remain `not yet reviewed`; neither count measures analysis eligibility. The C catalog has 338 generic-pending rows. Source-status propagation marks 608 pension numeric/count fields as located in the official Codebook with no discrete categories; six entries with more specific existing review states were preserved. A further 51 household-income/expenditure fields have exact Codebook numeric-summary entries, and five wave-specific wage-receipt menus now show `1=Yes; 2=No` without frequencies. These updates do not confirm units, routes, release coding, or analysis eligibility. See [`pension_numeric_status_sync_2026-10-23.md`](pension_numeric_status_sync_2026-10-23.md) and [`income_numeric_and_receipt_label_sync_2026-10-23.md`](income_numeric_and_receipt_label_sync_2026-10-23.md).


2026-10-23网站加载复核：旧版23个前端数据请求现都延迟到对应视图打开时；主目录另分为E（15.46 MB）、P（6.40 MB）、C（1.93 MB）三份并只在进入对应目录时请求。默认首页不请求目录JSON，Pages产物排除主目录副本；ETag使用`no-cache`重新验证缓存。正式finalize-only管线会重新生成分片，部署/验证工作流已加入对应规则。73项Python测试、延迟加载Node测试、前端语法与分片一致性均通过。此改动提升目录原型的首屏和按角色浏览效率，不改变候选指标或结果平台完成度（仍约25%–30%）。详见[`site_static_asset_cache_review_2026-10-23.md`](site_static_asset_cache_review_2026-10-23.md)。

2026-10-23续记：就业/工作暴露交叉表中170个此前通用待核字段已同步为有来源的连续/开放响应或无离散类别状态；另将5个2020 CAPI派生公式和2个问卷/Codebook身份冲突的标签及状态同步至主目录。后两类仍保留路由待核或`DO NOT ANALYZE`，不表示分析资格已验证。当前E/P目录有3,207行非空官方/已审标签文本（3,181波次—字段码）、670行通用待核状态；84项测试通过。目录和网站变更正准备推送。完整目标完成度仍约25%–30%，正式关联模型数仍为0，分析设计与2013样本标记等门槛未解决。相关审计见[`work_numeric_catalog_status_sync_2026-10-23.md`](work_numeric_catalog_status_sync_2026-10-23.md)。

2026-10-23追加：另将工作/就业目录33条2011逐波字段的“官方代码本类别标签未定位”状态连同代码本来源写入主目录及网站。该状态只说明已提取的官方Codebook中未检出类别标签，并不表示字段没有类别；问卷菜单、特殊值、单位、路由和发行版编码仍须分别核验。当前E/P目录通用待核行降至637，非空官方/已审标签行仍为3,207；85项测试通过。

2026-10-23继续：复核吸烟戒烟时间格式选择器。2013、2015、2018、2020选择器转入C类；2018 DA062两个子字段因问卷与Codebook年龄/年份标签反向而锁定。更新主目录、跨表、网页分片、审计和回归测试。86项测试、前端语法及延迟加载器均通过；本批尚待推送触发Pages部署。该修正只加强目录正确性，不改变正式关联模型数（仍为0）或整体完成度估算（25%–30%）。
