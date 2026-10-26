# 2026-10-27 自动续接工作记录

## K=150/K=90 执行器实现与门禁审查（续）

- 新增本机受保护K=150/K=90执行器及专用冻结模型配置模板。执行器首先核对元数据crosswalk、四类官方源文件身份/哈希、准备表哈希、独立计划指纹、试点成功与复现审查及冻结配置；未通过任何一步都会在读参与者记录前拒绝运行。
- 冻结配置明确目标总体、全设计框架、年龄域、调查权重/PSU/分层字段、Taylor方差与局限、singleton PSU规则、六项家庭字段映射、主模型协变量、15项表型变换。执行器限定在`svy==0.35.0`已核实的Taylor接口，并拒绝未审核的replicate-weight设计。年龄和`i020=No`加热源路由保留为survey domain条件，完整设计框架进入模型引擎，不做预先物理删样。
- 本轮静态审查修正/加固singleton规则校验，清理计划指纹中的重复DAG引用；更新scale-up差距记录，使其不再误称“运行器尚未实现”。
- 继续核对`svy==0.35.0`的singleton API后发现，整设计孤立PSU和分析domain内singleton是两种不同情形；现冻结配置必须分别声明全设计方法、domain方法及domain诊断的error/warn/ignore行为。执行器显式传入Taylor估计方法，并在私有pair QA保存domain-singleton分层数。
- 加固“读数据前”配置校验：年龄/资格代码、所有暴露与参照代码、协变量中心值/二元对照/分类水平均须在受控配置中合法；问卷字段不可错误复用参与者ID。公开登记表数值候选在模型调用前做一致性检查。
- 代码仍处于未提交的审查态；仅完成源码与安装版`svy`API/静态资料核对，尚未运行关联模型。禁止运行真实模型：最新受控Wave 1门禁仍显示官方All Data、PSU、Weight、Blood缺失，且没有冻结配置/方法审批。后续只进行语法、CLI帮助、纯元数据门禁和静态审查；不读取旧派生表或个体回答。

项目：CHARLS ExWAS Atlas
执行环境：Windows本机受控项目 + 个人服务器CHARLS专属目录

## 本次做了什么

- 阅读本轮前沿进度日志、项目README和交接手册、Wave 1官方入库清单、试点成功标准/扩展路线、协变量策略、方差设计审计及K=150/K=90运行器差距记录。
- 用元数据门禁报告确认：Wave 1 All Data/PSU/Weight/Blood缺失；Wave 2 Weights和Wave 3 Blood也缺失。旧派生表和单独PSU候选不替代获准发行版。
- 只读复核服务器项目文件清单、受限目录和资源；项目目录当前仅有README、字段元数据、背景/方法决策和日志，没有CHARLS .dta/.zip/.rar数据，本轮没有上传数据或启动模型。
- 新增 `audit/pilot_autonomous_execution_decision_2026-10-27.md`，写明No-Go当前结论、何谓有效试点、协变量暂定策略、官方数据到位后的自动顺序和无数据阶段的并行工作；README新增状态入口。
- 本轮没有读取/解压参与者数据，没有重跑关联模型，没有发送CHARLS询问，没有生成或发布结果。

## 决策

此前探索脚本曾成功运行只证明软件管线可运行，不等于设计与来源有效；目前科学试点有效性尚未判定。因此暂停新关联模型，继续来源无关的变量/协变量/DAG与代码门禁准备。文件到位后按官方身份→重建/分母→目标和年龄域/权重/PSU方差→冻结105项复核→独立方法审查→K=150主块→K=90路由子域执行。扩展基于设计与复现门槛，而非p值。

## 当前待办触发条件

受控入库目录中出现用户获准下载的官方Wave 1四类文件后，先运行metadata-only预检；不完整或身份不明则停止在预检。只有来源审核和方法准入文件均通过，才建表、拟合和扩展。期间只开展不需要参与者值的资料/代码/模型计划工作。

## 本轮追加产出

已生成Wave 1家庭环境K=150/K=90候选假设登记表（240条规划项：150+90），均标注未批准/来源发行版待核/主模型未冻结。该表便于之后记录每一条假设的估计和审核状态；不含分析样本、结果或CHARLS参与者值，也不代表240条都可估。已在当前执行路线文档和README说明其状态与边界。

