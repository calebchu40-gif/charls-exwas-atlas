# CHARLS Wave 1 ExWAS 试点：官方源包入库与下一阶段执行手册（2026-10-26）

## 当前决策

现有 2011 水源/烹饪燃料 × 血液指标流程已证明代码链可运行，但**没有通过正式分析的来源、目标人群和复杂抽样方差门槛**。因此现阶段不扩展新的关联模型，也不将试点估计或显著性发布到网站。下一步是从 CHARLS 官方授权账号取得并核验原始发行文件，再根据下列顺序决定试点是否可晋级。

## 官方目录中需要的资料

CHARLS 官方 Wave 1 页面把资料分成独立下载项：[Wave 1 官方目录](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)。官方[用户数据协议](https://charls.charlsdata.com/users/sign_up/agreement/zh-cn.html)规定数据仅限学术研究，不得以任何形式发布原始微观数据，分析结果不得泄露受访者个人信息，也不得向他人开放数据访问。本项目代码与基于公开资料的元数据可公开；微观数据/受限派生结果只留在授权用户的受控环境，网站仅能考虑经披露审查批准的非识别性聚合结果。本试点的最小完整源包为：

1. **Wave 1 全部数据 ZIP（文档123）**：用于从官方家户/社区模块重建住宅环境候选及协变量来源。官方页面标题为“All dataset in one zipfile including whole household questionnaire and community questionnaire data”，页面标注更新日期2013-03-13。
2. **PSU（文档117）**：用于核实最终抽样单元和当前本地 `communityID` 映射。
3. **Weight（文档118）**：用于核实基线权重来源、字段和适用总体。
4. **Blood data（文档201）**：用于核实血液分析物、`bloodweight`、目标/应答资格及与个人记录的连接。

血检定义和权重解释还需对照官方[血液数据用户指南](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)、[全国基线用户指南](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/CHARLS_nationalbaseline_users_guide.pdf)及当前 Wave 1 Codebook。官方发布页面提供的文档编号是下载入口标识，不是文件校验码；已知页面未给上述四个文件的 SHA-1，因此本地 SHA-256 只用于标识实际收到的文件，不得写成官方认证。

官方 2011 页面和发布说明指出数据需注册用户登录后下载：[Wave 1 发布说明](https://charls.pku.edu.cn/en/info/1110/1286.htm)。流程只使用具有授权的账号和官方入口；不共享账号、不上传原始数据或下载包到 GitHub、Pages、OneDrive、协作者服务器或公开网站。

## 授权下载后的固定步骤

把未改动的官方下载包放入本机受控目录，不放入项目仓库。建议目录：

```text
%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\incoming_2011_official\
  wave1_all_data.zip
  PSU.<official extension>
  Weight.<official extension>
  Blood.<official extension>
  intake_manifest.json
```

下载时保留官方页面、下载日期、页面版本/更新日期、原始文件名和扩展名。不要重命名原文件本体；如需便于脚本读取，另存经记录的工作副本。随后按此顺序执行：

受控 `intake_manifest.json` 为每类源文件保存官方文档编号/页面、官方显示标题、原始文件名、下载日期、人工核验状态和复核时记录的本地 SHA-256；顶层记录复核日期和说明，不记录 CHARLS 账号、密码或个人身份信息。来源核对完成后，由授权下载者按官方页面逐项填写并标记 `verified_official_source`，再运行预检。预检要求文件名、文档编号、页面、人工复核哈希与当前收到文件完全一致；官方校验和若未提供，保持如实记录，不影响使用“私有本地哈希已记录”状态。该状态仅表示字节指纹已留档，不证明来源身份。若输入文件字节改变，脚本会自动轮换 `source_manifest_id`、清除旧复核哈希并将来源状态退回待核；必须重新核对后才能恢复来源闸门。来源身份和哈希状态会写进受控预检报告，供后续私有运行清单引用；报告不进入仓库或网站。

1. **来源清点**：逐个核对文件名、文件大小、归档列表和本地 SHA-256；将官方未提供校验码写为“未提供”，不做猜测。拒绝内容不符、来源不明或部分下载文件。
2. **仅元数据预检**：运行 `python scripts/audit_2011_pilot_intake_metadata.py`。脚本从 Stata 文件头读取行列数和字段名，从 ZIP 读取文件清单，不解压、不读取具体受访者答案；报告仅保存在受控目录。脚本完成不等于来源身份已由代码证明，需人工保留官方下载来源证据并核验文件/模块清单。失败时停止，不作关联分析。
3. **设计与估计对象审计**：公开指南已支持把研究目标表述为全血样设计框架中的 age≥45 子总体，并在创建完整 survey design 后用 domain/`where` 估计；禁止先从框架中删掉年轻配偶。取得源文件后仍需核对精确年龄、主受访者/配偶关系、血样资格和 `bloodweight` 覆盖。再从精确版指南、PSU、Sample Info 核实社区拆分与最终 PSU/方差层。不得用省份、城乡或地区类型替代官方方差层。
4. **私有重建**：只在受控目录从官方输入重新生成分析表；审查唯一键、合并覆盖、字段来源和一致性。建表脚本现支持显式传入 Wave 1 ZIP/RAR 及独立 PSU、Weight、Blood 文件；授权文件到位且来源预检通过后，调用形式如下（将占位文件名替换成收到的原文件名）：

   ```powershell
   python scripts\prepare_charls_wave_tables.py --waves 2011 `
     --wave1-all-data "$env:LOCALAPPDATA\CHARLS_ExWAS_Atlas\incoming_2011_official\wave1_all_data.zip" `
     --wave1-psu "$env:LOCALAPPDATA\CHARLS_ExWAS_Atlas\incoming_2011_official\PSU.dta" `
     --wave1-weight "$env:LOCALAPPDATA\CHARLS_ExWAS_Atlas\incoming_2011_official\Weight.dta" `
     --wave1-blood "$env:LOCALAPPDATA\CHARLS_ExWAS_Atlas\incoming_2011_official\Blood.dta"
   ```

   输入和输出参数必须位于 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas` 受保护目录。脚本临时解包也限制在该目录下的 `tmp`，并在程序完成后清除；每个独立官方源文件的本地 SHA-256 写入本机派生表 manifest，该哈希仅作本地文件身份标识。个体 ID、记录差异和逐对 N 只在本地处理；输出到仓库的 QA 限于预先审查过的聚合来源状态，不含受访者级数据或可识别小单元。
5. **阶段 1 Go/No-Go**：若来源无法独立确认、年龄域与权重不匹配、或最终 PSU/方差设计无法解释，则暂停全国代表性推断；保留为软件演示，不继续扫描结果。若所有门槛有官方依据并闭环，再冻结试点方案。
6. **独立准入审核**：两个模型脚本除要求显式 `--run` 外，还要求受保护目录中存在与当前 `source_manifest_id`、准备表 SHA-256 和冻结分析计划匹配的审核记录。须逐项附证据，通过样本框/分母、目标总体与年龄域、权重/非应答资格、最终 PSU、方差方法及其限制、冻结方案审核后，才可启动内部探索性试点。模板为[`wave1_analysis_readiness.template.json`](templates/wave1_analysis_readiness.template.json)。该审核只准入内部试点，不授权公开关联结果。
7. **受控复核试点**：按已冻结的完整 105 系数家族重跑水源/烹饪燃料 × 15 个血液结局；检查权重分布与有效样本、PSU 支持、标准误/自由度、缺失与分布、影响 PSU、预设 M1/M2 稳健性和 BY-FDR/Bonferroni 全家族校正。全部假设（包括不可估计项）均保留。需要独立方法学复核后才能晋级。
8. **有条件扩展**：仅在试点有效且可复现后，填写单独的[`wave1_household_environment_readiness.template.json`](templates/wave1_household_environment_readiness.template.json)，其中须包含试点成功/可复现性审核；再运行预先规定的 Wave 1 家庭环境批次（主家族 K=150；取暖条件子域 K=90 单独建族），然后按波次分别建模并核对权重/样本设计，不套用 NHANES 周期合并公式。网站仅在统计和 CHARLS 披露审查通过后增加聚合结果。

## 目前无需原始数据即可完成的工作

- 继续完善代码、元数据来源说明、网站的“候选/未分析/结果审查”状态，以及不读取个人值的验证器。
- 继续用已下载的官方问卷、Codebook、指南审阅目录字段，但不能将候选字段数、目录共现对数当成有效分析配对数。
- 不重复运行或扩大受保护目录中已完成的试点；在来源闸门开启前不把 p 值作为选择依据。
- 试点何谓“有效”以及通过后如何扩展，已写入 [`pilot_success_criteria_and_scale_up_2026-10-26.md`](pilot_success_criteria_and_scale_up_2026-10-26.md)。判断依据是来源、抽样设计、可复现性和披露审查，不以是否出现显著 p 值作为标准。

## 本次现场核验

- 2026-10-26：本地受控目录名称级清点仍只找到派生 2011 个人表、年龄候选和 PSU 候选，没有 Wave 1 全部数据、官方 Weight 或 Blood 原始包。
- 2026-10-26：新增并运行 `scripts/audit_2011_pilot_design_frame.py`。它仅在本机读取受保护的派生个人表并输出汇总计数到 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\qa_outputs`，不写出个人记录、不估计关联。预检发现本地派生框架分母尚未与官方血样指南目标人数闭合，候选年龄和权重也存在未覆盖记录；完整计数仅保存在本机受控 JSON 中。正式模型闸门保持未通过。
- 2026-10-26：预检汇总确认本地候选 PSU 映射中的所有派生个人表社区键均可匹配，但这不认证来源发行版、最终 PSU 编码或方差层。年龄候选中存在缺失值，因此后续必须基于官方 Wave 1 字段核实/重建资格与年龄域。
- 2026-10-26：为避免修改系统 Python，在 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\analysis_env` 建立了项目隔离环境，并按 `requirements-survey-audit.txt` 安装固定依赖；环境和分析数据均未进入仓库或同步目录。
- 2026-10-26：依据建表脚本的实际 import 补齐固定 `pandas` 依赖，并在受保护环境中安装；系统 Python 未被修改。
- 2026-10-26：去除 2011 试点代码中继承自旧派生表的固定行数和 PSU 数量常数，防止更完整的官方重建数据被历史数量误拒；实际分母仍须通过独立的官方源对账。
- 2026-10-26：检查发现通用 Wave 表建表脚本原先将 2011 归档路径固定为旧 RAR 文件名，无法直接使用当前 intake 清单中的全量 ZIP 和独立 PSU/Weight/Blood。已扩展 CLI 显式接收这些授权文件、记录各源文件本地 SHA-256，并保留旧路径兼容；由于官方包尚未到位，本轮不执行解压或合并。
- 2026-10-26：为避免授权数据落入系统临时目录，建表脚本现要求输入、输出及临时解包均留在 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas`；旧的同步盘路径会继续被拒绝。
- 2026-10-26：公开站点 HTTP 200；线上 app asset 为 `app.js?v=191`；CHARLS 致谢、基线指南链接及无正式关联结果提示均已出现。
- 2026-10-26：提交 `998cf4e` 的部署 #324 和 Validate #658 均成功；此处为上一版公开站点证据，与后续新增的本地入库手册/预检脚本无关。
- 2026-10-26：新增 `scripts/audit_2011_pilot_intake_metadata.py`，供官方文件到位后执行目录/哈希/Stata头部预检；脚本明确将来源凭证和抽样设计审查留作人工闸门，不把存在文件或本地哈希误当作官方认证。预检已运行；因四类输入缺失而正确保持未通过。
- 2026-10-26：入库预检现在读取受控 `intake_manifest.json`，区分官方来源人工核验、私有本地哈希状态与未到位文件；当源文件字节发生变化时会轮换来源清单ID并重置人工复核状态。合成元数据测试覆盖初次留档、变更回退、缺失输入和路径拒绝；本次实际入库仍四类文件全缺，来源与哈希状态均保持 `unavailable_pending_authorized_file`。
- 2026-10-26：已在 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\incoming_2011_official` 建立受控入库目录和来源清单模板，并运行预检；Wave 1 ZIP、PSU、Weight、Blood 四项均缺失，报告只写入受控 `qa_outputs`，release gate 保持 `not_passed`。
- 2026-10-26：入库手册和预检脚本的较早提交为 `858d658`，后续 age-domain 说明及试点清单分别在 `2252683`、`f672b76` 更新。较早记录中未核验 CI 的状态仅代表当时快照；具体工作流状态应以对应 commit 的 Actions 页面为准。
- 结论：代码演示层可继续，正式统计阶段当前为 **No-Go**。关键闸门包括获准官方源包、派生框架分母差异解释、年龄/血样资格与权重覆盖、最终 PSU/方差设计闭环；任一未闭合时不发布或扩大正式结果扫描。不尝试绕过 CHARLS 登录。
