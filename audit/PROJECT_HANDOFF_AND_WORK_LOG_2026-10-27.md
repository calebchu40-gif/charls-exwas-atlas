# CHARLS ExWAS Atlas 项目总记录与交接说明

**记录日期：2026-10-27**  
**内容核对基线：`d0c16f4`；本记录随后随独立提交入库**  
**公开网站：<https://calebchu40-gif.github.io/charls-exwas-atlas/>**  
**代码仓库：<https://github.com/calebchu40-gif/charls-exwas-atlas>**

这份记录汇总研究目标、已完成工作、真实分析为何仍未正式放行、数据申请及入库方法和接下来的执行顺序。它只记录方法与项目状态，不包含 CHARLS 个体记录、受限分析输出、个人账号资料、服务器登录信息或私有文件哈希。

## 1. 项目目标和总体设计

构建一个面向 CHARLS 的 ExWAS（暴露—表型关联）目录与交互网站，并在官方数据许可和研究设计允许的前提下，逐波运行可复现的暴露—表型关联分析。网站要清楚区分：

1. **候选目录**：来自问卷、代码本、用户指南和波次字段交叉表的可检索概念；
2. **已分析结果**：实际按冻结方案拟合的波次特定关联；
3. **方法审查通过结果**：来源、目标总体、抽样设计、权重、方差、估计和敏感性检查均完成复核；
4. **公开结果**：通过 CHARLS 许可/披露复核、且只含允许公开的聚合结果。

目录中某字段的存在、两个字段同时出现或代码可以运行，都不代表该假设已经进入正式模型。关联是观察性、按波次定义的估计；不把相关性表述为因果效应。CHARLS 的随访包含重复受访者，所以不照搬 NHANES 独立调查周期的汇总公式。

## 2. 为什么“正式关联模型”目前仍为 0

此前在受保护本机运行过 2011 年水源/烹饪燃料 × 15 项血液表型的 **105 项探索性系数试点**，并有 M1/M2 模型输出。它说明软件分析链曾经跑通，但并没有被认定为正式、可发表或可公开的 CHARLS 发现。因此网站的正式/审查通过关联模型数仍为 **0**。试点估计、p/q 值、逐对样本支持及私有 QA 文件都留在受保护目录，不应用来筛变量或选题。

未闭合的关键问题包括：

- 目前入库的派生文件未能由完整的官方 Wave 1 All Data、PSU、Weight、Blood 原始发行包重新认证和重建；
- 官方 bloodweight 的适用总体与 45 岁以上分析域需要按血样资格、主受访者/配偶关系和完整设计框架核对；年龄域应在适当的设计框架内定义，不能先删掉可能属于血样设计框架的配偶；
- 官方抽样资料称 30 个大型社区曾拆分为子区域形成抽样 PSU，需确认受访者 `communityID` 与最终方差 PSU 的映射；
- 已查阅的公开指南没有给出可直接采用的方差层或复制权重定义。不能用省、市、城乡、地区或 `areatype` 自行拼造方差层；如官方发行版没有必要设计字段，必须另行形成有依据、有限定的方差方法并经调查统计方法复核；
- 年龄来源、样本分母、各模块适用对象、缺失和结构性跳题，以及主要协变量集仍需用精确发行版资料定版。

所以，“模型数为 0”表示没有结果完成正式审查并可进入网站结果层，不表示从未进行过试点模型。将探索性结果计为正式发现会掩盖尚未解决的来源与设计问题。

## 3. 已完成的工作

### 3.1 研究与参考实现

- 阅读并记录 NHANES Phenome–Exposome Atlas 文章、补充材料及公开 GitHub 实现中的成对关联、变量映射、模型、结果和多重检验思路。
- 将可借鉴的目录、数据字典、全家族多重校正、结果筛选与可复现记录思路用于 CHARLS 项目；没有把 NHANES 的独立调查周期合并方法直接套到 CHARLS。
- 形成 CHARLS 按波次估计、按样本/问卷路由定义目标总体、保留全部预先声明假设的分析框架。

### 3.2 CHARLS 候选目录和网站

- 建立常规 2011、2013、2015、2018、2020 波次的暴露、表型及协变量候选元数据，并为候选概念追踪波次字段、测量单位、问卷路由、来源和审查状态。
- 另整理 2014 Life History 元数据；其回顾性生命史字段不等于常规随访波次暴露或结局。
- 核对和修订了多轮官方问卷/代码本中的家庭环境、住房、迁移、健康、劳动、收入和养老金字段标签、路由及波次差异；制作部分协变量/DAG 审查和结构化交叉表。
- 网站已公开部署，提供候选目录、筛选/查询、波次与变量类别浏览及方法说明。网站首页在本记录创建时返回 HTTP 200；关联结果 JSON 返回 HTTP 404，符合当前没有批准结果文件的状态。
- 目录数量是元数据快照，含去重概念、角色和字段映射等不同计数，不能解释为实际可估计变量数、样本量或结果数。以 README 和相应交叉表的计数定义为准。

### 3.3 方法审查和受保护分析流程

