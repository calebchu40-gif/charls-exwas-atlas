# NHANES PE Atlas 网站目录与 CHARLS 编码映射审阅 v1

日期：2026-10-16  
目的：按用户要求直接对照 [Phenome-Exposome Atlas](https://pe.exposomeatlas.com/) 和 [nhanespewas GitHub](https://github.com/chiragjp/nhanespewas)，把网站展示的字段编码、类别和查询结构迁移到 CHARLS 的变量目录。

## 现场核对到的 NHANES 网站结构

首页与导航提供 About、Browse by Phenotype、Browse by Exposure、Browse by Exposure Group、E Catalog、P Catalog。E Catalog 与 P Catalog 是可搜索/筛选的数据表，页面主要列**变量 ID、类别、描述**；当前网站分别显示619条暴露与305条表型。单个表型页提供多个图形（按暴露组的 `−log(P)`、效应量、R²、`−log(P)` 对效应、地理视图、规格偏倚）和 Summary Statistics；示例结果字段为表型/暴露描述、效应大小、R²、`−log(P)`、显著性标签、总样本量、覆盖调查数和 UWLS I²，还会列相似表型。

网站首页与当前仓库的计数不是一一一致：本地固定提交里的 `select/select_expo_variables_3.csv` 有4,057条周期/文件源记录、929个不同变量代码；`select/select_pheno_variables_3.csv` 有1,591条周期/文件源记录、365个不同代码，而线上 E/P Catalog 显示619/305条。可见源清单包含周期版本及更广的变量备选，网站最终目录另有筛选。**因此不能把仓库CSV的行数、独立代码数直接说成网站分析指标数。**本项目也要分别报告源字段、候选代码系列、冻结概念、实际检验数。

GitHub 目录字段包括 `Variable.Name`、`Variable.Description`、`Data.File.Name`、`Data.File.Description`、`Begin.Year`、`EndYear`、`Component`、`Use.Constraints`、`epcf`、`varname`、`category`、`subcategory`。其中 `epcf` 区分 `e` 暴露、`p` 表型、`c` 调整/控制候选。NHANES 暴露大类包括 nutrients、pollutant、infection、smoking、physical activity、allergy、housing、income、autoantibody；细类包括 dietary interview/biomarker、heavy metals、VOC、phthalates、pesticide 等。表型大类包括 anthropometric、biochemistry、blood、blood pressure、lung、fitness、aging、disease 等。

## CHARLS 对应的编码和目录设计

### 本轮按代码目录方式补入住房字段（2026-10-16）

住房映射已按 `wave + CHARLS source code` 接入主 E/P 目录：当前437条逐波映射、419个不同源码名、26个候选概念，包含住宅设施条件及2018家庭住房资产槽位。可通过变量编码或英文题项标签检索；行中保留源字段标签、波次、模块、候选概念和待审说明。2018 `ha004_w4_1_1_` 在官方代码本标为 House[1] 总价值，`ha004_w4_2_1_` 为 House[1] 单位价值；`ha004_w4_1_` 是价值类型选择字段，不能与金额字段混为一项。`min/max bracket` 端点是区间元数据，已从候选指标映射排除。

此前的7,326/4,610及922波次字段标签数为历史快照。当前动态值见`audit/ep_concept_mapping_coverage_v1.md`：全角色目录7,280条字段—类别行；其中E/P为6,796行、4,214条去重记录，C类为484行、315条记录。E侧257/P侧255，共505个E/P候选概念；3,879条E/P概念映射全部匹配，另有7条C类映射。主目录覆盖1,274个已审值标签/语义波次—字段码。字段行/家庭槽位仍不等于独立指标数；所有编码只在相应CHARLS波次代码本语境下解释，标签覆盖也不代表已harmonize或可以用于模型。

CHARLS 需保留原始变量码与官方标签，如 `da049`（夜间睡眠时长）、`i022`（主要烹饪燃料）、`qi002`（实测身高）或 `newglu`（2011血糖）。同一概念跨波字段名可能变化，必须以概念ID连接并保留每个波次原码；同一码也可能不同波次改问法、路由或含义，不能仅因编码相同就判为可比。

已新增自动候选目录 `charls_atlas_candidate_fields_v0.csv` 和按代码/标签汇总的 `charls_atlas_candidate_series_v0.csv`，采用 NHANES 的 `epcf` 角色以及 ID/Category/Description 结构，并增补 Source Wave、Source Archive、审校状态和 harmonization 状态。角色初筛类别包括：

| E/P | CHARLS 候选类别 | 典型字段域 | 解释边界 |
|---|---|---|---|
| E | Behavior | 吸烟、饮酒、饮食/食物、身体活动、睡眠 | 需核题目、频率/时长定义和随机模块资格 |
| E | Built environment | 住所、用水、厕所、燃料、厨房、建筑特征 | 作为家庭环境代理，不等于个体污染剂量 |
| E | Community context | 社区环境、基础设施与服务 | 社区文件层级和跨波可得性要单独处理 |
| E | Social determinants | 教育/社会位置、收入/财富、工作退休、社会关系/照护 | 很多是混杂因素或中介；不能一律当作外部暴露或全部调入模型 |
| E/P | Internal biomarker | 血液及体测指标 | 双重角色仅表示可做方向探索；须按估计目标指定，不允许把同一指标自相关 |
| P | Anthropometric / blood pressure / biochemistry | 身体测量、血压、血检 | 体测和血检波次/子样本覆盖不全，单位与专用权重需核验 |
| P | Chronic disease / health and symptoms | 诊断、功能、症状、自评健康 | 慢病问卷跳题与疾病状态延续需派生；结构性空白不能编码为“否” |
| P | Cognition / mental health / physical function | 认知、情绪、ADL/IADL、力量/活动能力 | 量表构成、得分方向和题目跨波可比性须核验 |

## 初筛目录计数：仅作发现，不代表最终指标数

初版关键词扫描得到11,718条波次级匹配记录，明显受家庭成员矩阵、住房所有权格子和测量未完成原因膨胀。第二轮排除了 `Family_Information` / `Family_Transfer` 自动候选、家庭成员槽位、测量未完成字段，并把建成环境模块收窄到 `Housing_Characteristics` 后，当前目录为：4,929条波次级源字段—角色记录、3,080条编码—类别候选记录。角色分项（编码—类别记录）：e=1,900，p=837，e,p=30，c=313。E/P 共1,930条，但其中仍包括大量就业/收入/慢病诊断题的分支、历史、追问和细分字段；同一实质概念会对应多条源编码。因此这依然不是最终 ExWAS 指标数，也不能与线上 NHANES 网站的619/305直接比。

筛选脚本为 `../scripts/build_charls_atlas_catalog.py`；生成文件为 `charls_atlas_candidate_fields_v0.csv`（保留波次和来源）、`charls_atlas_candidate_series_v0.csv/json`（汇总显示）和 `charls_atlas_candidate_domain_counts_v0.csv`。候选目录现在供本地原型检索。所有字段仅来自变量目录元数据，不读取微观记录。自动筛选有意把家庭成员/转移矩阵暂列为“待派生研究”，不代表相关领域不能作为暴露；例如需要先定义家庭层级汇总量，再按官方问卷和样本设计另行审计。

宽筛最可能扩展当前核心目录的方向是社会经济和家庭环境、认知/功能/症状，而不是凭空新增生化污染物：CHARLS 血检主要集中在部分波次；2011有基线血检，2015独立 Blood Data 是否可用需按实际获批文件/本地源档确认。后续要将源字段候选逐层收敛为：真实测量/题项 → 非ID/非路由 → 合法编码 → 适用人群 → 可跨波映射的概念 → 有适当样本设计信息的可建模指标。每层都保留排除原因和证据。

## 网站映射和 CHARLS 必须改写的结果字段

- **保留** NHANES 的导航结构：按表型浏览、按暴露浏览、按类别浏览、E Catalog、P Catalog。CHARLS 的 E/P Catalog 显示原始码、官方标签、类别/细类、波次、模块和核验状态。
- **增加** CHARLS 来源和可比性：波次原码、概念ID、问卷/测量来源、单位/值域、路由/样本资格、缺失类型、权重/PSU/方差设计、目标样本、模型规格、FDR家族和数据版本。
- **不照搬** 线上结果页的跨NHANES调查数和UWLS I²字段作为 CHARLS “重复性/异质性”。CHARLS波次复访同一受访者，波次结果相关；先展示逐波结果和兼容性，需独立设计纵向/重复测量汇总方法。
- **首阶段网站** 可用当前候选目录和合成结果验证 E/P 搜索与分类交互；真实汇总结果待分析、披露与许可审查后接入。CHARLS 微观数据不进入网站。

### 复现来源

- [Phenome-Exposome Atlas 在线图谱](https://pe.exposomeatlas.com/)
- [nhanespewas 仓库](https://github.com/chiragjp/nhanespewas)，本地固定版本审阅记录见 `nhanespewas_github_method_review_v1.md`
- 仓库目录文件：`select/select_expo_variables_3.csv`、`select/select_pheno_variables_3.csv`、`select/variable_domains_ep_2.csv`


## 本轮修订和下一步概念收敛

前端原型已依照 NHANES 的入口结构提供按表型浏览、按暴露浏览、按暴露组浏览、E Catalog、P Catalog；表格用源编码、官方变量标签、类别、波次和来源模块展示，并可检索。关联页仍明确使用虚构记录。当前 E/P 目录是“编码候选层”，后续要新增并审核“概念字典层”：把别名/重复波次码并到稳定概念ID，明确测量/问句、响应类型、单位、值域、结构性缺失、样本资格、所需权重/PSU/方差方法、波次可比性，再决定是否成为统计检验的一项。

对 CHARLS 的扩展不应以匹配 NHANES 数字为目标。NHANES 暴露包含大量实验室化学物和污染物测量；CHARLS 的强项更偏向中老年队列的行为、社会经济、家庭/社区环境、认知、功能和疾病结局。实验室与体测虽然重要，但波次/子样本不齐。目录分组可以借鉴 NHANES 的命名和 `epcf` 概念；字段、类别、统计指标和跨波汇总必须按 CHARLS 问卷、数据发布与调查设计重新定义。


## Official-data access and current candidate counts (2026-10-16)

The CHARLS official 2015 release page lists Blood Data as a public release attachment; the official announcement says it is available after account registration/sign-in. The 2015 release note reports 13,420 blood responses among 21,100 wave-3 interviews, and 13,013 among the 20,284-person cross-sectional sample. The project has the official release note but not the separate person-level Blood Data file. This is an access/account step, not evidence that the file has not been released. Links: `https://charls.pku.edu.cn/en/Data/a2015_CHARLS_Wave_3.htm`, `https://charls.pku.edu.cn/en/data/Blood2015.pdf`, `https://charls.pku.edu.cn/info/1010/1012.htm`.

The current broad source-field catalog has 6,205 field-role-category rows and 3,880 deduplicated wave-code/category records; E=2,689 and P=974, with dual-role records overlapping. It now includes all 16 blood assay concepts in 2011/2015 and the audited objective measurement components. The 851 rows with reviewed categorical labels/response semantics span 805 wave-field codes; continuous measures are separately described by units/measurement metadata and are not counted as missing categorical labels. These remain source-field candidates, not frozen independent indicators. See `audit/charls_catalog_count_interpretation_v0.md` and the refreshed `site-prototype/dist/catalog.json`.

CHARLS has codebook-to-variable mappings analogous to the NHANES catalog pattern, but they must be built from CHARLS codebooks, release notes, questionnaires, and measurement crosswalks. The project preserves wave-specific codes, labels, units, sources, routing/sample caveats, and concept crosswalks; NHANES variable codes or response values are never reused as CHARLS codes.


## 新增的功能表型编码检索（2026-10-16）

健康相关工作/家务受限页新增4个候选概念、8条波次字段映射。2015细分题含条件跳转，2018/2020使用不同三级等级文本；网页按CHARLS原码和值标签展示，不把结构性缺失当“否”，不将健康限制解释为失业或家务参与。细节见`health_work_limitation_mapping_review_v1.md`。