本轮复核发现登记表初版`primary_block`标签存在确认性误读风险，已修订为试点后探索性扩展/条件子域；表内标记与既往K=105重叠的105条假设，并限定批次校正只作临时诊断。不会把扩展结果宣称为独立确认性证据。

## 本轮追加准备

新增家庭环境暴露—血液表型协变量DAG首轮审阅，明确候选核心调整集、SES敏感性层、潜在中介/共暴露，以及调查设计变量边界。现有试点M1/M2不直接移植到K=150/K=90；主模型仍未冻结。此项只基于字段级目录和官方方法材料，不涉及参与者数据。

## 方案口径协调

发现通用分析草案的M1（年龄/性别）与家户基础设施DAG候选核心集（另含教育、社区NBS城乡）命名容易造成误读。已更新试点路线：历史M1/M2仅作既往软件规格；针对家户设施暴露，以年龄/性别层作参考、年龄/性别+经核验教育与社区背景作候选调整模型，尚未正式冻结；SES和其他可能的中介/共暴露变量仅作有DAG依据的敏感性层。最终需在解盲和拟合前冻结模型角色、估计量、来源和表哈希。

## 最新受控入库门禁复核

再次只运行 Wave 1 源档案预检及可用波次入库元数据门禁。结果仍为：2011 All Data/PSU/Weight/Blood 均为 `missing_or_ambiguous`，Wave 1 release gate 为 `not_passed`；2013 官方 Weights、2015 官方 Blood 均为 `skipped_missing_input`。报告只写在本机 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\qa_outputs`，没有读取参与者值。由于正式源包缺失，本轮不启动复核拟合或扩展模型。

## 模型审批指纹静态审查

静态检查发现 Wave 1 分析准备审批的 `analysis_plan_sha256` 此前没有绑定 2026-10-27 执行路线和家户环境协变量DAG，存在方法文件更新后审阅仍可能沿用旧指纹的风险。已把执行路线加入试点及家户扩展计划指纹，并把协变量DAG加入家户扩展指纹。另明确105项历史试点复现必须保留其原冻结M1/M2定义，K=150/K=90则另按领域DAG冻结模型，避免以新方案改写历史复现。未运行测试或读取参与者数据。

## 审批指纹和远程输入复核

重新计算当前代码绑定的计划指纹：pilot `7e25d2dca123f5e0e5936731b75f240ac9973e617e28146f29298eafe553c8b6`；household extension `293451530822a1ec812ed624bfb89970f355462d7f398648a815c94da9e90acf`。两者都纳入新的执行路线，扩展计划还纳入协变量DAG。受保护本机入库目录仍只有来源清单和说明；服务器项目树（权限600文件）也没有 `.dta`、`.zip` 或 `.rar` CHARLS输入文件。

## 全图谱候选规模口径纠正

核对主E/P crosswalk、生成器和已部署索引后，确认当前五波共561,242个非自配的元数据共现概念对；跨波去重E=1,319、P=332（26个双角色）。早期方法说明中的约29k–30k/波是历史较窄目录口径，已更正并标为过期，当前站点索引与重建表逐波一致。上述数量不代表有效分析假设、样本量或模型结果。

线上核验：GitHub Pages 的 `candidate_pair_explorer_v1.json` 当前 HTTP 200，状态为 `metadata_candidate_pairs_only`；五波 E/P 概念数和候选对数与本地交叉表生成结果逐波完全一致。本次更正仅更新审计文档与工作日志，不改变网站或模型数据。

## 受控本机文件级数据清点

对 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas` 做了文件名/扩展名盘点：27个DTA均为既有派生表、候选协变量或社区/PSU候选映射，2个ZIP为NHANES参考文件；官方Wave 1 All Data/Weight/Blood没有进入入库目录，PSU候选也未完成发行身份审核。2013 Weights、2015 Blood缺失，服务器无CHARLS微观数据。已将区分“派生准备表”与“官方授权源输入”的说明更新到复现指南；未读取数据内容、未移动或上传任何个人级文件。

## 后续自动执行准备：官方年龄转换工具固定版本

