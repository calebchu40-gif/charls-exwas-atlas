# CHARLS ExWAS Atlas：执行计划与当前进度

**更新时间：2026-10-29 19:45（Asia/Shanghai）**
**项目目标状态：进行中**  
**当前阶段：Wave 1 调查设计准入复核；通过现行准入的正式模型仍为 0**

本文件是本项目当前执行计划的单一状态页。每次完成阶段或遇到新阻塞时更新。GitHub 只存代码与本计划，不存 CHARLS 个体数据或受限分析输出。

## 现在正在执行什么（2026-10-29 19:45）

**正在执行：完成已获授权数据的逐波样本标记/权重元数据准入盘点，并将目标估计量与可用权重逐波绑定。**

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
- 下一动作：将逐波矩阵绑定至当前冻结的试点/扩展配置，逐项标明尚未验证的权重字段与候选观测框；同步完成 Wave 1 县级/分层及最终子 PSU 方差决策材料。方法裁决和任何获准实现都须绑定审批记录、来源清单和冻结方案哈希。Wave 1 方差方案和空腹代码/处理规则审阅通过前不拟合正式模型。

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

- 2026-10-29：四项 Wave 1 官方来源经用户确认，哈希与服务器副本对应，metadata-only 预检完成；服务器 RAR 工具已在私人目录配置并通过 All Data CRC 检查。首次 Wave 1 重建于 Stata 写出时失败，原因定位为全缺失 object 列类型推断；本地已加修复，服务器重跑待执行。正式关联模型数仍为 0。
- 2026-10-29（状态更正）：Wave 1 受限准备表重建现已成功；首次写出失败由全缺失列类型处理修复。当前步骤已切换为样本框、年龄域、权重、PSU/子 PSU 和方差估计准入审查。此前同日记录中“重建待执行”已由本条更新覆盖。正式关联模型仍为 0。

## 2026-10-29 当前设计审查的具体下一项

核查 Wave 1 官方材料/发行文件中是否存在最终子 PSU 映射、方差层或复制权重。若没有，则整理仅以 `communityID` 聚类、明确标记为近似的候选方案并完成独立方法审阅；在审阅决定前不拟合正式关联模型。审查依据及45+ domain、血检专用权重和胱抑素 C 子样本决定见 [`wave1_estimand_weight_psu_variance_gate_2026-10-29.md`](wave1_estimand_weight_psu_variance_gate_2026-10-29.md)。

- 2026-10-29（设计审查更新）：首轮审查确认血液化验需按官方血检目标与 `bloodweight` 处理；45+ 估计应使用 survey domain 保持完整设计；基线配偶不限年龄。胱抑素 C 的随机二阶段检测尚未找到对应权重说明。官方说明存在30个拆分社区，已核对字段未提供子 PSU 对应键；显式方差层/复制权重也未确认，因此调查设计门继续阻断，正式关联模型仍为0。

- 2026-10-29（方差设计键复核更正）：`sub_commuID` 的空格空值已规范化后重算；拆分父社区内的 respondent-to-final-PSU 归属仍不可从已审发行键恢复。新增候选方差估计决策矩阵，供独立复杂抽样审阅；未拟合真实模型。

- 2026-10-29（多波次入库与官方权重审查）：在本机受保护目录发现并核验 Wave 2 权重（文档318）、Wave 3 权重（1152）与 Wave 3 血检（2088）；仅进行压缩包成员与 Stata header 元数据检查。官方发布说明确认 Wave 2 有横断面/纵向权重及横断面 biomarker weight，但无纵向 biomarker weight；Wave 3 血检只发布横断面 `Blood_weight`，面板血检权重需按研究目的另行构造。2015 `bl_fasting` 标签为1=Yes、2=No，仅适用于该波，不能推断2011编码。详细审查已记录；模型门仍因样本设计、链接、冻结计划和独立审查未通过而关闭。

- 2026-10-29（Wave 3–5样本信息和权重准入更新）：按服务器官方 intake manifest 的 `verified_official_sha1` 状态检查2015样本信息、2018权重/样本信息、2020权重/样本信息；逐个本地副本 SHA-256 与私有 manifest 匹配后，metadata-only读取 Stata 表头。公开用户指南确认Wave4/5提供横断面权重并由 `Sample_Infor.crosssection` 识别横断面样本，不提供通用面板权重；Wave4 HCAP属于特定年龄框，非全体45+常规表型。报告与输入只保存在本机受控目录。新增逐波目标/权重矩阵供审阅，正式分析仍未放行。
