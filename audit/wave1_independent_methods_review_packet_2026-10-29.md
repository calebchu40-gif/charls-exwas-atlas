# Wave 1 设计与105项试点：独立方法审阅材料

**最后更新：2026-10-30**

**状态：当前审阅候选待独立调查抽样/生物统计审阅；未获模型运行或结果发布批准。**

**本材料的现行方案更正：**下方旧段落曾把 age≥45、Harmonized CHARLS D 年龄、`communityID` 单层聚类写作当前方案；这些属于历史探索运行或已被替代的候选，不能用于当前 readiness 文件。当前目标人群审阅候选为官方完整 Wave 1 血检目标（主访者及配偶）与 `bloodweight`，45+作为次级 survey domain；年龄来自官方 DOB/访谈时间，区间构造及上下界敏感性仍待审阅。**目前没有优先或已批准的方差方案。**county-prefix 顶层簇 Taylor 近似与县内 community 条件敏感性只作为未批准的审阅选项，不能视为当前推荐设计。当前准入证据与门槛见本页及 [`wave1_biomarker_estimand_age_recommendation_2026-10-30.md`](wave1_biomarker_estimand_age_recommendation_2026-10-30.md)、[`wave1_variance_review_recommendation_2026-10-30.md`](wave1_variance_review_recommendation_2026-10-30.md)。

本材料汇总当前可核实的方法信息及尚需决定的事项，供具备复杂抽样调查经验的审阅人评估。材料不含 CHARLS 参与者记录、样本计数、逐对结果或本地哈希。

## 当前可核实的证据

