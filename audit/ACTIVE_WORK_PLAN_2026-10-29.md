# CHARLS ExWAS Atlas：执行计划与当前进度

**更新时间：2026-10-30（Asia/Shanghai；Wave 3农历生日不确定性方法审阅）**
**2026-10-30 通用设计模板校正：**发现通用 `exwas_design.template.json` 仍预填 `communityID`、`bloodweight`、未分层近似和 45+ 域，与当前官方抽样设计审阅及“45+仅作次级域”候选不一致。现已将权重/PSU/波次/年龄/协变量字段改为空的待审值，并标记不可直接运行；当前没有获批的单层方差方案。详见[`multwave_runner_configuration_compatibility_review_2026-10-29.md`](multwave_runner_configuration_compatibility_review_2026-10-29.md)。
**2026-10-30 通用扫描引擎审阅：**修正通用引擎的二项模型 OR 标准误尺度、正权重缺失 PSU/分层键处理、低于两个 PSU 的配对域阻断和模型 ID 显式配置要求。已确认仓库受控 Wave 1 runner 原本包含来源身份、准备表 hash、冻结计划 hash、逐门审阅记录及私有扫描授权；服务器未提交草稿漏掉了该门禁，不能覆盖受控版本。服务器草稿将先私有备份，再同步带准入门的 runner。当前正式模型 0，未运行测试或真实拟合。详见[`generic_exwas_runner_safety_review_2026-10-30.md`](generic_exwas_runner_safety_review_2026-10-30.md)。
**2026-10-30 Wave 3 农历生日方法更新：**CHARLS维护的 `lunar2solar` 使用全变量级 `leap` 选项与分开的普通/闰月表；已审Wave 3生日路由记录农历/公历类型，但没有发现逐人闰月标记。不得对全部农历日期默认调用普通月表，也不得推断闰月。拟审候选方法是对同一有效农历日期保留普通表映射，并仅在官方闰月表存在同键时保留闰月映射，随后结合访谈年月缺少日的信息计算年龄区间；45岁domain只在区间稳定跨过阈值时分类。该法尚未做官方表格解析/运行时验证或独立年龄审查，当前年龄与真实模型门仍关闭。详见[`wave3_lunar_date_uncertainty_method_review_2026-10-30.md`](wave3_lunar_date_uncertainty_method_review_2026-10-30.md)。
**项目目标状态：进行中**  
**当前阶段：Wave 1 调查设计准入复核；通过现行准入的正式模型仍为 0**
**2026-10-30 方差审阅更新：**重新核对 CHARLS 官方抽样页后，撤下县级 ID 前缀作为“优先单层簇”的定位。官方将村/社区称为 PSU，同时另有县级系统 PPS 与分层，以及 30 个大社区的子社区抽样；2015公开发行文件未见可重建原始分层及所有拆分子 PSU 的受访者映射。县级前缀和 parent `communityID` 均不作为已验证设计变量。当前无获批的单层近似；Wave 3正式模型仍为0。详见[`charls_wave3_psu_variance_release_review_2026-10-30.md`](charls_wave3_psu_variance_release_review_2026-10-30.md)。
**2026-10-30 Harmonized CHARLS 设计信息排查：**Gateway 当前列表为 Harmonized CHARLS D.2（Wave 1–4及2014 Life History，所述数据截至2021），CHARLS 下载页仍列公开 D 版；Gateway D.2 行没有 Codebook 下载链接，旧 codebook 路径当前返回 soft 404。故 D.2 是否增加 Wave 3 PSU/分层字段仍未知，不能据旧 D 版、Harmonized 权重、年龄或地理字段推断。SAGE+ 文献只作为历史旁证。后续只有取得 D.2 实际版本化 Codebook/创建说明后才能重开这一设计来源审查；当前方差门及零模型状态不变。详见方差审阅 memo。

**2026-10-30 Wave 3 官方血检准备：**复核官方 2015 Codebook 后，将 Wave 3 主表框架改为官方 `Sample_Infor`（保留 `crosssection`）；人口学模块缺失仍留空。受保护 ID-only 核验确认 Blood 文件 ID 均属于 Sample_Infor，正向 `Blood_weight` 均属于横断面域；随后基于该框架重建个人准备表并完成官方 Blood 一对一合并，未发生行扩张。源与输出指纹、精细 QA 仅保存在服务器私有目录，不进入 GitHub、OneDrive 或 Pages。Wave 3年龄来源字段及BA002/BA003问卷路由已对照官方文档列明；Sample_Infor仅含访谈年月、出生日期候选字段在Demographic_Background。受保护的hash绑定年龄路由QA已发现部分BA002路由未决、已知路由缺失/无效BA003日历值及月/日为0的未知日期；存在出生年份及月/日信息缺失；非缺失日期字段未超出问卷基本范围，访谈年月字段完整。精确计数只留在服务器owner-only QA。年龄区间验证、协变量完整性、分析 estimand 冻结、PSU/方差、冻结方案及独立方法审查仍未通过；官方 Blood_weight 的横断面血检目标及构造已据发布说明确认，详见[`wave3_blood_weight_estimand_review_2026-10-30.md`](wave3_blood_weight_estimand_review_2026-10-30.md)，正式关联模型仍为 0。具体字段/路由及安全处理见[`wave3_age_covariate_route_review_2026-10-30.md`](wave3_age_covariate_route_review_2026-10-30.md)。流程与当前状态见 [`wave3_official_blood_merge_pipeline_2026-10-27.md`](wave3_official_blood_merge_pipeline_2026-10-27.md)。**

