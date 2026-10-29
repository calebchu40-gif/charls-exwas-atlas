# Wave 1 PSU 映射与方差估计候选决策矩阵

**日期：2026-10-29**  
**性质：内部方法审查材料，不是独立审查批准，也不放行真实模型。**

## 已核实的设计层级

CHARLS 2011 National Baseline Users' Guide 描述县级单位按地区、城乡和人均 GDP 排序/分层后系统 PPS 抽取；每个县级单位抽取 3 个村/城市社区 PSU。对超过 2,000 户的大型社区，部分社区以地理子区（例如原居委会）作为 PSU，子区按估计人口抽取，子区占父社区的份额进入后续权重构造。指南称共有 30 个社区需要拆分。

本轮再次逐段核对 CHARLS 官方 Sample 页面与 Wave 1 Users' Guide：县级单位的排序/分层变量为地区、城乡、GDP；村/社区以 PPS 抽取；大社区确有以子社区作为后续 PSU 的阶段。官方指南还说明权重由各阶段抽样概率连乘取倒数构成，并区分家庭/个人以及是否校正非应答的权重；血液样本另有校正血检非应答的个人权重。拆分子社区的份额参与点权重构造，但**权重不能替代最终分析 PSU 归属或设计方差变量**。因此，原计划中“不能从公开文件恢复全部正式设计字段”的结论仍成立，不过对官方抽样过程的描述现有更直接的官方文本依据。

受保护服务器中的发行包键结构复核进一步表明：个体记录有 `communityID`，社区模块同时包含 `communityID` 与 `sub_commuID`，但后者只有少数非空子区记录；这些记录位于重复的父社区键下。对空格形式的空值作清洗后，不能把社区模块直接当成完整 respondent-to-sub-PSU crosswalk。个体记录没有 `sub_commuID`，PSU 文件也没有该字段。受保护 QA 中保存精确键覆盖摘要；此公开方法备忘录不复制参与者行数、ID、原始值或文件哈希。

因此，当前证据支持普通村/社区层面的 `communityID` 键，但尚不能识别被拆分社区内每位受访者属于哪个最终抽样子 PSU。该发现修正了“社区表里有 `sub_commuID` 也许能直接映射”的初步猜想：空白值清洗前的快速汇总把空格误计成有效值；校正后仍是拆分父社区内的归属不明。

## 权重构造与方差字段是两类不同信息（官方手册逐段复核：2026-10-29）

重新核对 Wave 1 Users' Guide 的 “Sample weights” 章节后，补充以下来源细节：

- household base weight 的发行说明明确逐阶段相乘抽样概率的倒数，并在30个需要拆分的大社区情形下，把子社区相对于父社区的份额纳入抽样概率。个体权重再按家庭内被选为主受访者或配偶的条件概率调整。
- nonresponse-adjusted household weight 的应答模型使用 PSU 虚拟变量；个体应答调整还纳入性别、年龄信息状态、年龄、婚姻状态及 PSU 虚拟变量。若某些 village dummy 因参与状态完全相同而无法单独估计，指南称会与邻近或至少同县单位合并。
- 这说明发行权重不只是简单的“社区内样本校正”，也提示非应答调整中的部分 PSU 指示项可能经过合并；但手册没有发布哪些 PSU 被合并、合并后的变量、县级分层 ID、拆分社区内个人到最终子 PSU 的映射，也没有提供 Taylor/复制权重方差算法。因此不能从手册中的权重模型反推出方差 strata/PSU，也不能据此声称 `communityID` 聚类已复原完整设计。
- 对本项目暴露—结局配对，结局模块专用应答权重只解决其手册明确覆盖的抽样/应答步骤；若暴露来自另一独立模块或存在模块非应答，还须说明配对完整案例目标及是否需要另行处理该非应答。不能仅凭 `bloodweight` 或 `Biomarker_weight` 非缺失，把所有候选配对都当成同一分析框。

