# CHARLS逐波模块与分析准备度矩阵（2026-10-25）

## 用途与判读

此矩阵把三件不同的事拆开：公开目录记录某波是否有某类源字段；本机准备表是否存在同名列；该字段是否已经具备目标人群、测量资格、权重和统计设计支持。前两项均不自动推出第三项。准备表核对仅读 Stata 文件头中的变量名，不读取个人答案、缺失分布、样本量或关联结果；模块级结果写在 `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\prepared_catalog_module_availability_v1.csv`，不进入仓库。可用 `scripts/audit_prepared_catalog_field_availability.py` 重现。

| 波次 | 访谈、体测与功能测量 | 实验室血液指标 | 独立/关系/社区模块 | 抽样、权重与当前分析门槛 |
|---|---|---|---|---|
| 2011 | 基线问卷、健康与功能、血压/肺功能/握力/步态等现场测量。活动题属于随机子样本，需按当波问卷和选择标记定义分母。 | 有独立基线 Blood Assays。目录含16项分析物概念；血检有专用权重，胱抑素C另有年龄分层检测机制，不能把未测者记为正常。 | 社区数据必须与个人表分开：`communityID`不是安全的一对一键；社区/子社区映射尚未闭环。关系名册保留独立分析单位。 | 基线总体为家庭居住的45岁及以上人群；应按分析目标使用个体/血检权重。现有准备表没有独立横截面旗标；communityID仅为PSU候选；官方称30个大型社区曾按子区拆分抽样，故实际PSU映射及方差层/复制权重仍需逐发行版确认。 |
| 2013 | 追访问卷和现场体测/功能测量。活动问题属于随机子样本，题项资格不能用普通个体权重缺失与否替代。该波没有血液采样。 | 无实验室血液检测；`Biomarker`是现场测量模块。 | 父母/子女等关系表仍是名册型数据，不得展开为一人多行的个人表；关系表记录不自动进入个人表。 | 官方 Wave 2 All Data、PSU、Weights 文件已来源核验；`crosssection`、`longitudinal`及模块权重已进入独立Wave 2准备表。横断面人体测量可将`Biomarker_weight`作为来源支持的权重候选；不能用于纵向/面板 biomarker 估计。样本框/年龄、字段资格、配对完整性、最终PSU/方差与独立方法审查仍阻断模型。 |
| 2015 | 追访问卷和现场体测/功能测量。活动题继续有随机子样本限制，需逐字段核验。 | 有独立 Wave 3 Blood Data 发布，列出16项实验室分析物与专用`Blood_weight`。官方 Blood、Weights、Sample_Infor文件已在受保护入库并完成来源/表头预检；Blood仍作为独立模块，尚不能与个人表同名字段等同或直接纵向合并。2011/2015同名检测需先审方法与运输流程，不能未经校准作为变化结局。 | 关系名册独立存放；家庭/社区层字段应按键和调查单位处理，不能仅因同名就合并。 | Blood_weight是横断面血检估计的来源支持候选，不是面板血检权重。样本框、年龄、血液与暴露模块连接、特殊值/顶码、最终PSU/方差和独立审查仍未通过；不拟合模型。 |
| 2018 | Wave 4访谈与认知模块按该波官方定义。Wave 4指南记载非血液生物标志物在波次1–3收集，官方Wave 4数据清单也没有单列Biomarker或Blood Data文件；HCAP是60岁及以上认知评估，不应误标为生物标志物或全龄认知量表。 | 官方 Wave 4发布资料没有列出单独实验室血检数据文件；当前目录不纳入2018检验指标。 | 关系名册和家户模块仍须保留层级；不得仅凭个人键命中推断每个模块目标一致。 | Wave 4 Weights 与 Sample_Infor来源已核验并完成表头检查；`crosssection`及横断面权重只适用于代表性主访者/配偶样本。目标年龄/抽样框、模块资格、配对完整性与最终PSU/方差仍需审查；HCAP另有年龄和评估资格约束。 |
| 2020 | Wave 5访谈和健康字段需保留疫情时期调查模式与题项变化；官方数据清单未列现场Biomarker模块，故不能从前波题项或二手描述推断本波测量存在。 | 官方 Wave 5数据清单未列单独实验室血检/生物标志物文件；当前目录不纳入2020检验指标。 | 家户、个人及关系模块的分析单位仍按发布结构区分；2021–2023常规调查未作为本项目第六波纳入，因为本项目范围限定于已核验的五个全国主波。 | Wave 5 Weights 与 Sample_Infor来源已核验并完成表头检查；`crosssection`与横断面权重只适用于官方代表性样本。2018年后较年轻刷新样本的全国代表性受官方指南限制；目标年龄域还需结合疫情调查模式、模块资格、最终PSU/方差与独立审查。 |