**2026-10-30 Wave 1 受保护重建及键/分母复核：**按已核验的官方来源清单和本人授权账号来源记录，在本机受控 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas` 中重新重建 Wave 1 个人主表，并运行仅读取 ID、PSU 键及官方权重字段的聚合核对。按 CHARLS Blood Guide，主分析应使用 `bloodweight`；Blood 的全部已发布记录均链接到个人主表，正权重覆盖 Blood 记录，发布记录数与指南的完整血样人数一致，因此血检文件—权重—个人主表连接门通过。All Data 人口学个人主表仍较官方主样本口径少量记录；主问卷个人权重文件有相应未匹配项，ID-only模块审计发现部分标识也出现在其他个人模块，但不能由模块出现推断资格。该 `ind_weight_ad2` 差异是待澄清的附属问题，不应误当成血检模型使用的权重或用来否定已匹配的 `bloodweight`；主样本完整分母仍部分待核。PSU 社区键覆盖受访者社区键，但最终拆分 PSU/设计层仍未解析。没有读取暴露或结局值、没有估计关联模型、没有把逐人标识或模块小单元计数写入公开仓库。未发送的官方咨询稿已区分血检权重与个人主问卷权重。正式模型仍为 0，当前主要阻断是方差设计、年龄/结局规则及独立方法审查。**

**2026-10-30 权重门拆分纠正：**更新后的 ID/权重聚合审计按实际拟使用的血检权重分别检查，确认 Blood 文件的 `bloodweight` 非缺失且正值记录均与 Blood ID 和 Wave 1 个人主表匹配，Blood 完整样本记录数与官方 Blood Guide 相符。故“血检文件—`bloodweight`—个人主表链接”通过；不能继续把 `ind_weight_ad2` 的附属未匹配问题当成血检模型的权重链接失败。官方完整目标分母仍因人口学主表与指南总体人数有小幅未核差异而标为部分核对；方差设计、分析年龄与结局规则、独立方法审查继续阻断正式模型。重跑后的受保护报告为 `qa_outputs/wave1_official_frame_reconciliation.json`；该文件不进 Git/OneDrive/站点。**

**2026-10-30 官方方法问题草稿更新：**复核发现旧版 CHARLS 咨询稿仍询问现已取得的 Wave 2 Weights 文件，可能误导后续核实。已标记其为历史版本，并新增未发送的当前稿，聚焦 Wave 1 县级系统 PPS/隐式分层、30 个拆分社区 PSU 映射、县级 ID 前缀定义、`bloodweight` 目标、`qc1_va003` 编码与官方农历年龄算法，同时询问 Wave 3–5 的公开方差设计字段。草稿不含数据或账号信息；没有代发邮件/论坛帖。发件人需在发送当天自行核对官方联系页（现页标注2019年），收到回复也须独立审阅，不自动放行模型。详见 [`current_charls_official_inquiry_draft_2026-10-30.md`](current_charls_official_inquiry_draft_2026-10-30.md)。

**2026-10-30 CHARLS公开发布条款核对：**重查北京大学开放数据平台列出的 CHARLS Terms of Access、官方用户条款入口与 FAQ。要求学术非商业用途、不得发布原始微观数据或转交数据，公开统计/分析结果不得泄露个人信息；2011/2013发表需用指定致谢和基线 Users' Guide 引用。跟踪文件清单未发现 Stata/归档微观数据文件，线上结果 JSON 仍为404。网站已有数据限制说明；现将页脚致谢改为官方要求的原文，并更新 Wave 1 官方数据目录链接。条款、证据及边界核查记录见 [`charls_data_use_and_public_release_requirements_2026-10-30.md`](charls_data_use_and_public_release_requirements_2026-10-30.md)。

**2026-10-30 方差候选与执行器接口核对：**静态检查 `exwas_engine.DesignSpec` 和Wave 1 scale-up冻结配置后确认：现有代码能表达“单一县级候选簇 + `bloodweight` + 不虚构分层 + WR Taylor近似”，并会标注其不是完整设计方差；若方差候选获独立方法审查认可，无需先重写估计核心。此发现只解决执行器兼容性疑问，不验证县级前缀就是原始一级抽样单位，也不解决系统PPS隐式分层、配对权重/目标及自由度。所有准入仍待裁决，正式模型仍为0；本轮仅静态读代码，没有运行真实数据或测试。详见 [`wave1_variance_review_recommendation_2026-10-30.md`](wave1_variance_review_recommendation_2026-10-30.md)。

**2026-10-30 空腹代码官方来源复核：**重新打开 CHARLS 官方 Wave 1 文档目录与 Blood Users' Guide。目录仍只列通用 Codebook 和 Blood Guide；Guide说明状态会被记录并指出非空腹血样的风险，但未提供 `qc1_va003` 数值映射。网上 `1=Yes, 2=No` 目前仅见于第三方变量索引，未作为本项目准入证据。故血糖、甘油三酯的空腹代码/域仍未闭环；其他结局也仍受共同的方差及独立方法审查阻断。本轮没有读取个体结局值或运行关联模型。详见 [`wave1_fasting_code_source_review_2026-10-29.md`](wave1_fasting_code_source_review_2026-10-29.md)。

**2026-10-30 年龄区间保守性复核：**静态审阅发现，旧的农历/日历未决出生年份下界可能偏高：农历年份对应的公历出生日期可落在该年或下一公历年，而访谈只有年月、没有日，因此候选实足年龄可能比“访谈年−记录出生年”低两岁。已将闰月歧义、部分农历日期及日历未决的仅年份路线改为 `[max(0, 访谈年−出生年−2), 访谈年−出生年]`，并在受保护目录按同一已审来源指纹重新生成临时年龄区间表。公历出生月份明确时保留更窄的月份界限。此修正只使候选区间更保守；官方 Mata 逐格一致性、独立年龄方法审查与复杂抽样方差仍未通过，年龄仍不用于筛人，正式关联模型仍为0。本轮未读取血检结局值、未拟合模型、未跑测试。

**2026-10-30 计划与审阅包一致性修订：**纠正独立方法审阅包中仍被写成“当前定义”的旧方案：age≥45 主目标、Harmonized CHARLS D 年龄和 `communityID` 单层方差运行均为历史探索/旧候选，不得用于现行 readiness。当时记下的 county-prefix 方差候选已由2026-10-30官方样本设计复核撤下优先定位；当前不选择单层簇。完整官方血检目标、`bloodweight`、45+次级domain及年龄区间仍是待审估计量/年龄候选，均未冻结或批准。将 2026-10-26 的试点后续路线标为历史快照，并指向本活动计划，避免其“原始包尚缺失”等过期状态被误用。没有读取个体记录或运行关联模型。

**2026-10-30 多波次来源状态对齐：**逐波 readiness 矩阵及数据准备说明现已更新为当前受控入库状态：Wave 2官方 All Data/PSU/Weights 和样本标记已核验并进入独立准备表；Wave 3 2015 Blood、Weights、Sample_Infor及Wave 4/5的Weights、Sample_Infor已完成来源/表头预检。Wave 2 `Biomarker_weight`仅是横断面现场测量的候选权重；2015 `Blood_weight`仅是横断面血检候选；2018/2020的一般横断面权重需依`crosssection`与目标样本使用。以上不关闭波次各自的年龄、模块完整案例、最终PSU/方差及独立审查门，也不授权拟合。此前文档中“Wave 2样本标记未取得”及“2015血检未入库”为历史状态。

**2026-10-30 血检结局准入补充：**官方 2011 Blood Guide 说明非空腹血样也被采集，空腹状态记录在数据中，并报告血样参与者超过92%为空腹；但 `qc1_va003` 的数值编码仍无经审阅的官方映射。故不把非空腹自动定为无效，不猜编码、不据此筛样。指南对偏态、极端值及测量/运输的描述作为解释和预先设定敏感性方案的依据，不作为本项目的数值过滤/转换规则。主图谱仍以连续化验值为候选；指南的临床高风险切点不直接作为二分 ExWAS 结局。胱抑素C的年龄分层抽测资格及权重仍须单独闭环。详见 [`wave1_outcome_scale_readiness_2026-10-29.md`](wave1_outcome_scale_readiness_2026-10-29.md)。本轮仅补方法文档，未读个体化验值，未拟合模型。

**2026-10-30 方差方案历史候选（已撤下优先定位）：**此前将县级ID前缀列作单层簇候选。重新阅读官方抽样页后，当前判断改为无优先方差候选：县级系统PPS与分层、社区PSU、拆分子社区及缺少最终 respondent-to-PSU 映射共同构成未决设计门。县级前缀近似和 parent `communityID` 近似均未通过独立审查，不能用于放行模型。更新依据见[`charls_wave3_psu_variance_release_review_2026-10-30.md`](charls_wave3_psu_variance_release_review_2026-10-30.md)；历史技术审阅见[`wave1_variance_review_recommendation_2026-10-30.md`](wave1_variance_review_recommendation_2026-10-30.md)。

**2026-10-30 农历转换直接对照工作流已备妥：**为补足 Python 发行版之间一致、但尚未与 CHARLS 官方 Mata 表逐值比较的证据，新增 Stata 合成网格导出器和 Python 逐格对照审计器。导出器只生成合成 YYYYMMDD 输入，使用项目固定版本的官方 `lunar2solar.ado/.mmat`，输出应留在受保护临时目录；审计器校验官方源文件哈希、完整合成键集、官方矩阵维度并只报告聚合差异，不输出映射表。当前工作站和个人服务器没有可用 Stata runtime，因此仅完成工作流准备，尚未执行，也未关闭年龄算法门。执行说明见 [`lunar_official_stata_parity_workflow_2026-10-30.md`](lunar_official_stata_parity_workflow_2026-10-30.md)。本轮未读取出生日期、未运行年龄派生/关联模型，正式模型仍为0。

**2026-10-30 年龄路由修正：**静态复核发现旧候选派生器在出生年份无效时可能直接使用条件题 `ba004`，而官方 Wave 1 问卷只在整道 `ba002` 出生日期题为 DK/RF 时询问 `ba004`。现已将回退收紧为出生年、月、日及 `ba003` 日历类型均缺失；部分或无效出生日期不再借用 `ba004`。候选年龄区间和依赖年龄候选的覆盖 QA 已在受保护本机重建。官方问卷支持 `ba003=1` 公历、`2` 农历及 BA004 路由；农历候选仍未与 CHARLS Mata 查找表逐值验证，不能视为年龄算法通过；正式模型仍为0。

**2026-10-30 受控覆盖审计补充：**已在本机受保护目录完成首轮血检目标配对资格诊断：只读取 Blood 文件 ID/`bloodweight`、准备表中的六个登记家庭环境字段与家庭键，以及尚未审阅的年龄区间候选；没有读取任何血液结局值、没有按年龄候选筛人、没有拟合关联模型。六个字段登记的全部预设对比两侧均有正权重目标记录支持；可观测家庭键上的同户非缺失字段值一致。`i021` 只在 `i020=2` 路由子域检查。该结果证明目前没有明显的候选类别/家庭字段拼接空缺，但不是最终分析 N、权重适用性结论或科学试点有效性证据。年龄覆盖仅作未审阅候选诊断。受保护详细汇总保存在 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\qa_outputs\`，未进入仓库、OneDrive、服务器或网站；可公开的方法说明见 [`wave1_exposure_blood_target_completeness_2026-10-30.md`](wave1_exposure_blood_target_completeness_2026-10-30.md)。下一步应优先解决年龄算法/目标域审阅与 PSU/方差裁决，再冻结模型规格；模型门仍关闭。

**2026-10-30 最新状态：**Wave 1官方来源身份已由用户确认；修正了入库清单中一条过期的“等待人工确认”备注。受保护的 `Community.sub_commuID` 汇总核对显示它不能充当 respondent-to-final-sub-PSU 跨表键。上轮对历史试点的“范围不匹配”结论也已更正：按暴露字段、表型字段及具体对比项核对后，登记与历史输出的键范围吻合，但仍不验证模型、权重、年龄域或方差有效性。正式模型数仍为 0。线上首页 HTTP 200，关联结果 JSON HTTP 404。新增县级前缀 ultimate-cluster 有放回方差候选，明确其忽略县级系统 PPS 隐式分层且不保证保守；另列县内社区条件方差选项。两者均待独立统计审查，不能据此放行模型。2011血检主 estimand 的当前待审建议为完整官方血检目标（主访者+配偶）与 `bloodweight`，45+作为次级domain；已将10月29日的旧45+主目标候选标注为历史候选，并同步更新站点。分母、暴露完整案例与年龄算法仍需核验/审查。下一阶段依次是冻结 Wave 1 年龄/目标域与方差方案、完成独立方法审查、再复核105项试点；随后才扩展 K=150/K=90 和其他波次。

**2026-10-30 执行复核：**重新运行 Wave 1 官方文件 metadata-only 预检，四个角色均仍匹配当前入库清单，状态为 `input_set_complete_source_and_design_review_pending`；Wave 2 Weight 与 Wave 3 Blood 独立来源/表头预检也通过。没有解压 Wave 1 All Data 或读取参与者值。另复核 CHARLS Harmonized CHARLS Codebook Version D：其“CHARLS提供了设计信息时可计算设计校正标准误”的概括，没有给出 Wave 1 可直接执行的设计层/最终子 PSU 映射或 `svyset`，故不改变当前方差准入判断。此说明已补入 [`wave1_variance_review_recommendation_2026-10-30.md`](wave1_variance_review_recommendation_2026-10-30.md)。公开站点首页仍 HTTP 200，正式结果 JSON HTTP 404；真实关联模型仍为 0。

**2026-10-29 年龄转换进展：**CHARLS 官方 `lunar2solar` 帮助明确说明转换基于 `python-lunardate`。新增可复用的纯合成域审计，穷举其文档范围并比较本机固定的 0.1.4/0.1.5 源码：普通历49,949项、闰月1,521项，合计51,470项；两版映射键完全一致、共享键输出差异0项，计数恰与官方 `.mmat` 两矩阵的行数相同。这是来源/范围一致性证据，不是对 `.mmat` 的逐值比较。Wave 1 问卷没有记录闰月的独立字段；参与者年龄尚未派生，年龄算法仍需冻结闰月/不完整日期路由并作方法审查。审计脚本 [`scripts/audit_lunardate_release_domain.py`](../scripts/audit_lunardate_release_domain.py)，汇总证据见 [`lunar_conversion_candidate_synthetic_crosscheck_2026-10-29.md`](lunar_conversion_candidate_synthetic_crosscheck_2026-10-29.md)。

**Wave 1 年龄候选派生（2026-10-29；2026-10-30 路由修正）：**在复核官方来源 manifest、原始文件哈希、准备表哈希和年龄输入哈希后，受保护本机生成了临时年龄区间表。仅使用官方出生年/月/日、日历类型、条件自报年龄及官方访谈年/月；不读取暴露/结局。因没有访谈日或独立闰月标志，输出上下界而非假装精确的年龄：可按官方转换器默认路线处理的完整日期保留访谈日不确定区间；可能属于闰月及不完整日期使用更宽的出生年区间；仅当出生年、月、日和日历类型均缺失、与官方 BA002 DK/RF 后才询问 BA004 的路由一致时，才把条件年龄作为候选。部分/无效日期不再回退 BA004。对无法转换的日期保留缺失并标记原因。未因45岁候选状态筛除任何记录。该表仅供方法审查，不能进入冻结模型；农历转换仍未与 CHARLS Mata 查找表逐值验证，年龄测量/误差敏感性和抽样设计仍待审阅，正式模型数保持0。私有输出位于本机 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\\age_inputs_2011\\` 和 `qa_outputs\\`，不在 GitHub/OneDrive/网站。