- 记录 Wave 1 用户指南、Blood User Guide、抽样和权重资料及 Wave 2 权重、Wave 3 血液子样本的来源核对要点。
- 已有仅检查来源/哈希/压缩包清单/文件头的 metadata-only 入库程序；它不解压 All Data 包、不读取受访者答案，也不自动证明官方来源身份。
- Wave 1 重建、权重/PSU/血液表键核查、分析资格和运行前门禁已有脚本/模板。真实关联运行器要求受保护的来源、方案、变量和设计准备记录通过，并只在受控本机存放个体数据和中间输出。
- 对血液表型的有效值和测量尺度开展审查；已将 Wave 1 表型标准化参考尺度设计为在冻结分析域内统一估算，使后续暴露模型可比较，同时保留原始量纲估计。有效值、单位、检出限/特殊码仍须依官方版本逐项核实。
- 明确阶段性 K=105/K=150/K=90 校正不能替代最终全图谱主检验族的 BY/Bonferroni。最近新增受保护的最终化工具，要求完整冻结的 primary hypothesis ID 清单、单一 primary model、所有合格分批结果，以及 SHA-256 绑定到清单的独立 scope-review 记录；缺项、多项、重复或未解决状态会停止。该工具本身不审查研究范围是否科学完整，也没有用真实 CHARLS 结果运行。
- 结果发布构建器要求完整家族和逐项披露决定绑定到精确结果文件；只允许经过审查的聚合字段进入公开站点。

### 3.4 版本与记录

- 项目代码和安全可公开的文档变更持续推送到个人 GitHub 仓库；最近提交为 `d0c16f4`（全局主族最终化要求独立范围审查记录）。
- 适合公开的代码/文档副本另行放在个人服务器项目目录；服务器只同步过代码、方法文档和空白模板，不放 CHARLS 个体数据或限制性结果。服务器地址/登录别名不写入本交接文档。
- `logs/progress_log.md` 记录逐次进展；该进度日志被 Git 忽略，不会随公开仓库提交。具体方法审计和执行记录列于下文“关键文件”。

## 4. 当前状态（2026-10-27 核验）

| 项目 | 状态 | 说明 |
|---|---|---|
| Wave 1 All Data | 缺失 | metadata gate：`missing_or_ambiguous` |
| Wave 1 PSU | 缺失/未通过来源审核 | metadata gate：`missing_or_ambiguous`；旧目录中的单个文件不能替代精确官方入库包 |
| Wave 1 Weight | 缺失 | metadata gate：`missing_or_ambiguous` |
| Wave 1 Blood | 缺失 | metadata gate：`missing_or_ambiguous` |
| Wave 2（2013）Weights.dta | 缺失 | 受保护预检：`skipped_missing_input` |
| Wave 3（2015）Blood Data | 缺失 | 受保护预检：`skipped_missing_input` |
| 正式/方法审查通过关联模型 | 0 | 既有 105 项只为探索性试点，不是正式结果 |
| 网站首页 | 可访问 | HTTP 200 |
| 公开关联结果 JSON | 不存在 | HTTP 404；当前没有批准公开的结果 |
| Git 工作区 | 干净 | `main` 与 `origin/main` 对齐到 `d0c16f4` |
| 最近提交的 CI | 未确认 | 历史上部分提交 CI 成功；不要把旧提交的绿灯当作 `d0c16f4` 的验证 |

Wave 1 和可用波次的元数据门禁脚本在每次接收新文件时应重跑。当前状态只反映最近一次核验，不应在文件下载后继续引用为当前状态。

## 5. 官方申请与文件入库

CHARLS 官方 FAQ 说明：用户需在官方网站注册、签署数据使用协议、提供真实信息并验证邮箱；公开发布的数据集需分别申请，FAQ 给出的通常审核时间为 3 个工作日。申请需由用户本人以自己的获准账号完成。数据使用条件应以申请时的协议和各发布包的说明为准。

### Wave 1（当前第一优先级）

从官方 [Wave 1 页面](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)分别申请：