上述区分强化了后续审阅问题：审阅人须分别裁决“点估计使用的目标总体与发行权重”及“标准误使用的聚类/分层/阶段近似”，并明确响应加权覆盖范围。当前不改变任何模型准入状态。

## 额外需要审阅的多阶段层级

此前矩阵主要比较社区 PSU 的完整/近似方差处理。本轮把官方设计中的**县级抽样层**单独纳入：CHARLS 设计说明为县级单位按地区、城乡、GDP组织后抽取，再在县内抽取社区。已审 PSU 文件的表头包含 `communityID`、省/市名称、NBS 城乡/地区类型与版本，没有明显命名为 county sampling-unit ID 或 stratum ID 的变量。省/市名称字段不能未经唯一性与层级核验就当作县级抽样单元；地区/城乡等排序变量也不能直接当作实际方差层。

此前按 PSU 表字段审查时，没有发现单列 county sampling-unit ID。现已重新核对官方用户手册的 ID 编码章节：9 位 household ID 前六位编码省、市、县并区分县级单位，第七位编码县内村/社区；个人 ID 在 household ID 上增加两位。见[CHARLS 2011 National Baseline Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/CHARLS_nationalbaseline_users_guide.pdf)。

据此新增 `scripts/audit_wave1_county_prefix_design.py`，绑定已复核的 Wave 1 prepared manifest 与官方 PSU 文件哈希，只读取受保护 person ID、household ID、community ID 和 PSU community ID，核验编码前缀与 respondent-community 覆盖。受保护本机和服务器结果均通过前缀一致性核验；县级候选键及县内社区结构与官方手册描述的基线抽样结构一致。精确聚合计数只保存在 owner-only QA 中，不输出编码值或逐行记录。

这修正了此前“缺少县级候选键”的结论：官方编码规则支持一个县级抽样单位候选键，且它可从 CHARLS ID 复现；它不是行政区县名 crosswalk。当前可评价“县级候选键—communityID”嵌套结构，但仍未恢复县级系统 PPS 的抽样顺序/尺寸和隐式分层，也没有拆分社区到 respondent 的最终 sub-PSU 映射。故仍不能声称完整恢复了 CHARLS 方差设计或放行关联模型；需明确近似与推断范围。

此结论现有公开官方 codebook 交叉验证：2011 Codebook 的 PSU 节（印刷页1340–1341）仅列 `communityID`、`province`、`city`、`urban_nbs` 与 `areatype`；没有县级抽样单位 ID 或显式方差层字段。Wave 1 `PSU.dta` 实际表头另有版本元数据，但也未显示县 ID/strata。官方页面列出的 PSU 产品见[CHARLS 2011 Wave 1 数据页](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)。

## 候选处理方案

## 当前 runner 的设计表达能力（静态代码审阅，2026-10-29）

对 `scripts/run_2011_household_environment_scaleup.py`、冻结设计配置及受控本机锁定的 `svy==0.35.0` 实现做了静态检查，未运行模型。`svy.Design` 数据结构可声明多个 PSU/SSU 标识、复制权重和两阶段 `PopSize`；但本项目用于 GLM 的 runner 与该版本 GLM 执行路径有以下限制：

- 当前 runner 接受一个 `psu_field`，只组装 `__design_psu` 和 `__design_weight`，没有将社区及县级/子社区阶段字段接入设计对象。
- runner 将 GLM 调用硬编码为 Taylor，且显式拒绝 `replicate_weight_fields`；`svy==0.35.0` 的 `GLM.fit` 本身支持显式 `method="replication"`，所以这是项目配置/runner 的限制。CHARLS 已审发行包没有官方复制权重；不能用缺少真实设计信息的任意算法构造 replicate weights 来绕过该门。
- 包的 `Design` schema 声明了 `ssu` 与两阶段总体规模 `PopSize`，但已锁定版本的 GLM Rust 执行调用只接收单一 strata、PSU 与 FPC 列；该回归路径的 FPC 处理注释明确说明只使用 PSU 层修正并忽略 SSU 信息。不能把 API 上存在字段等同于本项目 GLM 已实现完整多阶段估计。
- runner 允许多个 `stratum_fields` 进入 `Design`，但本项目没有核实其组合语义，也没有实现县级 PPS、系统抽样隐式分层或 CHARLS 阶段抽样信息的映射。
- 单 PSU 与 domain singleton 要求显式指定处理策略，但指定软件选项并不能弥补缺失的官方设计变量。