## 对 ExWAS 设计的直接影响

1. CHARLS公开五个全国主波为2011、2013、2015、2018和2020，并非逐年连续调查。跨波配对目录只说明官方问卷/代码本中存在候选字段，不说明每个受访者都测量、在每波都采用相同问法，或同一人群/权重适用。
2. CHARLS可支持广义的“暴露—表型”探索：生活环境与住房、职业/工作史、社会经济与家庭背景、行为习惯等候选暴露，及自报疾病、认知、心理、功能、体测和少数波次血检表型。它不等于 NHANES 中数百项环境化学物/营养生物标志物的实验室暴露组；站点应明确这是基于CHARLS现有字段的候选目录，而非宣称已有同等规模的化学暴露测定。
3. 已有逐波候选概念对数是目录层的元数据共现数。正式计算前仍要逐对确认题意、访谈对象、跳题、随机子样本、特殊缺失、模块权重、目标人群和方差估计。不得把它展示成配对分析N或显著关联。
4. 协变量字段只做检索与因果模型候选。不能把年龄、性别、城乡、收入、社区或整套C目录自动塞入每个模型；协变量集合须针对估计目标和因果图预先说明，并避免调整中介、碰撞变量或暴露自身。

## 证据来源

- CHARLS官方抽样设计说明：[Sample-CHARLS](https://charls.pku.edu.cn/en/About/Sample.htm)。
- CHARLS官方2013 Wave 2发布说明及`Weights.dta`：[Wave 2 Release Note](https://charls.pku.edu.cn/en/data/Release2013.pdf)。
- CHARLS官方2018 Wave 4用户指南：[User's Guide](https://charls.pku.edu.cn/en/data/User2018.pdf)。
- CHARLS官方2018 Wave 4文件目录：[Wave 4数据清单](https://charls.pku.edu.cn/en/Data/a2018_CHARLS_Wave_4.htm)。
- CHARLS官方2020 Wave 5用户指南与发布页：[Wave 5资料页](https://charls.charlsdata.com/pages/Data/2020-charls-wave5/zh.html)。
- CHARLS官方2015血检发布说明：[2015 Blood Data Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf)。
- 本项目的波次权重、实验室检测、年龄总体、准备表字段覆盖和源文件状态分别见[`survey_design_weight_review_v1.md`](survey_design_weight_review_v1.md)、[`blood_biomarker_definition_review_v1.md`](blood_biomarker_definition_review_v1.md)、[`wave_specific_target_population_and_age_coverage_2026-10-22.md`](wave_specific_target_population_and_age_coverage_2026-10-22.md)、[`data_preparation_plan_and_controls.md`](data_preparation_plan_and_controls.md)及[`regular_wave5_2021_2023_release_status_2026-10-24.md`](regular_wave5_2021_2023_release_status_2026-10-24.md)。

本次只汇总官方问卷/发布文档和已经完成的目录、表头审计；没有读取个人作答、估计配对样本量、运行关联模型或发布微观数据。

## 外部来源冲突记录

第三方 [NIA Biomarker Network 的 CHARLS 说明页](https://biomarker-network.isr.umich.edu/studies-with-biomarkers/charls/)称也在2018、2020采集血液样本；这与CHARLS Wave 4指南所述“血液采集于波次1和3”及官方Wave 4/Wave 5数据目录未列相应文件不一致。Wave 5指南的血样引用段落引用的是2015年血检研究，不能据此确认Wave 5有新一轮检验。本项目暂按可定位的官方公开字段/发行文件维护目录，并将该差异保留为来源核验事项；若CHARLS发布相应官方文件、变量字典及权重说明，再按新版本修订。