**状态复核（2026-10-29 21:38，Asia/Shanghai）：**重新检查本机受保护入库、服务器项目目录/计划、GitHub主分支与线上 Pages。Wave 1四件套仍在本机受保护入库及服务器 `private/incoming_2011_official/`；服务器另有 Wave 2 All Data/权重和 Wave 3 样本信息/权重/血检官方文件。仅确认入库/目录状态，未重新读取参与者值或重跑分析。服务器 SSH 可用；服务器计划仍记载 Wave 1 设计准入未通过、正式模型为0。公开首页显示 `app.js?v=194`，首页与候选配对索引 HTTP 200，`association_results_v1.json` HTTP 404。年龄派生仍缺 Stata/官方转换对照，县级抽样层及拆分社区 respondent-to-sub-PSU 映射/方差方案仍未闭环；本次不改变模型准入状态。为避免早期“数据尚未入库”快照造成误读，仓库 README 顶部现明确当前输入与线上状态，并声明下文旧日期段落为历史记录。

**2026-10-29 农历年龄实现复核补充：**已逐行审阅 CHARLS 官方 `lunar2solar` 的 `.ado/.sthlp` 及 `.mmat` 文件头。该 Stata 程序用官方二进制 Mata 查找表分别处理普通农历日和闰月；当前本机与服务器 PATH 均未发现 Stata 可执行程序。实现细节、不可直接用 Python ad hoc 解析 `.mmat` 的原因及受保护年龄派生的下一步见 [`charls_official_lunar_conversion_implementation_review_2026-10-29.md`](charls_official_lunar_conversion_implementation_review_2026-10-29.md)。年龄构造仍未获准/冻结，未读取受访者生日、未运行转换或关联模型。

**2026-10-29 官方样本设计页补核：**基线筛查随机选取年龄>40的成员，≥45岁者成为主访者并纳入其配偶，40–44岁者进入 refresher 预留路径；故需将抽样资格路由与血检分析权重分母分别对账。官方页明确记录县级单位按地区、城乡类别、人均GDP排序后 PPS 抽样，但不提供公开 PSU 字段可直接使用的逐县方差 strata ID。细节及来源已补入 Wave 1 estimand/方差审查备忘录。

**2026-10-29 权重构造与方差分离补核：**逐段重读2011 Users' Guide的抽样权重章节，确认点权重按县、村/社区、必要时子社区份额、家庭及家庭内个人抽选概率构造；非应答调整模型使用 PSU 虚拟变量，个别完全参与/不参与的村级虚拟变量会与邻近或同县单位合并。该信息解释了权重所覆盖的选择/应答步骤，但没有给出合并映射、公开分层ID、拆分社区 respondent-to-final-PSU crosswalk 或方差计算方案，故不能由权重构造推导完整方差设计。对跨模块 E/P 配对还要审查暴露模块非应答是否由结局专用权重覆盖。细节补入 [`wave1_variance_estimator_decision_matrix_2026-10-29.md`](wave1_variance_estimator_decision_matrix_2026-10-29.md)；正式模型门不变。

**2026-10-29 Wave 1 年龄来源闸门加固：**发现旧 readiness 模板只要求“年龄域”审阅，没有独立要求证明年龄字段来自官方 CHARLS 来源及经验证的派生算法，而历史试点代码使用 Harmonized CHARLS D 临时年龄候选作调整项。已将 `official_age_source_and_derivation` 加入所有 Wave 1 readiness 的必过机检，要求记录官方字段、派生方法、来源锚点与验证证据；将模板纳入对应计划指纹，因此旧审阅不能自动沿用。该项目前未通过，年龄尚未正式派生，模型门仍关闭。审计见 [`wave1_family_runner_scope_review_2026-10-29.md`](wave1_family_runner_scope_review_2026-10-29.md)。

本文件是本项目当前执行计划的单一状态页。每次完成阶段或遇到新阻塞时更新。GitHub 只存代码与本计划，不存 CHARLS 个体数据或受限分析输出。

## 现在正在执行什么（2026-10-29）

**本次更新：Wave 2 官方包已核验、重建 Wave 2 受访者表并完成受保护的框架 QA。** All Data 整包与官方发布校验值匹配；表头确认 Biomarker 字段与 `crosssection`/`longitudinal`/`Biomarker_weight` 已纳入。重建表、模块合并 QA、权重/标记与人体测量字段覆盖汇总均留在服务器私有目录，文件/目录均限制为所有者访问；没有读取后对外发布记录或统计数。新增年龄来源审查见 [`wave2_age_preload_calendar_review_2026-10-29.md`](wave2_age_preload_calendar_review_2026-10-29.md)：Wave 2 `zba002_*` 是预载出生日期，`ba001_w2_1`确认该日期；回答“是”时跳过 Wave 2 `ba002/ba003`，因此 Wave 2 `ba003` 仅标记新回答的 `ba002` 日期，不能泛化到预载日期。Wave 1 `ba003` 只能在精准跨波链接、出生日期一致性和来源优先级审核后作为候选历法来源。`ba004`仍是出生日期未知/拒答时的条件年龄，不能作为普遍年龄字段。CHARLS目标样本包含45岁以上受访者及其配偶，不能机械按当前年龄≥45筛除所有配偶。官方人体测量问卷还确认993/999是非测量状态，体重有单独的<150 kg资格路由，且QI001题干有“breathing test”文字错误；路由/上下文必须与测量值分开，最终数值有效规则仍待审查。配对资格、模块响应、有效值、年龄、方差和独立审查仍未通过。

**最近完成：Wave 2 官方 All Data 来源/表头核验、Wave 2受保护表重建及框架 QA；Wave 1 家庭环境/血液来源及问卷路由核对；补正公开血液目录中滞后的2015入库状态。**

