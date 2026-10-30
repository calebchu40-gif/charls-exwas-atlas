# Wave 1 ExWAS 独立方法审阅要点

**用途：**供独立复杂抽样/生物统计审阅人快速判断拟议方案是否可进入受控试点。本文是审阅摘要，**不是**预分析方案批准、数据授权证明或分析结果；不得仅凭本摘要启动真实 CHARLS 模型。

## 研究问题与预登记范围

拟在 CHARLS 2011 基线血液样本中探索家庭供水、烹饪燃料与常规血液生物标志物的关联。第一批登记 105 个系数：供水 1 个预设对比、烹饪燃料 6 个类别对电力参照，各与 15 个常规血液结局配对。官方 Fieldwork Plan 附件2记录“是否空腹”1=是、2=否，且 Wave 1 Blood 表头将 `qc1_va003` 标为 “Fasting”；两者已形成来源支持的字段/编码映射。此前曾将 `qc1_va003==1` fasted-only 作为主分析候选；在核对血液权重说明后撤销这一预设主次。`bloodweight` 明确校正血检参与非应答，但已核对来源未说明是否校正 fasting-status 选择。全血样本测量条件建模和 fasted-only 条件domain是需独立比较的备选估计量，当前均未批准拟合。其余91项同样尚未获准拟合。

该 105 项批次嵌套在完整预设假设族：K=150 家庭环境主块及 K=90 供暖路由子域。若后续全部通过，计划对完整 K=240 族统一进行多重检验校正；不按显著性删减配对或决定扩展。

## 目标总体、样本框和权重候选

CHARLS 官方血液指南说明，血检目标为 17,708 名基线主受访者及配偶，实际采到 11,847 份血样；`bloodweight` 用于调整基线家户/个人未应答和未参加血检。分析中需把官方目标总体、观察到的血样设计样本、配对完整案例及年龄 domain 分开报告；上述公开人数不是任一具体模型的 N。主分析候选是在完整观察血样对象中按官方年龄下界达到45岁定义 domain；年龄上界达到45岁及完整观察血样对象为预设敏感性。配偶年龄、年龄区间及完整案例对应的估计目标仍需审阅。

来源：[CHARLS 2011–2012 Blood Data Users’ Guide，第5节](https://charls.pku.edu.cn/en/data/Blood2011.pdf)；[CHARLS 官方 Wave 1 数据页](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)。

## 复杂抽样方差候选

用户选定的工作候选为 Option A：`communityID` 聚类、未发布的 strata 不自行构造、with-replacement Taylor 线性化；输出须明确标为**近似方差**。这不恢复 CHARLS 多阶段 PPS 的全部设计、隐式分层、无放回抽样细节或大型社区拆分后的最终 PSU 映射，亦不保证标准误偏保守。CHARLS 官方论坛管理员的公开答复将设计概述为多阶段 PPS，并表示聚类层级要结合研究需要；它没有为本研究的 `communityID` 方案背书，也没有提供完整的 Wave 1 血检 `svyset` 映射。[论坛讨论](https://forum.charlsdata.com/viewtopic.php?t=22)。

请审阅人判断：该近似是否足以支持限定为探索性关联的回归推断；PSU 支持、自由度、singleton/domain 规则是否可接受；若不足，应否改为描述性分析或等待可追溯的完整设计映射。

## 结局与模型候选

- 结局以来源字段、单位及连续原量纲作为首选候选；不把指南中的 assay detection limits 当作观测剔除阈值，不因临床切点、极端分布或显著性筛除/截尾。
- Stata 表头没有结局值标签或 tagged-missing 声明；这不能排除有限数值型特殊码。须判断现有来源证据能否支持“仅排除 Stata 缺失、保留其他有限发行值”的规则；若不能，应阻断相应结局，不能猜测编码。
- Blood 指南说明右偏指标的图形省略少量极端值，但未给出可复现删值规则。原量纲为候选主尺度；对数变换仅是待审敏感性候选，必须先通过独立的有效值/正值规则，且不得改变主分析样本来满足变换条件。
- 混杂控制候选包括年龄、性别、教育和社区城乡背景；须审阅其对具体供水/燃料对比的因果角色、字段编码、社区变量含义及完整案例选择。社会经济、行为、BMI、既往诊断和治疗变量不得自动塞入通用模型；需要预先说明其混杂身份，并排除暴露后中介/碰撞变量。
- 精确协变量集合、函数形式、缺失数据/完整案例估计量、效应尺度、敏感性规格及单对可估性标准均需在哈希绑定配置中冻结。

## 需要独立审阅人给出的决定

1. 明确的目标总体、观察样本、`bloodweight` 适用性及45岁 domain 是否相互一致。
2. Option A 的近似方差、聚类层级、自由度及 singleton/domain 处理是否足以支持所述推断；若不通过，指定描述性退路或所需的官方设计资料。
3. 15项结局的有效值/特殊码/变换规则；审阅已来源核实的 `qc1_va003` 1=Yes/2=No 映射、血液权重是否支持 fasting domain、全样本测量条件建模与fasted-only条件估计的目标总体及方差实现。
4. 暴露编码、混杂变量/DAG、缺失和完整案例估计量、模型规格、敏感性及多重检验家族是否适当。
5. 真实数据分析前 readiness 是否通过；对每一项给出 **pass / revise / block**、依据、审阅人身份、日期和所审草案哈希。

独立审阅的具体证据、完整源与配置哈希以及签署记录留在服务器私有 `analysis_review/`。任何一项仍为 revise/block 时，不得启动 CHARLS 真实关联。软件或合成数据运行不算 CHARLS 科学试点。

## 数据使用和发布边界

CHARLS 条款限定学术用途，禁止公开原始微观数据或向他人转交；网站只可接收通过分析审阅及披露审查的聚合结果。不得公开个体记录、精确受限 QA、可识别地理/社区键或能够反推个体的单元格。[CHARLS 官方数据访问条款](https://opendata.pku.edu.cn/file.xhtml?datasetVersionId=97&fileId=138)。


## New fasting-domain weight question (2026-10-30)

The source-supported fasting code does not establish a valid fasting-domain weight. The CHARLS Blood Users’ Guide describes `bloodweight` as correcting household/individual nonresponse and nonparticipation in blood collection, but does not document an additional fasting-response adjustment. Compare a full blood-respondent estimand with fasting status as a measurement-condition covariate (and a separately frozen interaction only if justified) against a conditional fasted-domain estimand; do not treat `bloodweight` as correcting fasted selection absent authoritative evidence. A fasting domain must also be implemented within the full design for variance estimation, but that does not fix selection-weight validity. Detailed issue and primary references: [`wave1_fasting_estimand_weight_compatibility_2026-10-30.md`](wave1_fasting_estimand_weight_compatibility_2026-10-30.md).

## Cluster support diagnostics for the pilot contrasts (2026-10-31)

A protected, source-bound availability audit now summarizes communityID support separately for each contrast arm and provisional age domain, including communities with both arms and single-record clusters. The private aggregate results show that some infrequent cooking-fuel exposure categories have materially thinner community support than the reference arm. Exact pair/domain counts remain in the owner-only review packet and are not published here.

This is not a fitted-model result, final analytic N, or an automatic exclusion rule. The independent reviewer should determine whether the community-cluster WR Taylor approximation supports inference for these contrasts, whether a predeclared minimum-support rule is justified, and how any pair that fails that rule should be recorded in the full registered family. Do not collapse exposure categories or select pairs after inspecting association results. No cluster-count threshold is currently frozen.