包内 `GLM.fit` 源码及其[官方 GLM 文档](https://svylab.com/docs/svy/tutorials/glm.html)说明 Taylor 为默认；复制权重须显式指定 `method="replication"`，不会自动使用。该文档确认的是软件功能，不构成 CHARLS 复制权重或设计规格的来源。

另对照 `svy` 官方[多阶段抽样文档](https://svylab.com/docs/svy/tutorials/multistage.html)：包支持按三阶段抽样链生成设计/权重；其文档描述的方差使用 ultimate-cluster approach，即按首阶段 PSU totals 在 strata 内估计，较低阶段分层进入权重但不作为方差分层。**能构造三阶段抽样权重不等于能恢复 CHARLS 实际抽样框、县级 strata 或最终子社区到个人的归属。**如以社区为 ultimate cluster，须把它表述为社区层估计目标/近似，并由审阅人判断对 CHARLS 目标总体及拆分社区是否成立。

因此，方案 A（完整恢复全部官方设计阶段与方差所需信息）仍受县级隐式分层/系统 PPS 信息及最终子 PSU respondent 映射缺口阻断；但县级候选键已有官方编码规则和受保护键核验依据。是否扩展 GLM 执行器要依据审阅结论确定。方案 B 也不能仅靠把 `communityID` 填入单一 `psu_field` 自动获准；需评估 county-prefix 与 community 的嵌套表达、近似目标总体、方差自由度及拆分社区处理。不得使用普通模型标准误伪装设计方差。

这项代码缺口属于实现能力判断，不是统计方法批准。当前正式分析仍关闭。

| 方案 | 做法 | 可支持的解释 | 主要风险/限制 | 当前状态 |
|---|---|---|---|---|
| A. 官方完整设计 | 使用 CHARLS 对应 2011 受访者/家庭到最终子 PSU 的映射、正式分层及适用的抽样阶段信息；按官方建议指定方差 | 最接近目标抽样设计的设计型推断 | 当前公开发行包/已审材料未提供完整跨表映射、方差层或复制权重；不能从地理变量推造 | 首选；需可追溯官方证据 |
| A1. 县级编码键—社区嵌套候选 | 用用户手册定义的 ID 前六位作县级候选键、用 `communityID` 作县内社区键；将其作为多阶段设计候选输入 | 保留官方文件可复现的县/社区层级；是否足以做设计型推断须裁决 | 未恢复隐式分层、系统 PPS 排序/尺寸及拆分社区内 respondent-to-sub-PSU 映射 | 键核验通过；设计未批准 |
| B. 父社区聚类近似 | 对可识别的普通 PSU 使用 `communityID`；对拆分父社区不猜测子区归属，暂以父社区聚为一个 cluster；权重仍按结局/目标人群的官方定义 | 只能作为明确标记的近似加权关联；点估计和不确定性都须按该近似重新解释 | 将多个被抽子 PSU 合并会改变方差结构；缺少显式分层且隐式排序不能直接还原为正式 strata；FPC/阶段信息不足 | 仅供独立复杂抽样审阅，不自动放行 |
| C. 按子区均分/任意分配 | 将父社区内 respondent 平均分到子 PSU，或按社区表顺序/城乡/地理变量分配 | 无 | 伪造抽样单元归属，改变 cluster 数及方差；无法由已发布键证明 | 禁止 |
| D. 删除拆分父社区 | 删除无法归到子 PSU 的父社区记录后估计 | 变成被人为删减且需重新构造权重的样本 | 设计选择与应答权重不再对应；可能造成选择偏差和目标总体变化 | 不可作为默认处理 |
| E. 普通回归标准误 | 使用一般线性模型或仅个体级稳健标准误，不考虑复杂设计 | 条件样本内模型关联，且须明确非设计型 | 把相同 PSU/家庭内相关性当独立，无法支撑设计型总体不确定性 | 不能替代本项目所需设计方差 |

## 需独立审阅人回答的门槛问题

1. 已有官方编码支持的县级候选键及县/社区嵌套关系，但缺少抽样顺序/尺寸和显式 strata 时，哪种多阶段方差近似可支持预先定义的 estimand？目标总体、标准误、自由度与未建模阶段应如何表述？
2. 县内三个社区及拆分社区子区的方差贡献如何处理？拆分社区到 respondent 的映射是否为最低准入条件；若取不到，哪些推断/发布范围必须受限？
3. 县级抽样的“排序/分层”变量不等同于发布的方差层。没有确切分层标识时，无显式 strata 的 Taylor with-replacement 近似是否可接受？单 PSU/domain-empty 处理、自由度和有限总体修正如何规定？
4. 权重中对子区相对父社区份额的调整，是否足以支持点估计；它对方差估计缺失的子 PSU 归属有何影响？权重不能被视为方差结构的替代。
5. 对家庭暴露，同一家庭多名受访者以及社区暴露的 cluster-level 变异如何体现在 PSU 方差中？
6. 若只有近似方案获准，输出能否用于公开 Atlas；需要怎样标注为探索性/近似设计、限制代表性主张，并如何做足够的敏感性分析？

## 建议的决定顺序

1. 保留已验证的县级编码前缀和社区候选键，继续查找有官方来源的拆分子 PSU respondent 映射、正式方差层/复制权重或 CHARLS 方差估计建议；不将后续波次 Sample_Info 当成基线替代。
2. 将方案 B 作为需要审阅的 fallback，而不是默认批准方案；审阅记录须绑定 Wave 1 来源清单、准备表、冻结的目标/权重方案与执行器版本。
3. 独立复杂抽样审阅人明确批准的只是“方法可以进入内部试点”或“仅可作描述/探索”，不能默认批准公开发布。
4. 方差审查通过后，再解决血糖/甘油三酯 `qc1_va003` 官方代码、空腹规则、105 项假设族及结局量纲，并完成方案冻结；随后才复核/拟合真实试点。
5. 只有试点的估计可行性、设计处理、诊断和敏感性检查经复核后，才考虑 K=150/K=90 扩展；不得用 p 值显著性作为扩展门槛。

## 官方依据

- [CHARLS 官方 2011 样本设计说明](https://charls.pku.edu.cn/en/About/Sample.htm)，县级排序/分层、PPS、30个拆分社区、45岁主样本及配偶入样规则。
- [CHARLS 2011 National Baseline Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/CHARLS_nationalbaseline_users_guide.pdf)，抽样设计与权重章节。
- [CHARLS 2011 Wave 1 官方数据与文档页](https://charls.pku.edu.cn/en/Data/a2011_CHARLS_Wave1__Baseline_.htm)。
- [项目的 Wave 1 estimand/权重/PSU/方差门槛备忘录](wave1_estimand_weight_psu_variance_gate_2026-10-29.md)。



## 官方用户论坛的抽样方差答复边界（补充检索：2026-10-29）

在 [CHARLS 数据用户论坛历史问答](https://forum.charlsdata.com/viewtopic.php?t=22)中发现一则关于样本权重与 `svyset` 的讨论。提问者询问公开数据没有直接标明 PSU/strata 时该如何指定。CHARLS 论坛管理员的回复概括 CHARLS 为多阶段 PPS 聚类抽样，权重为家户/个人抽样概率倒数，并称实际处理时聚类到哪一层取决于研究需要。该回复**没有给出** Wave 1 应使用的 `strata()` 字段、`communityID` 的具体 Stata 声明、拆分社区个人映射、方差自由度或复制权重方法；提问者后续提出的 SAS 示例也没有在该帖子中获得管理员确认。

因此，该论坛答复可作为“权重不自动定义方差、研究者需明确分析聚类层级”的项目组用户支持线索，但不能当作可操作的正式方差规格，更不能据此批准社区聚类、把 `communityID` 设为 strata，或推断完整设计已被还原。现行门槛不变：优先取得可追溯的正式技术规格/键映射；否则由独立复杂抽样审阅人明确裁决一个有限目标总体的社区层近似能否支持内部模型，以及它是否足以支撑 Atlas 发布。审阅记录需说明该方案没有还原官方县级分层/PPS阶段和拆分子社区最终 PSU 归属。

该问答的网页目前可由搜索索引读取，但直接打开论坛时返回 502；因此只记录其索引可见的问答摘要，不将其作为唯一依据。核验的主要设计事实仍来自 CHARLS 官方样本设计页与 Wave 1 Users' Guide。

## 2026-10-29 official sample-frame nuance: realized county units

A fresh read of the current CHARLS official sample page adds a detail relevant to the first-stage design reconstruction: the planned sample selected 150 county-level units, but administrative boundary changes caused six communities to fall within two counties in six counties; those communities were retained, so the page reports 156 final county-level units. The page also states that six of the originally selected 450 communities were replaced for frame/eligibility reasons, following the stated selection procedure.

This means a released `province`/`city` label cannot be presumed to identify the realized first-stage sampling unit, reproduce the original 150-unit PPS draw, or define the implicit sorting strata. Even a future geography-based county crosswalk would need to reconcile the 150 planned selection units, the 156 realized administrative units, six replacements, and boundary changes; administrative labels alone do not supply the sample-design history. The already observed absence of a county-unit key in the Wave 1 PSU release therefore remains a substantive design limitation, not merely a variable-name search issue.

The same official page distinguishes the age screening path: households with members older than 40 could enter screening; a selected person aged 45+ became a main respondent and their spouse was interviewed, while a selected 40–44-year-old was reserved for a future refresher round. Blood User Guide defines the blood target as the full main-respondent-plus-spouse baseline group, so eligibility must follow the released respondent/blood target and not a mechanical `age >= 45` filter.

**Design consequence:** retain the first-stage county design gate as unresolved unless an official crosswalk/design file or written variance specification explains the realized unit mapping. Do not infer county strata from province, city, NBS region, urban/rural, or GDP ordering variables. A parent-community approximation remains a review candidate only, with its target and omitted first-stage variance stated explicitly.

Sources: [CHARLS official Sample page](https://charls.pku.edu.cn/en/About/Sample.htm), [2011 Wave 1 User's Guide](https://charls.pku.edu.cn/en/data/User2011.pdf), [Blood Data User's Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf).

## 2026-10-29 补充：县前缀与最终地理县级数的差别

官方 Sample 页面说明，Wave 1 原计划抽取150个县级单位；6个被抽社区因边界变化落入额外县且未替换，最终实际县级地理单元为156。受保护 ID 前缀审计得到150个前缀组、每组关联3个样本社区，这与“原始抽样框中的150个第一阶段单位”一致，但不能单凭结构匹配证明前缀就是原始第一阶段抽样单位。官方 ID 章节只说明其省/市/县编码可区分县，并没有说明遇到边界变化时前缀如何归属。故将“county-unit key recovered”收窄为“county-code grouping candidate identified; first-stage PSU identity unresolved”。在得到可追溯说明/独立裁决前，不把前缀直接用于正式方差模型。