1. [All Data，文档 123](https://charls.charlsdata.com/documents/123/download/en.html)
2. [PSU，文档 117](https://charls.charlsdata.com/documents/117/download/en.html)
3. [Weight，文档 118](https://charls.charlsdata.com/documents/118/download/en.html)
4. [Blood Data，文档 201](https://charls.charlsdata.com/documents/201/download/en.html)

将原始下载包/文件放入本机非同步的 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\incoming_2011_official`。保留原始文件名和下载来源；不要把个体数据复制到 OneDrive、GitHub、协作者压缩包、公共服务器或网站。不要把密码、验证码或个人身份资料提供给项目日志。

初次到位时，先从项目根目录运行：

```powershell
python scripts/audit_2011_pilot_intake_metadata.py
```

这一步只做 metadata-only 预检。来源/文件标题/发行版与角色审核通过后，再按受控 README 指引重建 Wave 1；不能跳过样本框、年龄域、权重和 PSU/方差设计审查后直接拟合模型。

### 后续波次

可并行申请后续公开波次，之后按波次分别审核。当前已有独立预检入口：2013 Wave 2 `Weights.dta`；2015 Wave 3 Blood Data 与 `.dta`。对于 2015，优先声明可由官方横断面血检权重支持的估计总体；不要把横断面 Blood_weight 直接当面板权重。2018/2020 等波次也需按各自用户指南、字段、权重、PSU/方差、测量协议和目标人群做独立准备。

**无需等所有波次都下载完才能开始：**Wave 1 四项到齐并通过门禁后即可先推进基线；后续波次按序增加。数据申请通过不等于所有变量、估计目标或抽样方差问题自动解决。

## 6. 文件到位后的固定顺序

1. **只做元数据预检**：核对文件名、来源页、版本/官方校验和（若有）、压缩包清单和 Stata header。初检不读取个人回答。
2. **来源身份审核**：用户本人下载的文件逐项与官方文档/版本匹配；本地 SHA-256 仅记录字节身份，不冒充 CHARLS 官方校验值。受保护 manifest 中记录人工审核证据。
3. **重建 Wave 1**：从经过确认的 All Data、PSU、Weight、Blood 源表重建，不把旧派生表当权威输入；个体数据只在授权本机受控目录处理。
4. **样本框与资格**：分清个人、家庭、主受访者/配偶、血样目标/响应样本和各问卷路由；明确 45+ 年龄域与血样权重支持的 estimand；核对各分母、结构性缺失和连接覆盖。
5. **权重、PSU 与方差**：确认具体权重字段和适用样本；核实 PSU 对拆分社区的映射；查找官方 variance strata/replicate weights 或形成经独立方法复核的限制性近似。不得推造分层变量。
6. **冻结模型和复核 105 项试点**：冻结主要模型、协变量因果角色、量纲、有效值/缺失规则、估计域、假设家族、诊断阈值、软件/代码版本。检查复现、收敛、有效样本支持、PSU 支持、权重和影响点。成功标准是设计与估计有效、可复现，不是 p 值显著。
7. **通过独立方法审查后扩展**：按预先登记范围运行 K=150 住宅/家庭环境主块及 K=90 的 `i020=No` 供暖路由子域；明确 K=90 是特定路由人群估计，不代表全体。K=105/K=150/K=90 的批次校正只能用于内部诊断。
8. **逐波追加**：2013、2015、2018、2020 分别完成来源、变量、样本框、测量、权重、PSU/方差和估计目标审核；不把重复个体当独立调查周期，也不默认跨波测量可比。
9. **全图谱多重校正**：冻结完整 primary hypothesis universe 后，对全部波次/批次的唯一主模型一次性做 atlas-wide BY/Bonferroni；保留不可估计的预声明假设。M0/M2 不暗中变成额外 primary discoveries。
10. **披露审查与网站发布**：对精确结果文件逐项完成披露决定，整族发布；只生成 allowlisted 聚合 JSON。复核网页内容和结果筛选后再发布。原始数据、个体记录、行级 QA、私有哈希、文件路径和受限诊断都不公开。

## 7. 关键文件导航

- 项目首页和总状态：[README.md](../README.md)
- 逐次日志：[logs/progress_log.md](../logs/progress_log.md)
- 当前执行路线：[pilot_followup_execution_plan_2026-10-26.md](pilot_followup_execution_plan_2026-10-26.md)
- 自主执行/Go-No-Go：[pilot_autonomous_execution_decision_2026-10-27.md](pilot_autonomous_execution_decision_2026-10-27.md)
- 试点方案和来源/设计门：[pilot_2011_water_biomarker_plan_and_gates_2026-10-26.md](pilot_2011_water_biomarker_plan_and_gates_2026-10-26.md)
- 105 项门控执行记录：[execution_checkpoint_2026-10-27.md](execution_checkpoint_2026-10-27.md)
- 多重检验与主模型：[multiplicity_primary_family_reconciliation_2026-10-27.md](multiplicity_primary_family_reconciliation_2026-10-27.md)
- 数据清理/准备控制：[data_preparation_plan_and_controls.md](data_preparation_plan_and_controls.md)
- 数据许可审阅：[charls_data_access_license_review_2026-10-24.md](charls_data_access_license_review_2026-10-24.md)
- 公开结果合同：[public_association_release_contract_v1.md](public_association_release_contract_v1.md)
- 最终化工具：[../scripts/finalize_atlas_primary_family.py](../scripts/finalize_atlas_primary_family.py)
- 波次/表型/候选目录：查阅仓库 `sources_official/`、`audit/` 以及 `site-prototype/dist/` 下的公开元数据；这些文件不是 CHARLS 个体数据。

## 8. 当前下一动作

唯一需要用户本人完成的外部操作是：在 CHARLS 授权账户中申请并下载 Wave 1 四项官方文件，放到前述本机受控 intake 文件夹。文件到位后，不用重新讨论已定顺序；先跑 metadata-only 预检，然后依次推进来源身份、Wave 1 重建、目标/权重/PSU/方差门和冻结 105 项复核。

在上述门槛通过前，不运行或发布新的正式关联结果；不以候选目录配对数当样本量，不用显著性挑选配对，不将合成/软件校验称作科学试点有效。项目目标仍是完成逐波 ExWAS 分析与公开交互平台，不因当前数据缺失而缩小目标。
