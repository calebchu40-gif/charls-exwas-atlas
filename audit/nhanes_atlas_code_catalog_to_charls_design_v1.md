# NHANES PE Atlas 编码目录如何映射到 CHARLS

更新：2026-10-17。参考 Patel 等的[论文](https://www.nature.com/articles/s41591-026-04266-0)、官方[Phenome-Exposome Atlas](https://pe.exposomeatlas.com/)与作者的[`nhanespewas` GitHub 仓库](https://github.com/chiragjp/nhanespewas)，尤其是仓库的[`pe_catalog.Rmd`](https://github.com/chiragjp/nhanespewas/blob/main/pe_catalog.Rmd)。本项目只借用索引、选择、复现结构；字段含义和方法依据CHARLS官方逐波资料。

## NHANES端“编码对应”是什么

NHANES Atlas/`nhanespewas`将暴露和表型概念目录与NHANES原始字段名连接。GitHub教程示例从数据库的`variable_names_epcf`索引取NHANES变量/文件名，展示`e_catalog`和`p_catalog`，再用暴露字段名`evarname`、表型字段名`pvarname`以及变量对可用样本数构成后续分析的选择表。模型函数仍接收数据库里的原始NHANES变量名。该索引解决“概念目录里这个指标对应哪个调查字段/表”，不是把不同调查的数字编码一一映成同一通用数值码。

论文说明Atlas汇总的是跨NHANES调查周期得到的关联效应、标准误、P值和方差解释度；分析流程使用调查加权回归、可配置协变量、跨周期汇总/复现判断。CHARLS五轮是同一纵向队列重复访问，不能把NHANES互相独立周期的合并方法照抄为CHARLS跨波meta分析。

## CHARLS现有的对应层

本地原型的`dist/catalog.json`索引CHARLS原始变量名、波次、变量标签、模块、候选E/P角色、候选Concept ID、已审值标签及映射状态。查询可以从原始码（如`dc006_cnt`）或概念出发，显示对应波次来源。专题crosswalk补上逐题语义、选项/单位、路由、返访或代理回答属性、结构性缺失与跨波可比性提醒。每一波分别查证，不因同名、相似标签或相同整数编码就默认同义。

当前编码对应是可检索、可追溯的“官方字段—候选概念”目录，不是已经冻结的统计变量字典。正式锁定指标仍须逐项登记：测量层级（个人/家庭/社区）、目标人群和分母、有效值与特殊缺失、题目路由、子样本/权重覆盖、时间窗、单位、重复测量构造、跨波可比性以及证据文件/页码。未完成上述事项的概念保留`candidate`状态，不进入正式分析配对。

## 对当前目录规模的判断

截至2026-10-17当前全量构建有764个候选E/P Concept ID（E=490，P=283，含9个双角色）、5,004条E/P概念—字段映射；主目录有7,042条E/P字段—波次—角色—类别行和4,387条变量码—角色—类别序列。它们不等于可直接建模指标。多词回忆拆题、养老金槽位、住房成员清单和多选项必须先按构念聚合或作为组成字段；一项单波题也可保留为单波指标。NHANES的619个暴露主要包含CHARLS没有的广泛环境化学物生物监测面板，因此不能用拆分题数量追平；CHARLS的283个候选表型概念与NHANES的305个数量接近，但仍待逐项资格审查。摘要计数应另列“候选概念”“满足分析资格指标”“实际估计关联数”。

## 对 CHARLS 网站的实现约定

现阶段网站优先提供NHANES Atlas式的E/P概念目录、原始编码检索、波次筛选、官方标签和解释、条件/可比性说明，以及透明标注尚未核实的字段。正式模型尚未运行，所以关联地图/总览中所有演示效应和N必须继续标为虚构。模型阶段应先产生CHARLS自己的波次×字段配对样本流，再根据问卷和调查设计配置拟合；只有经官方使用条款/披露规则审查的汇总输出才可进入公开页面。

## 可复现入口

```powershell
python scripts/build_ep_atlas_metadata.py
```

生成主目录、概念crosswalk和网页JSON。主要产物：`audit/ep_concept_source_crosswalk_v1.csv`、`audit/charls_atlas_candidate_fields_v0.csv`、`audit/charls_atlas_candidate_series_v0.csv`、`site-prototype/dist/catalog.json`。当前数据/设计约束还应与[`nhanes_to_charls_implementation_contract_v1.md`](nhanes_to_charls_implementation_contract_v1.md)及[`survey_design_weight_review_v1.md`](survey_design_weight_review_v1.md)合并阅读。



历史快照（养老金缴费字段核对时）：候选目录为590个E/P概念（E=315、P=282、7个双角色）、4,379条E/P映射；此后社区环境字段扩展，当前数值以项目快照为准。养老金本人/单位缴费金额、工资比例和混合回答已按CHARLS代码本拆分概念。


2026-10-17继续审计后，官方2011/2013/2015/2018家户耐用品字段已分开展示所有权状态与当前估值；2018单列新增空气净化器和原始编码，边界见audit/household_asset_exposure_mapping_review_v1.md。该段为家户资产增补时的历史快照；当前目录以文首最新计数及`current_directory_snapshot_2026-10-17.md`为准。\n

2026-10-17社区问卷槽位审计：官方社区问卷明确给出13类公共设施的数量和距离、8类常用医疗设施及JF001–JF009后续问项、7类近五年灾害史。CHARLS交叉表新增84个候选概念/136条映射；社区模块当前100个概念/187条字段映射。所有这些仍是社区层单波候选，不可解释为个人暴露或仪器测量污染物。逐题定义见`community_public_facility_disaster_mapping_review_v1.md`。


### 网站主目录粒度更新（2026-10-17）

历史主目录快照曾为7,425行（E/P 6,962、C 463）；当前逐波目录为7,506行（E/P 7,042、C 464），相同代码跨波不会拼接答案标签。单位/分支构成可随原始码搜索。候选映射和目录行仍非正式统计指标。


历史快照（雇主所有制`fl016`和政府雇员身份`fl015`增补时）：候选概念745、暴露角色470、E/P波次字段映射4,856；当前总数见文首及最新快照。公务员身份仅适用于政府部门路由，所有制仅适用于企业路由；网站附各自逐波官方答案标签与来源，遵守NHANES式概念—变量—周期索引，同时保存CHARLS本地题目路由。详见 `audit/employer_ownership_type_mapping_review_2026-10-17.md`。


2026-10-17更新：网站类别分布、字段数及其非互斥限制见 `audit/candidate_concept_category_counts_v1.md`。DB021/DB029辅助工具按P类功能状态候选检索，26条映射保留原码/值标签和题组路由，专项审计见 `audit/assistive_device_phenotype_mapping_review_2026-10-17.md`。