**Wave 1本轮推进：** 重新运行官方入库的 metadata-only 检查，四件套仍与人工确认的官方来源清单及本地 SHA-256 一致；随后在受保护本机目录新建独立版本目录，从四件套重建 Wave 1 受访者表，旧准备表未覆盖。新表已通过 source-bound provenance gate。受保护的 ID/社区键与官方权重字段聚合核对表明：官方访谈/血检目标总数与 `ind_weight_ad2` 非缺失总数一致；Blood 文件中的全部受检者 ID 能连到新 respondent spine，`bloodweight` 样本数与官方 Blood Guide 一致。Weight 文件仍有少量带正权重的 ID 无法连入 Demographic_Background spine，精确键/数量仅在本机受保护 QA 中；故官方目标分母只算聚合层面部分对账，不能宣称逐人框架完全统一。`bloodweight` 是血检结局的首选权重来源，但不解决PSU/分层方差，也不自动适用于非血液表型或暴露模块非应答。新增 [`scripts/audit_2011_official_frame_reconciliation.py`](../scripts/audit_2011_official_frame_reconciliation.py) 与方法记录 [`wave1_official_design_file_inventory_review_2026-10-29.md`](wave1_official_design_file_inventory_review_2026-10-29.md)。Wave 1 runner 现在支持通过 `CHARLS_EXWAS_DATA_DIR` 指向受保护版本目录；只应按单次 Wave 1 命令设置，不要全局覆盖多波次数据目录。真实关联模型依然为 0，正式执行闸门仍关闭。

**Wave 1框架追查补充：** 对当前官方 All Data 15个模块进行受保护 ID-only扫描后，Weight 中无法连接到 `Demographic_Background` spine 的正权重 ID 均可在其他模块找到，但不在 Blood 文件中；官方 `mainr` 标签将这些记录识别为主访者/配偶，角色均可判定。年龄/性别仍因 Demographic 缺行而无法核对；精确数量/模块小单元留在本机私有 QA。官方指南报告访谈人数17,708，而2011 Codebook报告 `Demographic_Background.ID` 17,705条；公开材料未解释这三条记录的差异。故这两个分母必须分开标注。血液结局观测框从 Blood ID 与有效 `bloodweight` 开始，再按暴露完整性和冻结年龄域确定配对样本；这不代表更广的权重构造/总体分母已解释。新增 [`scripts/audit_2011_weight_ids_across_modules.py`](../scripts/audit_2011_weight_ids_across_modules.py)。

**并行多波次推进：Wave 2（2013）源包和受保护 Wave 2 个人表重建已完成。** 官方 Release Note 将 `Biomarker.dta` 定义为人体测量，并将 `Biomarker_weight` 定义为横断面且经生物标志物模块应答调整；它可作为该模块横断面配对的来源支持候选，但不是实验室血检权重，也没有纵向 biomarker 权重。Wave2表以官方 Demographic respondent spine 构建，模块键/行扩张审计和源哈希manifest存放在服务器私有区。年龄域审查确认 `ba004` 仅在不知/拒答出生日期时路由提问；Wave 2抽样目标还包含受访者配偶，不能统一强制年龄≥45。年龄协变量必须按官方出生日期/访谈时间、Wave1链接规则和农历转换审查；具体人体测量字段、权重及剩余门槛见 [`wave2_anthropometry_release_weight_gate_2026-10-29.md`](wave2_anthropometry_release_weight_gate_2026-10-29.md)。配对资格、字段有效值、年龄构造和方差仍需审查。
- 随后将网站五波概览中两处过期/错误说明改正：Wave 2 确有 anthropometric `Biomarker.dta`（但无静脉血实验室检测），Wave 3/2015 官方血检档案已进入受控入库并完成元数据预检。没有对外暴露本地路径、个体数据或哈希。

- 新补查 CHARLS 官方数据用户论坛对“缺少明确 PSU/strata 时如何用权重”的历史答复：论坛管理员只说明多阶段 PPS、权重是抽样概率倒数、聚类层级需结合研究问题；未给出 Wave 1 可直接执行的 strata/PSU 声明，也未确认提问者后续建议的代码。该线索不能放行模型；已补进方差决策矩阵，继续等正式规格或独立审阅的明确裁决。

- [`wave1_hypothesis_registry_source_reconciliation_2026-10-29.md`](wave1_hypothesis_registry_source_reconciliation_2026-10-29.md) 记录元数据审查依据：All Data 与 Blood 来源身份已通过用户授权来源清单核对；六个候选环境字段键出现在受保护准备表表头，15个候选血液结局键出现在受保护 Blood 表头。仅查表头，没有读回答值。
- 已更正 Wave 1 假设登记表的240行来源状态；所有行仍为 `planned_not_approved`。同时将 K90 明确标成 `i020=2 (No)` 后路由至 `i021` 的受限子域；2011问卷中 `i020=1 (Yes)` 跳过 `i021`，烹饪燃料 `i022` 没有显式“无烹饪”响应。来源键确认不等于样本资格、权重或设计准入。
- 进一步将公开血液 crosswalk 中17个 Wave 1 字段的来源状态与受保护 Blood 文件表头对齐；其中15项预设结局的有效值/特殊码/变换、cystatin C年龄抽样权重和 `qc1_va003` 空腹码仍待独立来源/方法审查。
- 前序波次 × 模块交叉表见 [`wave_module_source_estimand_weight_gate_crosswalk_v1.md`](wave_module_source_estimand_weight_gate_crosswalk_v1.md) 和 CSV；该目录汇总仍然是候选字段元数据，不是可分析配对或样本量。
- 交叉表见 [`wave_module_source_estimand_weight_gate_crosswalk_v1.md`](wave_module_source_estimand_weight_gate_crosswalk_v1.md) 和 [`wave_module_source_estimand_weight_gate_crosswalk_v1.csv`](wave_module_source_estimand_weight_gate_crosswalk_v1.csv)，由 [`build_wave_module_gate_crosswalk.py`](../scripts/build_wave_module_gate_crosswalk.py) 从仓库候选字段元数据生成。60行覆盖五波目录中的来源模块；E/P/C数是唯一候选字段名数量，不是样本量、完整配对数或可估模型数。逐波权重重复列为模块审核起点，不表示适用性已经确认。
- 兼容性审计见 [`multwave_runner_configuration_compatibility_review_2026-10-29.md`](multwave_runner_configuration_compatibility_review_2026-10-29.md)：当前只有 Wave 1 探索性水源—血检 runner 和 K150/K90 受门禁保护的扩展 runner；Wave 2–5 尚无关联 runner/冻结配置。通用 design 样例也不是扩展 runner 的获批配置。
- Wave 1 历史 runner 硬编码 `bloodweight`、`communityID` 与协变量，并使用未分层方差近似；扩展 runner 则 fail-closed 要求冻结的完整样本框、目标、设计、结局有效值规则与审查记录。逐波矩阵不授权直接运行。
- 交叉核对发现血液指标目录仍把 Wave 3/2015 独立血检包标为“本地缺失”；现已根据受保护入库中的官方归档及既有 metadata-only 预检记录更正18条目录状态。该修正只更新来源/目录元数据，没有读取或公开参与者记录。
- **当前阶段：Wave 1 调查设计准入复核；通过现行准入的正式模型仍为 0。**本机 Wave 1–5 官方输入仍在受保护入库；服务器项目文档/日志已核对。真实数据关联分析仍被样本目标、设计方差、Wave 1 空腹来源和独立审查门禁阻断。