- 官方设计页面/用户手册将 Wave 1 说明为分层多阶段 PPS：县级单位按地区、城乡和 GDP 组织/抽取，再在每个县抽取3个社区；超过2,000户的大社区可拆分子社区作为最终 PSU，约30个社区采用了这一做法。选中45+主受访者后会访问其配偶，因此设计框内存在低于45岁的配偶；分析45+目标域需在设计对象中作 domain/subpopulation，而不能先物理删行。
- 官方用户手册说明 household/individual weights 来自各阶段抽样概率，并有非应答校正版本；血检另有校正血检非应答的 individual weight。对子社区抽样，权重还乘入子社区占父社区的份额。该权重支持目标点估计权重选择审阅，但不携带每位受访者所属最终子 PSU 的映射，不能单独解决方差估计。
- **受保护的血检权重连接复核（2026-10-30）：**按当前候选估计量，实际分析权重取 Blood 文件内的 `bloodweight`，不取主问卷 `ind_weight_ad2`。仅读取 ID/权重列的键值核对确认，Blood 发布记录的 `bloodweight` 均为非缺失正值，并全部链接到当前人口学个人主表；Blood 发布记录数与官方 Blood Guide 报告的完整血样数一致。因此，血检文件—生物标志物权重—个人主表的字段连接已通过。官方完整血检目标与个人主表之间仍有总体分母的小幅差异，且 `ind_weight_ad2` 存在未匹配 ID；该项保留为非血检权重分母的附属来源问题，不把它混同为 `bloodweight` 连接失败。此核对没有读取暴露或结局值，也不证明暴露模块应答覆盖、年龄域或方差设计正确。
- 设计是嵌套多阶段，而非单一社区聚类：官方文本先抽县级单位，再在县内以 PPS 抽社区；大社区可能继续抽子社区。已核发行 PSU 文件表头有 `communityID`、省/市名称、NBS 城乡/地区类型和版本字段，但没有明确标为县级抽样单元编码或方差层编码的列。受控 PSU 键拓扑 QA 确认省/市标签不能作为官方县级样本单位的一对一 crosswalk；精确聚合数和类别仅存本机 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\qa_outputs\`，不公开。不得仅凭列名假定 county、strata 或 final PSU。
- 官方 2011 Codebook 的 PSU 节（印刷页 1340–1341）列出的变量为 `communityID`、`province`、`city`、`urban_nbs`、`areatype`，未列 county sample-unit ID 或方差 strata。该公开字段清单与实际 PSU 表头核验相符；release/version 字段是版本元数据，不构成抽样层变量。

- 用户确认 Wave 1 All Data、PSU、Weight、Blood 来自其获准 CHARLS 账号，对应官方数据项 123、117、118、201。服务器只读来源检查和准备表 provenance/hash 检查通过；该检查核对来源文件清单、Stata 表头和文件哈希，不读取受访者答案。
- 受保护发行包中15个 All Data 模块的字段名已经逐一检查。`sub_commuID` 只见于社区模块；其余14个模块均没有此字段。社区模块同时含 `communityID`。
- **键结构更正**：受保护复核发现社区模块的空白 `sub_commuID` 以空格存储。按空白规范化后，子区编号仅见于拆分父社区的多行记录；个体表只有父 `communityID`，不能据此分配这些父社区内的具体子 PSU。此前未处理空白的快速汇总会把空格误作有效值，已更正。完整候选处理矩阵见 [`wave1_variance_estimator_decision_matrix_2026-10-29.md`](wave1_variance_estimator_decision_matrix_2026-10-29.md)。
- 独立 PSU 文件的表头提供 `communityID`、省/市、NBS城乡、地区类型和版本字段；未见子 PSU 映射键、显式方差层或复制权重。社区字段存在不等于能确定个人所在子 PSU。
- Weight 文件含家庭/个人键及多类权重；Blood 文件含 `bloodweight`、空腹标记和15个常规血液分析物字段，另有 cystatin C。官方手册支持常规血液结局优先评估血检专用权重；cystatin C 因有年龄分层随机检测而暂不并入普通血检分析族。
- 受保护只读 `require_verified_wave1_frame` 检查通过；`require_wave1_analysis_readiness` 因没有绑定当前来源和方案的审阅记录而阻断模型执行。
- 两个 Wave 1 试点入口都在读取分析输入前调用上述来源与分析就绪门；当前没有审核记录时会 fail closed，不会进入拟合步骤。

## 当前准入矩阵（供独立审阅填写；不是批准）

| 审阅门 | 当前状态 | 已有证据/未决项 |
|---|---|---|
| 官方来源身份 | 已通过 | 用户确认来源于本人获准账号；服务器 source manifest 与源/准备表哈希门通过 |
| 样本框及分母 | 部分核实，需审阅 | 官方抽样框和问卷/血检目标已归纳；具体目标分母须绑定每个结局模块、访谈/血检资格与缺失处理 |
| 目标总体及年龄域 | 候选方案，未审阅批准 | 主分析候选为官方完整血检目标（主访者及配偶）；45+仅为次级 domain；仍需复核权重分母和完整案例目标 |
| 权重与非应答 | 候选方案，未审阅批准 | 常规血检候选 `bloodweight`；它不能替代 PSU/方差，也不自动修正家庭暴露模块非应答 |
| 最终 PSU 映射 | 未解决 | `communityID` 是父社区键；拆分社区内 respondent-to-final-sub-PSU 无可追溯链接。county-prefix 仅为候选，不是已确认原始抽样县 ID |
| 方差方法 | 未批准 | county-prefix 顶层 with-replacement Taylor 近似和县内社区条件敏感性仅供审阅；不复现完整 CHARLS 设计，且不保证保守 |
| 结局有效值与测量条件 | 部分阻断 | 15项常规血液分析物目录已对照；血糖/TG 的 `qc1_va003` 数值和特殊缺失码未由官方文件确认 |
| 冻结模型与完整假设族 | 未批准 | K=105 关系已列明；M1/M2、空腹处理、结局量纲/变换、诊断及不可估计项规则须签定 |
| 内部试点放行 | 未通过 | 仅在各项所需门通过且审核记录绑定来源、准备表、冻结计划后放行 |
| 公开发布 | 未批准 | 内部试点审查不授权发布；逐项统计披露审查仍另行执行 |

审阅人应逐行选择 `passed`、`blocked` 或 `not_applicable`，填写可追溯证据和限定条件；不能把“已有建议”改写为“已批准”。当前登记的模板为 [`templates/wave1_analysis_readiness.template.json`](templates/wave1_analysis_readiness.template.json)，真实审批记录只能保存在服务器受保护的 `private/analysis_review/`。

## 105项方案候选（待重新冻结；以下不是已批准规格）

15项 Wave 1 普通血液结局的字段、原始单位、官方指南测定范围及尺度建议另列在 [`wave1_outcome_scale_readiness_2026-10-29.md`](wave1_outcome_scale_readiness_2026-10-29.md)。指南测定范围只是 assay metadata，不是可直接用于过滤的分析值上下限；15项结局尚无获批有效域或变换。

- 假设家族候选为 105 个系数：住所供水 `i017`（Yes vs No）15 项，加上烹饪燃料 `i022` 六个非电力类别分别对电力的 90 项；结局为 15 项常规 Wave 1 血液分析物，不含 cystatin C。官方燃料分类保持原样，不合并为“清洁/污染”。该方案是在早期水源探索后形成，须标记为探索性。
- 当前主要目标候选为完整官方血检目标（基线主访者及配偶），使用 `bloodweight`；不按个人年龄≥45机械筛选。45+仅作为完整设计框架中的次级 domain 候选。血检目标与暴露模块非应答共同决定的配对完整案例目标尚需审查。
- M1 候选：暴露 + 官方来源年龄 + 年龄平方 + 性别；M2 候选：在 M1 上增加 NBS 城乡及分组教育作为预设敏感性模型；M0 仅描述。当前官方年龄候选是区间年龄而非精确访谈日年龄，使用区间中点并以上下界及无歧义 DOB 子集作敏感性仍待审阅；不再使用 Harmonized CHARLS D 年龄替代官方派生。协变量因果角色须与 [`core_covariate_readiness_2026-10-23.md`](core_covariate_readiness_2026-10-23.md) 的 DAG 审查共同冻结。
- 若 M1/M2 获准，分别在完整 105 项中计算 BY-FDR 与 Bonferroni，所有不可估计假设保留在固定家族内。结果不能按显著性选配对；该多重校正也不能消除早期探索造成的选择性。
- 方差没有首选方案。县级编码前缀顶层簇的 with-replacement Taylor 近似、县内社区聚类且条件于已抽中县的敏感性，都只是供独立审阅的未批准选项；两者都不等于 CHARLS 完整设计，未获独立审阅前不得进入配置。历史运行的 `communityID` 单层近似不能作为当前批准规格。
- 结局有效码、特殊码、单位/变换、LOD/顶码和 `qc1_va003` 空腹编码仍需逐项以官方材料审阅并在冻结前定版。指南测定范围不是默认清洗阈值；空腹编码未确认前，不据此筛血糖或甘油三酯样本。

## 新发现的测量条件问题：空腹状态

Wave 1 官方 Blood User Guide 说明采血前要求过夜空腹，但未空腹者仍采血并记录状态；指南指出非空腹样本约占少数，且非空腹血糖可能高于空腹测量。官方 Blood 文件含 `qc1_va003` 空腹字段。该字段在 Stata 文件中没有 value-label set；所取得的 Wave 1 Codebook 和 Blood User Guide 说明了字段用途/测量背景，但没有给出该变量的具体数值编码。官方2015 CodeBook的相近 `bl_fasting` 字段为1=Yes、2=No，但不据此推断Wave 1编码；第三方变量索引提示同一映射，也不据此解码或放行。现有105项扩展脚本没有将空腹状态放入模型或相应的结局 domain；项目变量语义记录则要求血糖、甘油三酯保留空腹信息。具体复核记录见 [`wave1_fasting_code_source_review_2026-10-29.md`](wave1_fasting_code_source_review_2026-10-29.md)。

因此，在任何真实模型运行前，先以发布文件文档核实 `qc1_va003` 数值编码，再明确并预先固定血糖及甘油三酯的处理：主估计是否对空腹状态调整、是否另做空腹样本敏感性分析，以及缺失/非空腹标记如何处理。不可查看结果后再决定筛选方式，也不得按未经核实的编码划分 fasting/not fasting。此决定也会影响结局标准化参考域和每一项的估计目标。

**实现约束已核对：**当前 scale-up runner 的结局规则只接受 `not_applicable`、`retain_all`、`restrict` 三种空腹模式；尚不支持以空腹状态作为协变量调整。未来若审阅人选择调整，须先从官方来源确认代码，再扩充模型配置/协变量构建设计与校验，并以合成数据验证软件行为；不得把软件校准当 CHARLS 结果。此改动目前未实施，也不改变当前准入状态。

## 请审阅人决定的问题

1. 官方抽样说明提及30个大型社区以子社区作为 PSU；当个人/家庭文件没有 `sub_commuID`，PSU 文件也没有该字段时，是否有可接受且可追溯的方式将最终 PSU 映射到受访者？如果没有，现有公开数据可以支持哪种推断范围？
2. 官方县级 PPS 与县内社区 PPS 应如何进入多阶段方差估计？对发布数据中的省/市名称、NBS 区域字段，可否建立抽样 county unit、实际 strata 和系统抽样排序的可靠映射？若不能，哪一级近似可接受、哪些阶段须声明未建模？
3. 若最终只能使用 `communityID` 聚类、没有正式 strata 字段，父社区聚类且无显式 strata 的 with-replacement Taylor 近似是否可用于清楚标记的内部探索估计？其标准误、自由度和代表性限制应怎样表述？审阅人可要求停止模型拟合或改为仅作描述。
4. 官方完整血检目标及 `bloodweight` 是否支持将主访者和配偶作为主估计总体、45+作为次级 survey domain？对 E/P 配对的暴露模块非应答及完整案例，`bloodweight` 应如何解释，有没有额外的配对权重/非应答调整？
5. 对血糖/甘油三酯，官方发布文档中应以何种代码解释 `qc1_va003`？在此基础上建议采用何种预先声明的空腹状态调整和敏感性方案？
6. 105项主族的具体有效值、量纲/变换、协变量、可估性标准、单 PSU/domain-singleton 处理、多重校正与结果复核是否足够完整？

## 当前决策

在上述问题获得独立方法审阅并写入受保护审核记录、冻结的105项配置绑定到当前来源与代码之前，不拟合真实关联模型。近似估计若被接受，也必须明确标成近似设计，不能表述为完整复现 CHARLS 分层多阶段设计或无条件全国代表性结果。没有任何结果可进入公开网站。

## 官方来源

- [CHARLS 官方 Wave 1 样本设计说明](https://charls.pku.edu.cn/en/About/Sample.htm)
- [CHARLS 2011 Wave 1 Codebook 下载页](https://charls.charlsdata.com/documents/120/download/en.html)，PSU节印刷页1340–1341。
- [CHARLS 2011–2012 National Baseline Users' Guide](https://charls.pku.edu.cn/wenjian/jixiandiaochashujuyonghushiyongshouce2013-04-07.pdf)
- [CHARLS Blood Sample Users' Guide](https://charls.pku.edu.cn/wenjian/xuejianshujuyonghushiyongshouce.pdf)，尤其是过夜空腹、非空腹样本仍采集以及血糖差异的说明。
- 项目内的 [试点方案与门禁](pilot_2011_water_biomarker_plan_and_gates_2026-10-26.md) 与 [生物标志物有效值/尺度门禁](wave1_biomarker_outcome_validity_and_scale_gate_2026-10-27.md)。