- 只读检查 CHARLS 团队公开的 `charls-data/lunar2solar` 仓库，固定到 `2284ccffdd74f057c234a446585ec32034b2d50d`；核对 README、Stata help、实现文件和 MIT license，并记录三件套 SHA-256 及农历闰月显式参数要求，详见 `audit/charls_lunar2solar_pinned_reference_2026-10-27.md`。
- 后续已把该精确版本的README、MIT license及三件套源码复制到`references/charls_lunar2solar/`以便协作者/服务器复现，复制后SHA-256与上游提交一致。未安装到Stata，也未对任何CHARLS个体记录执行转换；当前机器无Stata命令行，因此不能把工具运行验证冒充为已完成。
- 下一次官方数据到位时的顺序明确为：先确认原始波次文件/字段来源，再合成日期用例验证工具，之后依逐波路由重建年龄，最后仅输出聚合覆盖/差异QA；受保护年龄与出生日期不出本机授权目录。
- （当时的历史状态）仍未运行关联模型。Wave 1官方来源/设计门槛不通过，K=150/K=90扩展runner尚未实现；此前文档中的240条是假设登记，不是可估配对或结果。后续已实现runner，见本日志开头的执行器实现记录及`audit/wave1_scaleup_runner_gap_2026-10-27.md`。
- 检查到K=150/K=90 readiness template此前没有接入`require_verified_wave1_frame.py`，会让后续审批路由缺少专属绑定。已新增独立`household_environment_scaleup`计划入口，将来源/设计计划、DAG、假设登记表、扩展缺口审计和空白审批模板共同纳入计划指纹；它仍要求额外的pilot success/reproducibility gate，不会接受K=105审批代替。专属K=150/K=90 runner及正式模型冻结仍未完成，当前不会放行模型拟合。
- 本轮重新执行两个 metadata-only 入库入口：Wave 1 All Data/PSU/Weight/Blood 仍为 `missing_or_ambiguous`，release gate `not_passed`；Wave 2 Weights 与 Wave 3 Blood 仍为 `skipped_missing_input`。报告只写本机 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\qa_outputs`，未读取或解压参与者记录。
- 年龄转换参考说明已随代码提交 `23d7062` 推送至 GitHub；仓库工作区干净。未启动真实模型，因为官方来源及调查设计门槛仍不通过。

## 服务器项目副本同步（2026-10-27）

服务器专用项目目录不是Git克隆，而是精选的文档/脚本副本；因此将本轮更新的年龄转换审计、scale-up审批门禁审计、门禁脚本、续接日志及CHARLS公开转换程序单独同步到对应子目录。逐文件核对 SHA-256 与本地工作区一致；项目根README也与当前仓库版本对齐。未上传CHARLS原始/派生微观数据、个体级结果或私人QA。服务器副本中的分析输入门禁仍需正式数据到位后运行。

GitHub Validate：`cb6f8e2`（scale-up门禁）已成功；`8002a0c`（公开程序参考文件）核验时仍在运行，见Actions。此次服务器同步不改变数据门禁判定。

## 自动续接：入库门禁与试点后登记表审计

- 重新运行`audit_2011_pilot_intake_metadata.py`与`run_available_charls_intake_gates.py`：Wave 1 All Data/PSU/Weight/Blood均为`missing_or_ambiguous`，2011来源闸门`not_passed`；2013 Weights与2015 Blood均为`skipped_missing_input`。报告仅写在本机受保护QA目录。
- 因官方来源缺失，按已批准的Go/No-Go路线未读取既有个人级派生表、未运行真实CHARLS关联模型，也未用旧试点P/q值决定扩展。
- 新增`audit_wave1_scaleup_hypothesis_registry.py`，仅检查公开规划登记表的家族规模、交叉单元完整性、候选暴露对比、路由标记及“未批准/不可公开”状态。检查结果：K=150为10个对比×15表型，K=90为6个路由对比×15表型；两者共用15项表型，240条计划行无重复/缺失，全部仍未批准。审计明确声明不读取参与者数据、不验证源文件候选编码、不批准模型、不产生估计。
- 将该结构审计接入`.github/workflows/validate.yml`，使后续代码更新自动检查预设家族结构；更新README状态入口。下一阶段依赖官方四项Wave 1数据获准入库，随后按来源和设计门禁→复核试点→独立方法审查→K=150/K=90推进。不得跳过审核。

## 2011基线问卷来源二次核验

- 针对在线搜索易返回的2013 follow-up问卷与2011 baseline混淆，读取项目已存的官方2011基线家户问卷审计，并直接从CHARLS官方URL重新下载同一公开问卷文件做字节校验。
- 官方来源URL返回2,224,128字节，SHA-1与本地DOC完全一致（`18efb28804fdbc975e3d334c845a179493bb6221`）；本次重新计算的SHA-256为`689a7365fa93ae7996f2c352df53d4b4254edad29efe936f0f343d834828bbb1`。该哈希仅是本地文件身份记录，不是CHARLS公布的官方校验值。
- 核对边界：这增强了2011题目文字/跳转审计的来源把握；不证明受限数据发行版、Codebook与题目字段逐版吻合，也不改变当前数据门禁未通过的结论。详情已写入`SOURCES.md`与`wave1_household_exposure_questionnaire_review_2026-10-27.md`。

## 2011最终PSU/方差设计来源补核

- 重新打开CHARLS官方Sample页面并逐段核对基线抽样说明：县级单位按地区、城乡县区类型及人均GDP排序后系统PPS抽取；每县级单位抽3个社区PSU；30个大型社区可再拆子社区作为PSU；6个样本社区被替换，6个县级抽样点跨县界，最终覆盖156个县级单位。
- 因此`communityID`覆盖完整不等于最终PSU映射已认证；也不能从原始150县级抽样点、province/city或城乡代理变量推导出官方方差层。官方公开页面未提供最终拆分映射、方差层变量、复制权重或具体方差估计器。Wave 1设计门禁继续为未通过，不运行全设计关联模型。
- 已将该具体证据和解释加入`audit/survey_design_weight_review_v1.md`。来源为[CHARLS官方Sample页面](https://charls.pku.edu.cn/en/About/Sample.htm)。

## 新一轮续接：扩展候选元数据闭环（2026-10-27）

- 重新运行受保护 Wave 1 与可用波次入库门禁：Wave 1 All Data、PSU、Weight、Blood仍全部`missing_or_ambiguous`；Wave 2 Weights与Wave 3 Blood仍为`skipped_missing_input`。没有读取参与者数据或启动模型。
- 只读复核服务器专用项目目录：目录存在，未发现 CHARLS 数据档案；本机公开仓库跟踪文件清单中未发现 `.dta`、`.sav`、`.sas7bdat`、`.rdata`、`.rds` 或 CHARLS 压缩数据包。
- 新增`audit_wave1_scaleup_metadata_readiness.py`：将240条K=150/K=90规划行的16个对比与2011官方Codebook文本核对；将15项表型的候选字段/单位与血液crosswalk核对；核对`i021`仅属于`i020=No`路由；强制模型和发布状态继续未批准。审计输出为`passed_metadata_crosswalk_only`，明确声明无参与者数据读取、无模型批准、无关联结果。
- 将此审计加入GitHub Validate工作流，并更新规模扩展缺口记录和README状态入口。该改变提高正式数据到位前的编码/目录一致性把关；不替代精确发行版、目标样本框、权重、PSU/方差和模型冻结审核。
- 当前扩展真实关联分析仍不得运行；下一项可放行条件仍是 Wave 1 四项获准官方输入进入本机保护目录，随后按既定source/frame/design gates逐一核验。

## 自动续接：当前入库状态与试点后执行方案对照（2026-10-27）

- 重新运行 Wave 1 官方输入 metadata-only 预检：All Data、PSU、Weight、Blood 仍全部为 `missing_or_ambiguous`，release gate 为 `not_passed`；Wave 2 Weights 与 Wave 3 Blood 为 `skipped_missing_input`。报告写入本机受保护 QA 目录；未解压归档或读取参与者值。
- 重跑公开规划表结构与目录交叉核验：K=150/K=90 共240条计划假设，结构状态 `passed_structural_checks_only`；公开元数据核验 `passed_metadata_crosswalk_only`。两份报告均明确 `model_approved=false`、`association_results_created=false`，不代表统计模型有效或拟合完成。
- 对 scale-up runner 做静态语法检查与 `--help` CLI检查；没有调用真实数据路径或 `--run`。执行器要求明确 `--run` 且先通过来源、设计、试点成功/复现和哈希绑定的人工审批闸门。
- 修正2011入库交接手册的一处过期描述：K=150/K=90 runner、空白配置模板与专用准入门现已实现，但数据来源/模型/设计仍未获准；K=105 runner 不可替代扩展执行器。
- 试点后顺序以 `audit/pilot_autonomous_execution_decision_2026-10-27.md` 为准：认证源档案→重建与分母→目标框和复杂抽样设计审查→冻结原K=105规格并复现→独立方法评议→通过后运行K=150、再按`i020=No`路由运行K=90→跨波次分别审查→全局多重检验→独立统计与CHARLS披露审查→白名单聚合结果发布。是否扩展不依据显著性；不合并不同波次设计权重或把规划配对当作结果。
- 仍无官方微观数据可用于正式试点；本轮未创建关联结果、未更改网页数据、未上传任何微观数据。未来只有在受控入库目录发现获准输入时才可从源身份与设计门禁继续；当前继续做公开元数据、流程文件一致性和无数据依赖准备。

## 自动续接：估计状态审计与试点后文档校准（2026-10-27）

- 逐段审查 K=150/K=90 执行器的系数回收、推断状态和多重校正路径。发现引擎未返回某个系数时结果行会继承整组`fit_complete`状态；同时存在仅p值可用但标准误、置信区间或设计自由度缺失仍可能记为已估计的风险。
- 修复执行状态：缺失系数标记`term_not_returned_by_engine`；只有估计值、正标准误、有限置信区间、[0,1]内p值和正设计自由度均完整时才标记`estimated`并允许进入该批次的校正；部分推断记录标记`incomplete_inference`，原始引擎p值只保留在受保护的私有字段用于QA。
- 执行器源文件受计划SHA-256绑定，因此本次代码修改会使先前依据旧指纹准备的扩展审批失效；正式数据运行前须重新计算指纹、冻结配置并独立审查，不能沿用旧批准。
- 将试点成功标准、自治执行路线和暴露题目审核中的扩展步骤更新为“runner已实现、运行仍须门禁”；明确 K=105 和 K=150/K=90 执行器各自的范围。旧日志中的“runner尚未实现”已注明为当时状态。
- 本轮没有读取参与者数据、运行CHARLS模型或部署结果；官方 Wave 1 四项数据门禁仍未通过。代码只做静态语法/命令行与公开元数据检查，统计有效性须待正式源文件和设计审核。

## 自动续接：公开结果导出链原子性加固（2026-10-27）

- 检查公开结果发布器、结果表schema validator及Pages payload validator。确认现阶段`site-prototype/dist/association_results_v1.json`不存在，网站仍没有关联结果payload。
- 加固`build_public_association_release.py`：在写入公开目录前，先用站点实际payload validator复核刚生成的白名单JSON；输出先写入目标目录内的临时文件、flush/fsync后通过`os.replace`原子替换，若失败则清理临时文件，避免中断造成半写入公开JSON。
- 本机Python静态编译通过，现有网站dist payload validator通过，`git diff --check`通过。没有构造或发布结果、没有读取任何CHARLS参与者记录。
- 最新 intake 门禁复核仍为Wave 1四项官方输入缺失，Wave 2权重和Wave 3血检缺失。真实分析与网站关联发布仍由授权数据来源、调查设计、模型审查和逐行披露决策门禁控制。

## 自动续接：公开结果统计值一致性门禁（2026-10-27）

- 进一步检查公开JSON的CI校验：此前只验证BY q值和Bonferroni值在0–1范围内，没有在成品payload层按完整K重新计算；成功结果的标准误也允许为0。
- 已增强结果表validator：成功估计要求严格正的标准误。增强公开payload validator：按每个完整家族的所有行（包含不可估计项）重新计算BY/Bonferroni，并逐个与公开数值对照；成功结果必须具有正标准误。
- Python静态编译通过，当前站点dist通过payload validator；目前无`association_results_v1.json`，没有公开关联数据。
- GitHub前一提交`8c84d04`的Validate #743仍在检查中；本轮新修改尚未提交，待本地检查完成后再推送。

## 自动续接复核：下一阶段门禁与结果发布验证（2026-10-27）

- 从干净的`main`（`8848374`）续接；公开站点payload validator通过，`association_results_v1.json`仍不存在，站点未发布正式关联结果。
- 重新运行计划登记表结构审计和官方Codebook/表型目录交叉核验：K=150/K=90合计240条候选计划记录，状态分别为`passed_structural_checks_only`与`passed_metadata_crosswalk_only`；仍为`model_approved=false`、`association_results_created=false`。
- 重新运行可用波次入库门禁：2013 Weights、2015 Blood仍为`skipped_missing_input`；2011官方All Data/PSU/Weight/Blood受保护QA报告仍全部`missing_or_ambiguous`、release gate `not_passed`。本轮只读取聚合门禁报告和公开元数据，没有读取/解压参与者数据。
- 检查部署工作流：正式Pages发布会先执行`validate_public_site_payload.py`，随后仅打包`site-prototype/dist`并排除`catalog.json`；验证工作流包含登记表与元数据交叉审计。没有发现需要绕过或放松的安全门禁。
- GitHub Validate #744对应`8848374`。公开Actions摘要页仍标记`In progress`，页面错误而无法加载job细节；因此不能确认远端验证已结束。该状态不影响本地校验结果，但需后续核查Actions运行状态。
- 下一项真实CHARLS关联模型尚不能启动：缺少四类获准Wave 1官方输入且来源/设计闸门未通过。收到授权文件后，自动路径仍按既定顺序：来源身份→样本框/分母→权重与PSU/方差/年龄域→冻结K=105复现→独立审查→有效后K=150再K=90→波次独立审查→全局多重校正→方法与披露审查→仅发布获准聚合结果。无数据时继续推进元数据与软件发布准备，不会用候选行数或旧派生结果冒充发现。

## CI发布前校验前移（2026-10-27）

- 发现`validate.yml`虽然解析网站JSON目录、核对概念映射，但没有在每次push/PR校验中运行与Pages部署相同的`validate_public_site_payload.py`；部署流程本身已有该门禁。
- 在常规Validate工作流加入公开站点payload验证，使PR/提交阶段也会拒绝不符合schema、家族完整性、多重校正值复算或状态约束的结果payload；Pages部署前保留原有独立二次校验。
- 本地运行`python scripts/validate_public_site_payload.py site-prototype/dist`通过，`git diff --check`通过。站点仍没有`association_results_v1.json`，本次未生成或发布关联数据。

## 官方血检权重机制复核与远端CI观察（2026-10-27）

- 再次逐段核对 CHARLS 官方2011 Blood User Guide：血检目标是基线全部17,708名主受访者及其配偶，完成采血11,847人（约67%）。指南说明`bloodweight`由主调查个体权重出发，并乘以血检参与逆概率校正；参与模型使用社区虚拟变量、年龄、性别、年龄×性别及教育，逆概率因子截于第99百分位。官方同时明确该校正依赖可观测选择假设。
- 对本项目的解释：可在官方发行版字段和来源通过核验后，将`bloodweight`用于相应血检参与非响应调整；不能额外把它解释为方差分层/复制权重，也不能由此推断30个拆分社区的最终PSU设计已解决。胱抑素C的年龄分层子样本选择仍需单独处理。
- 一手依据：[CHARLS Blood Sample Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)，第13–15页；[CHARLS 2011 Wave 1官方资料页](https://charls.pku.edu.cn/en/Data/a2011_CHARLS_Wave1__Baseline_.htm)列出“All data”、PSU、Weight与Blood为不同下载项。
- GitHub `main`上的`validate.yml`已可见新加的公开payload校验步骤；但Actions工作流列表当前缓存/摘要仍停在旧运行（#730），无法从页面核实`7a032e5`对应的CI运行是否启动/完成。因此只报告代码已推送和本地validator通过，不宣称远端CI通过。
- 当前受控入库目录`incoming_2011_official`只有入库清单和说明，没有Wave 1四项源文件；正式模型仍不运行，结果JSON仍未生成。

## 候选目录计数解释纠偏（2026-10-27）

- 复核站点当前计数与`audit/charls_catalog_count_interpretation_v0.md`后发现，文档将2026-10-22的E=1,131/P=277旧候选规模标作“当前目录规模”，与2026-10-27生成口径不一致。
- 已将文档标题及旧计数明确标记为历史快照，并在开头链接当前机器生成源：截至2026-10-27为1,625个去重候选概念（E=1,319、P=332，含26个双角色），8,341条跨波E/P源字段映射。同步改写与NHANES的比较段，明确CHARLS候选数不是最终harmonized变量或可检验假设数。
- 当前源由`audit/directory_scope_counts_v1.json`和`audit/ep_concept_mapping_coverage_v1.md`支撑；没有改动站点的分析结果数据，也没有把候选数解释为实际配对或统计结果。