- 已完成 [`wave1_variance_estimator_decision_matrix_2026-10-29.md`](wave1_variance_estimator_decision_matrix_2026-10-29.md)：比较完整设计、父社区聚类近似、任意分配、删除拆分社区及普通回归标准误的适用边界；父社区聚类仅是待独立审阅的 fallback，不是已批准模型。
- **本轮更正发现**：社区表 `sub_commuID` 空值以空格存储。第一次快速汇总把空格误计为有效值；清洗后仍无法确定拆分父社区内每名受访者所属的最终子 PSU。精确键计数和 ID 只留在服务器受保护 QA，不写入 GitHub。
- **空腹代码搜索已穷尽当前本地官方公开材料**：CHARLS 官方 Wave 1 页面只列通用 Codebook、Blood Users' Guide 等；Blood ZIP 内只有 Stata 文件；`qc1_va003` 无 value labels，官方公开资料没有2011数值/特殊缺失码映射。2015 相近字段的 1/2 编码仍不能外推。证据见 [`wave1_fasting_code_source_review_2026-10-29.md`](wave1_fasting_code_source_review_2026-10-29.md)。
- **补查 Wave 1 官方体检问卷**：搜索官方归档的 Physical Examination Questionnaire 提取文本及 Blood Guide 完整文本层，未找到 `qc1_va003` 或空腹字段数字选项；体检问卷不能作为代码映射依据。该发现已记录在空腹代码来源备忘录。当前官方公开资料的搜索范围已包含通用 Codebook、Blood Guide、体检问卷、Blood 归档成员和 Stata value labels；若授权 CHARLS 账号后续有正式更正文件再纳入。
- **本轮完成15项结局尺度目录**：新增 [`wave1_outcome_scale_readiness_2026-10-29.md`](wave1_outcome_scale_readiness_2026-10-29.md)，列出15项非 cystatin C 血检结局的 Wave 1 字段、原始单位和官方指南测定范围；明确测定能力范围不是分析有效值过滤线，也未据此冻结变换。仅核读受控 Blood 文件的变量标签和值标签元数据：检测字段标签提供测量名称/单位线索，15项结局字段及 `qc1_va003` 均无值标签集；未读参与者记录。
- **历史状态更正**：[`wave1_biomarker_outcome_validity_and_scale_gate_2026-10-27.md`](wave1_biomarker_outcome_validity_and_scale_gate_2026-10-27.md) 曾写 Wave 1 输入尚未入库；已保留原文并追加10月29日状态更正，注明四类输入现在已完成受控入库，但分析仍未放行。
- **准入执行器复核**：静态检查冻结模板/runner：必须冻结配置、逐项声明15结局变换与有效值规则、填入审阅来源/审核人，并通过绑定准备表和方案哈希的私有 readiness record；设计项限定为当前实现支持的 Taylor 线性化和明确 singleton 策略。没有发现可绕过阻断门的空配置路径。空腹模型目前只支持保留全体/限制子域，不支持协变量调整；已经写入独立审阅包作为待裁决的软件需求，未擅自实现。
- **官方抽样说明补强**：重新核对 CHARLS 官方样本设计网页与 Wave 1 用户手册，确认 county 层按地区/城乡/GDP 排序分层并PPS抽取，社区层每县抽取3个PSU；大型社区可拆为子社区PSU，30个社区采用拆分；血检非应答有专用权重，子社区占父社区比例参与权重构造。权重不提供受访者的最终子 PSU 键，也不能补足方差设计变量。证据及推论边界已补进 [`wave1_variance_estimator_decision_matrix_2026-10-29.md`](wave1_variance_estimator_decision_matrix_2026-10-29.md) 和独立审阅包。
- **县级键拓扑受控 QA**：只使用受保护 Wave 1 `PSU.dta` 的省、市与社区键汇总结构，未读取个人分析表。省/市文本标签不是官方县级抽样单元的一对一键，不能据此构造县级 strata 或 first-stage PSU。准确聚合数和方法注记只存于本机受控 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\qa_outputs\`；GitHub 文档仅记录不含计数和地名的审慎结论。
- **官方 Codebook 字段清单交叉核验**：2011 Codebook PSU 节（印刷页1340–1341）列明 `communityID`、`province`、`city`、`urban_nbs`、`areatype`，没有县级 sample-unit ID/strata；与实际 `PSU.dta` 表头相符（版本字段仅作发布元数据）。详细来源核对已加入 [`wave1_official_design_file_inventory_review_2026-10-29.md`](wave1_official_design_file_inventory_review_2026-10-29.md)。
- **状态更正（2026-10-29 19:39）**：本机受保护入库现有 Wave 1 四件套、Wave 2 PSU/权重（官方文档319/318）、Wave 3 样本信息/权重/血检（1151/1152/2088）、Wave 4 权重/样本信息（2106/2107）和 Wave 5 权重/样本信息（2210/2209）。Wave 2 PSU表头及新增五个 Wave 3–5 设计包先与服务器私有清单中的 SHA-256 比对，服务器清单显示其已通过官方 SHA-1 校验，然后仅做 Stata metadata-only 表头审核。机器可读报告和原始包均仅存受控本机/服务器目录。官方逐波权重解释见 [`multwave_official_weights_blood_source_review_2026-10-29.md`](multwave_official_weights_blood_source_review_2026-10-29.md) 和 [`multwave_weight_estimand_matrix_v1.md`](multwave_weight_estimand_matrix_v1.md)。独立方法审阅目录仍空；正式关联模型未获准。Pages 首页 HTTP 200，`association_results_v1.json` HTTP 404。
- 下一动作：并行推进两项未决方法门：①为生日历法转换取得受保护环境可用的 Stata 执行路径，或设计经官方查找表验证的实现；先用合成日期验证，再审核 CHARLS DOB 路由/日期优先级/年龄域；②收敛县级分层与最终子 PSU 方差裁决及空腹字段来源审查。任何真实模型仍须先通过逐波设计方法独立审查、冻结方案与 disclosure gate。

- **官方抽样文件清单补查**：CHARLS Wave 1 官方公开数据页列有 All Data、PSU、Weight、Community、Blood 等，但未列独立 Sample Information、复制权重或方差层文件；2018 User's Guide 所述 Sample_Info 是回应/横截面/死亡/访谈日期元数据，不能外推成Wave 1子PSU映射。详细证据及限定见 [`wave1_official_design_file_inventory_review_2026-10-29.md`](wave1_official_design_file_inventory_review_2026-10-29.md)。当前调查设计门仍未通过。

- **执行器能力边界与方法文档复核（19:23）**：锁定环境为 `svy==0.35.0`。包的 `Design` schema 有 PSU/SSU、复制权重及两阶段 `PopSize`；`GLM.fit` 支持显式 `method="replication"`。`svy` 官方文档也说明其抽样组件可构造三阶段链，Taylor方差按 strata 内首阶段 PSU 总量作 ultimate-cluster 估计，较低阶段分层进入权重但不作为方差分层。项目 runner 仍只组装一个 PSU、将 GLM 固定为 Taylor并拒绝复制权重，且回归 GLM 路径的 FPC 只取 PSU 层因子。故软件具备部分相关结构，但现有项目模型路径及 CHARLS 发布键不能直接表达已说明的完整设计。CHARLS 已审发行包未见官方复制权重，不能用任意生成替代设计证据。方案 A 受县级/strata/子 PSU 键缺口阻断；方案 B 的社区 ultimate-cluster 近似须独立判断目标总体、拆分社区处理与自由度。方法矩阵已加入[官方 GLM](https://svylab.com/docs/svy/tutorials/glm.html)和[多阶段](https://svylab.com/docs/svy/tutorials/multistage.html)依据。下一步针对 GLM 的 ultimate-cluster方差与多 strata/自由度映射收敛审阅问题；未运行模型或测试。

- **范围和状态澄清**：历史105项是水源1个对比加烹饪燃料6个对比，共7×15个候选假设；当前登记的后续K150主块与K90供暖子域是不同扩展阶段，共240个登记候选行。它们都不是样本量。历史探索性模型曾经运行过；“正式模型=0”指当前没有通过来源、抽样设计、冻结方案和独立审查的正式/可发布模型。执行器仍需补充M1/M2关系与空腹调整配置支持，详见 [`wave1_family_runner_scope_review_2026-10-29.md`](wave1_family_runner_scope_review_2026-10-29.md)。

- **已完成的设计字段核验**：仅检查受保护服务器的 Stata **表头元数据**，没有读取受访者答案。15个模块表头全部核对完：`community.dta` 有 `sub_commuID` 与 `communityID`；另14个模块均未发现 `sub_commuID`。`health_care_and_insurance.dta` 的 pyreadstat 表头读取失败后，改用 pandas Stata reader 的 header-only 路径成功取得变量名（Stata 113，480个变量），没有读取观测。
- 官方 `PSU.dta` 表头含 `communityID`、省/市、城乡/地区类型和版本字段，没有子 PSU、显式方差层或复制权重字段；Weight 表有社区/家庭/个人键及多种权重，Blood 文件有 `bloodweight`。因此目前没有发行文件证据可将社区子区对应到个人，也没有完整的官方方差字段。
- 服务器只读准入校验结果：官方来源身份及 Wave 1 准备表 provenance/hash 门 **passed**；真实分析就绪门 **blocked**，原因是缺少绑定当前来源和冻结方案的审阅记录。模型未运行。
- **方法审阅材料**已整理在 [`wave1_independent_methods_review_packet_2026-10-29.md`](wave1_independent_methods_review_packet_2026-10-29.md)。105项构成和类别编码已核对；当前脚本遗漏血糖/甘油三酯的空腹条件处理。官方指南说明非空腹者也采血且非空腹血糖可能偏高；`qc1_va003` 在Stata文件中没有值标签，当前官方Codebook/Guide未给出具体代码。
- **官方空腹代码检索结论**：CHARLS 官方 Blood Guide 证实未空腹者仍采血并记录状态，且非空腹血糖可能偏高；官方 Wave1 数据页只列通用 CodeBook 和 Blood Guide，Blood 压缩包也无辅助数据字典；Stata 字段无值标签。官方2015 CodeBook的相近字段 `bl_fasting` 为1=Yes、2=No，但不能证明2011编码一致；第三方索引仅作线索。详见 [`wave1_fasting_code_source_review_2026-10-29.md`](wave1_fasting_code_source_review_2026-10-29.md)。
- **审阅材料状态**：逐项准入矩阵已并入 [`wave1_independent_methods_review_packet_2026-10-29.md`](wave1_independent_methods_review_packet_2026-10-29.md)；官方 Codebook 字段清单和受控 PSU 键拓扑 QA 都支持“现有发行包未提供县级样本单位/显式方差层/最终子 PSU 的个体链接”这一设计限制。官方样本设计来源已确认：设计确含县级排序/分层、系统PPS与子社区抽样/权重比例调整；官方公开来源目前没有2011 `qc1_va003` 数值/特殊缺失码；不得从2015或参与者值反推。设计与测量准入未通过前不拟合。
- **本阶段不启动真实关联模型**，直至样本框、权重、PSU/方差方案和冻结分析计划全部获审。服务器当前没有关联分析进程；active 目标会在后续任务轮次继续，不代表常驻计算。

### 后续执行顺序

1. 完成 Wave 1 PSU/方差调查设计审查并记录独立审阅结论。
2. 冻结105项试点的目标、结局有效值/单位、协变量角色、假设族、诊断和敏感性分析。
3. 通过来源、设计、方法门后，运行并独立复核105项真实试点；按估计可行性、样本支持、诊断和稳健性判断是否扩展，不按显著性筛选。
4. 试点获方法审查后运行 K=150 家庭暴露主块及 K=90 供暖路由子域，再逐波完成来源和设计准入。
5. 对完整主检验族重算图谱级多重校正，完成披露审查，再将获准聚合结果放入网站。

**已完成的准备**：官方来源确认、Wave 1 受限准备表重建、15模块表头审查、血检目标与 `bloodweight` 首轮核对、结果发布安全门及结果浏览器。**还未完成**：正式方法准入、真实关联模型、全图谱真实结果与结果上线。

## 当前执行中的工作

### W1.1 官方 Wave 1 入库和来源核验

- **已完成（本机受控目录）**：All Data、PSU、Weight、Blood 四项文件被识别；RAR 成员清单和 Stata 文件头元数据预检完成。未读取受访者回答。
- **已完成**：用户确认四个文件由本人获准 CHARLS 账号下载，对应官方文档 123、117、118、201；确认记录已写入本机受保护 manifest。SHA-256 是本地文件身份指纹，不是 CHARLS 官方校验和。
- **已完成（服务器）**：私人目录内的 RAR 解包工具已就绪；All Data 的 15 个 Stata 成员 CRC 检查通过，四项文件哈希与本机审核 manifest 对应；服务器 metadata-only 预检完成。
- **已完成**：Wave 1 受限准备表重建成功；来源 manifest、Stata header 和合并 QA 均在服务器受保护目录 `private/derived_wave_tables/`。输出文件权限为仅本人可读。
- **修复记录**：首次写出因全缺失 object 列类型推断失败；写出器现将全缺失列编码为 Stata numeric missing，保留列名与变量标签，并拒绝空 respondent 表。修复脚本已在服务器运行成功。
- **当前动作**：按官方资料已完成 Wave 1/2/3 权重首轮审查，并已从受控 Wave 3–5 样本信息/权重包读取表头；逐波目标、样本旗标、模块权重和面板权重缺口已整理成 [`multwave_weight_estimand_matrix_v1.md`](multwave_weight_estimand_matrix_v1.md)。详细血检/来源结论见 [`multwave_official_weights_blood_source_review_2026-10-29.md`](multwave_official_weights_blood_source_review_2026-10-29.md)。
- **当前结论**：常规血液结局使用专用 `bloodweight`；45+ 目标应作为 survey domain/subpopulation；基线配偶可低于45岁。胱抑素 C 有额外随机检测子样本，暂不纳入同一主族。
- **仍阻断**：官方说明有30个大型社区按子社区抽样，但已核对的发布字段未提供明确受访者—子 PSU 对应；显式方差层/复制权重或官方方差估计建议也尚未找到。不得用地理变量拼造分层，或把 `communityID` 近似称作完整设计。
- **放行标准**：获得可追溯子 PSU/方差方法证据，或由独立方法审查批准并清楚标记的近似估计方案；之后才冻结并运行正式105项试点。
- **当前候选方差审查材料**：[`wave1_variance_estimator_decision_matrix_2026-10-29.md`](wave1_variance_estimator_decision_matrix_2026-10-29.md)。社区子区空白键已按空格清洗重新核对；拆分社区的 respondent-to-final-PSU 归属仍无法从现有已审键识别。
- **安全边界**：个人级文件只留服务器受保护目录，不进入 GitHub、OneDrive 或 Pages。

## 阶段路线、产出与估时

估时为有效工作时间范围，按门槛可验证、阶段有先后依赖；不含等待 CHARLS/机构审批、独立审稿人排期、论文写作和投稿周期。

| 阶段 | 内容与交付物 | 当前状态 | 粗略有效工作时间 |
|---|---|---|---:|
| 1. Wave 1 来源与重建 | 元数据核验、来源 manifest、重建表与血检/PSU/weight 连接审计 | 来源核验与 Wave 1 准备表重建已完成；连接 QA 方法性审查继续 | 主要计算已完成；余下审查约 1–3 个工作日 |
| 2. 目标总体和抽样设计 | 样本框、年龄域、血检资格/非应答权重、PSU 映射、方差估计审查 | 未通过；PSU拆分与方差方法是最大未知项 | 3–10 个工作日，若需外部方法确认则更久 |
| 3. 105 项 Wave 1 试点复核 | 冻结模型、重跑、诊断、敏感性检查、独立方法审阅 | 历史运行仅作探索记录；正式审查尚未开始 | 3–7 个工作日 |
| 4. Wave 1 扩展 | K=150 家庭环境主块、K=90 路由供暖子域，固定范围/尺度/多重校正输入 | 计划和执行器已有；等待前序放行 | 3–7 个工作日 |
| 5. 其他波次 | 2013/2015/2018/2020分别审核变量、样本、权重、PSU/方差、测量可比性并运行 | Wave-specific 准入和数据输入仍需逐波完成 | 2–5 周，取决于波次门槛 |
| 6. 全图谱结果与披露 | 完整主检验族、atlas-wide BY/Bonferroni、稳健性/可估性与披露审核 | 工具与发布合同已有；真实结果未形成 | 1–2 周 |
| 7. 网站结果上线 | 只发布获准聚合数据；复核过滤/热图/下载与公开说明 | 网站原型在线；尚无批准结果 JSON | 2–5 个工作日 |

**当前排期估算**：若抽样方差门可由公开资料和已获发行文件闭环，Wave 1 基线主线约需 2–4 周有效工作时间；达到多波次、结果审核和网站发布的完整项目约需 6–12 周有效工作时间。若官方资料不能支持代表性方差估计或需 CHARLS/机构另行确认，日历时间会延长；不得通过臆造分层或跳过审查来压缩时间。

## 当前会话执行清单（2026-10-29）

1. **当前执行：Wave 1 设计准入审查** — 对照官方指南逐项核实样本框/年龄域、血检资格、权重、PSU/子 PSU 与方差方法。
2. **当前并行：完善锁定分析计划** — 已整理15项结局公开单位/测定范围及准入矩阵；继续审计 105 项冻结配置是否完整表达有效值、估计量、协变量角色、完整假设族、诊断与敏感性分析，并明确仍需独立方法审阅确认的选项。
3. **放行后：运行 105 项试点** — 仅在来源、设计和方案门全部通过后拟合；以估计有效性、收敛、样本支持、稳健性和可重复性判断是否扩展，不按 p 值选择。
4. **试点通过后：扩展 K=150/K=90** — 按冻结范围执行并逐波审查；完成全图谱校正和披露审核后才发布获准的聚合结果。

每完成一步，更新本文件和 `logs/progress_log.md`，记录日期、证据、下一动作和阻断。项目目标显示 active 代表目标仍进行中，不代表每个计算进程都持续运行。仓库首页已链接此状态页，可从 GitHub 的 `audit/ACTIVE_WORK_PLAN_2026-10-29.md` 查看。

### 2026-10-30 Codebook 归档补充

在 `C:\charls_raw` 暂存区发现官方 Wave 1 Codebook 归档，平台 MD5 核验通过；归档内 PDF 与受控参考区已有官方 PDF 的 SHA-256 一致。定向检索未发现 `qc1_va003` 代码定义，因此这项来源搜索现已完成但仍未解决 fasting 编码。归档和 PDF 只保存在 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\references\official_charls_codebook_2011\`；不进入代码仓库、OneDrive、服务器或网站。其余正式分析门不变。后续依次推进：取得新的正式字段释义（如用户从获准渠道获得的专门更正材料）、完成年龄/目标总体与方差设计的独立审阅、冻结分析计划并重审105项试点；在这些门通过前模型数保持0。

### 2026-10-30 Wave 1 官方计数口径

基线指南的访谈总数为 17,708；Table 4 的 17,587 是排除缺年龄、性别或户籍者后的描述表子集，不能作为完整分析框。这个官方 121 人表格差额与受保护 ID-only 文件核对中 Weight 到人口学主表的 3 人链接差异分别记录；后者仍待解释，但三人不在 Blood 文件。详见 [`wave1_official_denominator_interpretation_2026-10-30.md`](wave1_official_denominator_interpretation_2026-10-30.md)。这只澄清分母语义，不解除目标年龄、PSU/方差和独立方法审查门。

## 不可跳过的决策门

1. 来源身份和文件版本；
2. 目标样本框、问卷/血检资格、年龄域和权重适用性；
3. 最终 PSU 映射及可辩护的方差方法；
4. 冻结变量、结局有效值/量纲、模型、完整假设族和诊断标准；
5. 独立方法审查；
6. CHARLS 数据使用许可允许的发布范围及逐结果披露审核。

显著性不作为扩大范围的选择条件；不把合成校准、软件测试或候选配对数量称为真实科学结果或样本量。

## 可以并行的省时工作

- 数据准入期间并行修复代码、运行合成流程、更新数据字典映射和网站空结果界面；
- 对所有 Wave 1 源包做一次批处理和一次性重建，避免每个模块重复全量运行；
- 先完成 2011 基线，不等全部波次到齐；每个后续波次用独立 gate，不强行套同一权重/方差配置；
- 把 NHANES 的目录驱动、批处理模型、统一输出、失败行保留和结果浏览器结构复用；不复用 NHANES 权重、周期 meta-analysis、500 人门槛或变量定义。

## 更新记录

- 2026-10-29 21:38（Asia/Shanghai）：再次核验受保护服务器上的官方 Wave 2 权重包与 Wave 3 血检包。服务器私有分析环境已可导入 `pyreadstat 1.3.1`；两包均通过官方 SHA-1 与仅表头预检，摘要报告只写入权限为 owner-only 的 `private/qa_outputs/`。此步骤未读取受访者值/ID、未合并或拟合模型。Wave 1 输入仍齐全，但年龄算法和最终 PSU/方差设计审查未闭环；正式关联模型仍为 0。线上首页 HTTP 200、结果 JSON HTTP 404，符合当前未发布正式结果的状态。

- 2026-10-29：四项 Wave 1 官方来源经用户确认，哈希与服务器副本对应，metadata-only 预检完成；服务器 RAR 工具已在私人目录配置并通过 All Data CRC 检查。首次 Wave 1 重建于 Stata 写出时失败，原因定位为全缺失 object 列类型推断；本地已加修复，服务器重跑待执行。正式关联模型数仍为 0。
- 2026-10-29（状态更正）：Wave 1 受限准备表重建现已成功；首次写出失败由全缺失列类型处理修复。当前步骤已切换为样本框、年龄域、权重、PSU/子 PSU 和方差估计准入审查。此前同日记录中“重建待执行”已由本条更新覆盖。正式关联模型仍为 0。

## 2026-10-29 当前设计审查的具体下一项

核查 Wave 1 官方材料/发行文件中是否存在最终子 PSU 映射、方差层或复制权重。若没有，则整理仅以 `communityID` 聚类、明确标记为近似的候选方案并完成独立方法审阅；在审阅决定前不拟合正式关联模型。审查依据及45+ domain、血检专用权重和胱抑素 C 子样本决定见 [`wave1_estimand_weight_psu_variance_gate_2026-10-29.md`](wave1_estimand_weight_psu_variance_gate_2026-10-29.md)。

- 2026-10-29（设计审查更新）：首轮审查确认血液化验需按官方血检目标与 `bloodweight` 处理；45+ 估计应使用 survey domain 保持完整设计；基线配偶不限年龄。胱抑素 C 的随机二阶段检测尚未找到对应权重说明。官方说明存在30个拆分社区，已核对字段未提供子 PSU 对应键；显式方差层/复制权重也未确认，因此调查设计门继续阻断，正式关联模型仍为0。

- 2026-10-29（方差设计键复核更正）：`sub_commuID` 的空格空值已规范化后重算；拆分父社区内的 respondent-to-final-PSU 归属仍不可从已审发行键恢复。新增候选方差估计决策矩阵，供独立复杂抽样审阅；未拟合真实模型。

- 2026-10-29（多波次入库与官方权重审查）：在本机受保护目录发现并核验 Wave 2 权重（文档318）、Wave 3 权重（1152）与 Wave 3 血检（2088）；仅进行压缩包成员与 Stata header 元数据检查。官方发布说明确认 Wave 2 有横断面/纵向权重及横断面 biomarker weight，但无纵向 biomarker weight；Wave 3 血检只发布横断面 `Blood_weight`，面板血检权重需按研究目的另行构造。2015 `bl_fasting` 标签为1=Yes、2=No，仅适用于该波，不能推断2011编码。详细审查已记录；模型门仍因样本设计、链接、冻结计划和独立审查未通过而关闭。

- 2026-10-29（Wave 3–5样本信息和权重准入更新）：按服务器官方 intake manifest 的 `verified_official_sha1` 状态检查2015样本信息、2018权重/样本信息、2020权重/样本信息；逐个本地副本 SHA-256 与私有 manifest 匹配后，metadata-only读取 Stata 表头。公开用户指南确认Wave4/5提供横断面权重并由 `Sample_Infor.crosssection` 识别横断面样本，不提供通用面板权重；Wave4 HCAP属于特定年龄框，非全体45+常规表型。报告与输入只保存在本机受控目录。新增逐波目标/权重矩阵供审阅，正式分析仍未放行。

## 2026-10-29 年龄输入来源核对更新

已完成 Wave 1 年龄字段来源核对及受保护的最小输入表准备：源绑定 respondent 表有官方出生年月日 `ba002_1`–`ba002_3`、历法路由 `ba003` 和条件自报年龄 `ba004`，但没有访谈年月；官方 `Weight.dta` 有 `ID`、`iyear` 与 `imonth`。新增脚本先对照已复核 intake/prepared-table manifest 与当前文件 SHA-256，检查源字段表头和 ID 唯一性，再按 ID 一对一连接。数据只留在受控本机目录和服务器私有目录；逐行输入和精确 QA 均不进入 GitHub。该步骤已读取出生日期字段但未作历法转换、年龄计算或暴露/结局分析。

官方基线问卷对未知月份/日期使用 0，只询问公历或农历，未发现独立闰月回答字段。故不得擅自尝试公历、普通农历、闰月农历并择其“最合理”结果，也不得把 Harmonized CHARLS D 年龄作为正式年龄替代。CHARLS 官方 `lunar2solar` Stata 程序和矩阵已固定版本，但当前本机及服务器未发现可用 Stata。年龄输入联表现已完成；年龄算法及转换验证仍未通过。后续须先用合成日期验证兼容实现或找到获授权 Stata，再对受保护日期计算年龄并只保留聚合 QA，不向仓库或网站写入个体日期、转换明细或小单元 QA。

该字段来源进展不改变年龄定义、45+ domain 或调查设计准入状态；最终年龄算法仍须方法审查，PSU/方差门也仍关闭，正式 CHARLS 关联模型数仍为 0。

## 2026-10-29 — Clarify Python reference lineage for official lunar conversion

The official CHARLS `lunar2solar.sthlp` explicitly cites `lidaobing/python-lunardate` as the basis of the Stata conversion. The upstream project page identifies GPL-3.0 licensing and example conversions; PyPI release history dates lunardate 0.1.5 to 2014-09-09, after the CHARLS help version dated June 2014. This is a promising synthetic-validation reference, but the upstream revision used by CHARLS is not specified and does not prove exact `.mmat` parity. A license-aware, pinned-source synthetic review is next; no participant DOB conversion or association model is authorized by this evidence alone.

## 2026-10-29 年龄算法参考源固定

已将 PyPI `lunardate` 0.1.5 源码包下载到受控本机参考目录，并以 PyPI 页面所列 SHA-256 验证包身份；没有把源码包复制进 GitHub。源码元数据为 GPLv3，转换表覆盖农历年1900–2049，接口要求显式 `isLeapMonth`。CHARLS 官方 Stata 帮助文件确实引用该 Python 项目，但未说明版本，且 0.1.5 在官方帮助文件版本之后发布，PyPI 无构建来源证明。因此它只是固定版本候选，不能声称已经复现官方 `.mmat`。目前只静态阅读，未执行示例或处理受访者日期；后续需使用获授权 Stata 建立直接对照，或由独立方法审查明确接受其版本与闰月不确定性后再决定年龄算法。

**2026-10-29 synthetic lunar conversion comparison:** Compared locally pinned `python-lunardate` 0.1.4 and 0.1.5 on seven synthetic lunar dates, including a leap-month example and calendar endpoints. Both versions returned identical outputs and conversion tables. This checks cross-version consistency only; it does not establish parity with CHARLS's official Mata `.mmat`, and no participant DOB was read or transformed. Age derivation remains blocked pending official-output validation or independent approval of an alternative, then review of date-response coding and survey-domain eligibility. Details: [`lunar_conversion_candidate_synthetic_crosscheck_2026-10-29.md`](lunar_conversion_candidate_synthetic_crosscheck_2026-10-29.md).

**2026-10-29 official sample-frame detail:** Rechecked CHARLS's current Sample page and recorded that 150 county units were initially selected, while boundary changes caused the final sample to cover 156 county-level units; six communities were replaced under the stated selection procedure. This further rules out treating released province/city labels as a ready-made first-stage PSU/county key. The 40–44 refresher screening path and 45+ main-respondent-plus-spouse blood target were cross-referenced. No participant values or model outputs were used; design gate remains unresolved. See [`wave1_variance_estimator_decision_matrix_2026-10-29.md`](wave1_variance_estimator_decision_matrix_2026-10-29.md).

**2026-10-29 Wave 2/3 source-gate execution:** The standalone official 2013 weights ZIP and 2015 Blood ZIP were rechecked against their CHARLS-published SHA-1 values. A code review found the previous Wave 2 gate incorrectly compared the ZIP checksum with the extracted DTA; the audit now verifies the ZIP first, then checks the unique `Weights.dta` header in protected temporary storage, while the downstream merge requires the DTA to byte-match that verified archive member. The 2013 header has the required sample flags and weight fields. The 2015 Blood archive passes its official hash and its `Blood.dta` header matches the release row count/schema. These are provenance/header checks only; no IDs, flag/weight values, merges, associations, or participant-level data were inspected. No merge or model ran. Protected QA is in `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\charls_available_intake_gates.json`; source/design/model gates remain open.

## 2026-10-29 23:29（Asia/Shanghai）— Wave 1重建与年龄候选的本机/服务器一致性核验

服务器已使用当前源绑定脚本，在版本化私有目录完成 Wave 1 respondent 表重建；本机与服务器重建表的行列规模一致，字段名集合一致，但 DTA 字节哈希不同，故不宣称文件字节一致。后续对受保护年龄候选表按 ID 排序、规范化有限候选列后计算内容摘要，本机与服务器摘要一致，表明年龄候选逻辑内容一致；摘要不包含可读 ID 或个体值。双方均保留各自在受控目录中的私有文件。

本轮确认本机和服务器的受保护 Wave 1 四件套仍在位；服务器新重建目录和年龄输入/候选表均存在且私有目录权限为 owner-only。年龄候选仅是尚未审查的方法实现；尚未通过官方 `.mmat` 逐项对照、条件自报年龄可比性审查、45+ survey domain 审查，也未解决最终 PSU/方差设计。未加载暴露或结局，未运行任何正式关联模型，模型数仍为 0。下一步先将当前计划与方法审查记录同步到私人服务器，并继续依据官方样本设计材料审阅 PSU/方差候选；任何方法门未通过前不拟合真实关联。

## 2026-10-29 23:39（Asia/Shanghai）— 纠正 Wave 1 县级键判断并补齐官方转换矩阵来源

重新完整阅读官方 Wave 1 Users' Guide 的 ID 章节后发现：9 位 household ID 的前六位依次标识省/市/县，第七位标识县内社区，个人 ID 在 household ID 基础上增加两位。新增 `scripts/audit_wave1_county_prefix_design.py`，以已审核的 prepared-table manifest 与官方 PSU 文件 SHA-256 为前置门，在受保护本机和私人服务器核验 person/household/community 前缀、社区键覆盖和县/社区拓扑；两端均通过，且结构符合官方指南的抽样框描述。该结果提供可重建的 county-prefix 候选键，修正此前只因 PSU 表没有单列 county ID 而认为县级键缺失的判断。它仍不能恢复隐式分层与县级系统 PPS 顺序/尺寸，也不能建立拆分社区到 respondent 的最终 sub-PSU 映射；方差准入仍未通过。

另外，官方 `charls-data/lunar2solar` 仓库确实包含 `lunar2solar.mmat`。已将该文件下载到受保护参考目录，并核对当前仓库文件与项目已固定的上游 commit 文件字节相同。该文件为 Mata 二进制矩阵；本机和私人服务器均未找到 Stata 可执行程序，因此仍不能读取官方表并做逐项转换 parity。先前“官方 `.mmat` 未找到”的描述更正为“文件已找到，但缺少授权 Stata 读取能力”。未处理新增受访者日期，未加载暴露/结局，未拟合关联模型。

## 2026-10-29 23:45（Asia/Shanghai）— 复核历史探索性试点输出并明确正式模型计数
在受保护本机发现 2026-10-26 留存的探索性水源/家庭环境—血液表型分析输出。运行既有聚合完整性审计：结果表结构、拟合字段完整性、数值范围及声明的 BY/Bonferroni 校正算术均通过；审计未读 CHARLS 个体记录，QA 只保存在 `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\pilot_technical_integrity_aggregate.json`。原始运行清单明确标注该结果不可发布，年龄协变量来自 Harmonized CHARLS D 候选，PSU 用未分层 communityID Taylor 近似，源归属、总体分母和设计方差仍未验证。因此这些仅是私有历史探索输出，不能算正式或审查通过的 CHARLS 关联模型；正式可用模型数仍为0，公开站点结果 JSON 仍缺失。此前日志用“模型数0”概括状态时没有说明历史探索性拟合，现以此条补全区分；不删除或复制旧结果。

进一步核对服务器的 R 环境：R 4.5.3 与 `survey` 4.5 已安装。官方 `svydesign` 文档说明，多阶段 id 可以表达各级抽样簇，但不提供 FPC 时只用第一阶段计算方差；只给部分阶段 FPC 时，后续未给阶段被视作完整抽样。因此不能通过改用 R 或添加 county/community 两个字段就声称二阶段方差已解决。新增 [`wave1_multistage_variance_software_review_2026-10-29.md`](wave1_multistage_variance_software_review_2026-10-29.md) 记录软件能力与设计信息缺口；仍待正式方法裁决。此轮未拟合任何真实模型。

## 2026-10-29 23:47（Asia/Shanghai）— 限定县级前缀的抽样单元身份
复核 CHARLS 官方 Sample 页面第55行后，发现必须将上一轮的县前缀结论限定：该页称150个县级单位最初入样，但6个样本社区因行政边界变化落入额外县且未被替换，最终实际地理县级单位数为156。当前 ID 前缀聚合结构为150组、每组对应3个样本社区，与最初入样单元数相符；但现有官方 ID 说明没有明确说该前缀代表“原始第一阶段入样县”还是“最终实际地理县”。因此前缀只能称县级编码/分组候选，不能在独立核实前标记为已确认 first-stage PSU。已更新审计脚本，报告该差异并继续只写私有聚合 QA；更新多阶段设计备忘录。county/community键形态核验仍通过，县级样本单元身份及方差估计仍未通过。没有拟合新模型。

## 2026-10-29 — Private historical pilot scope reconciliation

A metadata-only key audit compared the historical exploratory result files with the predeclared `prior_pilot_overlap` metadata. It found that the register's 105 tagged rows represent fewer unique exposure–phenotype pairs because one pair can have multiple planned contrasts. The historical pilot and extension files do not form an exact set match to the registered overlap: the extension contains pairs outside that registered overlap. Exact aggregate counts are recorded only in the protected local QA report `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\historical_pilot_pair_scope_private.json`; no pair IDs, estimates, p-values, or participant values were emitted. This audit does not validate the historical models and does not change the approved real-data model count, which remains zero. Review/freeze the pilot-to-register crosswalk before any attempt to reproduce historical associations.

## 2026-10-29 — Corrected contrast-level reconciliation

The initial pair-scope audit keyed only on broad exposure concepts and phenotype concepts, which collapsed distinct questionnaire contrasts and produced a false mismatch. Reimplemented the audit at the registered exposure field × phenotype field × contrast level. The historical water pilot matches its registered water subset, and the extension matches the full registered 105-contrast scope. This confirms key-set coverage only; it does not assess estimates, model validity, design validity, or release approval. The earlier mismatch statement in the preceding progress entry is superseded by this correction. Formal approved model count remains zero.

## 2026-10-30 — Reconcile Wave 1 source-review note and sub-community linkage

Corrected a stale `agent_note` in the protected intake manifest that still said human source confirmation was pending, despite the manifest's verified source-review status and the account holder's recorded confirmation. This is a note-only correction; source fingerprints and the prepared-data manifest ID are unchanged. A restricted aggregate-only check of the official Community module's `communityID`/`sub_commuID` fields confirms that this sparse community-table field is not a respondent-level final sub-PSU crosswalk. The logged result is in the protected local QA directory. No geography labels or identifiers were emitted. The official guide's staged sub-neighborhood weight factor does not by itself resolve variance cluster membership; design admission remains closed.

**2026-10-30 estimand/age recommendation (not frozen):** The newest methods memo recommends aligning the primary Wave 1 biomarker analysis with CHARLS's official full blood target (main respondents plus spouses) and `bloodweight`, without mechanically excluding every spouse below age 45. Age 45+ can be a secondary survey domain. It also proposes using official DOB/calendar/interview-month inputs to derive age intervals and prespecifying lower/upper-bound sensitivities. This does not freeze the model or resolve age measurement and variance review; formal approved model count remains 0. See [`wave1_biomarker_estimand_age_recommendation_2026-10-30.md`](wave1_biomarker_estimand_age_recommendation_2026-10-30.md).

## 2026-10-30 — Draft a county-cluster variance candidate

The official guide and protected key review support considering the released county-prefix candidate as an ultimate cluster, which would retain unresolved subcommunity splits inside their county cluster. Drafted [`wave1_variance_candidate_county_cluster_2026-10-30.md`](wave1_variance_candidate_county_cluster_2026-10-30.md) with two explicitly distinct estimands: a county-cluster with-replacement approximation that omits implicit county stratification, and a community-within-county approximation conditional on selected counties. The memo states that neither is approved, neither reproduces the full CHARLS design, and Candidate A is not guaranteed conservative. It also prohibits fabricated strata/crosswalks and replicate weights. No real-data model ran; approved model count remains 0.
