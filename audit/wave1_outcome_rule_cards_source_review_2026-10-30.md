# Wave 1 血液结局逐项来源规则卡（供冻结与方法审阅）

**日期：**2026-10-30  
**状态：**来源核对与候选规则；未获独立审阅，不是有效值批准，也不开放关联模型。  
**范围：**用户预设 pilot105 / K150 / K90 中的 15 项 Wave 1 常规血液指标。未读取任何受访者化验取值。

## 来源核对结论

1. CHARLS 2011 Blood Users' Guide 的采血说明（印刷页4）写明调查要求过夜空腹，但非空腹样本仍会采集且空腹状态会记录；同一指南提示非空腹样本的血糖可能偏高。Guide/Codebook 本身没有给出 `qc1_va003` 数值码，但新增来源链已补齐映射：受控 Wave 1 Blood header 将 `qc1_va003` 标注为 “Fasting”，官方 2011 Fieldwork Plan 附件2把“是否空腹”编码为1=是、2=否。该映射经来源核对，不是 Wave 3 编码迁移。fasting-only 主分析候选尚未独立批准。
2. 指南表1（印刷页6）把化学分析的数值列为**assay detection limits**；它不是个体观测的有效范围、排除阈值、截尾规则或临床诊断界值。指南第6节（印刷页12–13）还说明部分密度图省略了少数极端观测，但没有列出观测、算法或可复现删值规则。故不得把表1范围当作筛除上下限，也不得凭样本分位数删值/winsorize。
3. Wave 1 Blood 文件头信息与已审核资料未提供这些指标的附属值标签/可执行有限特殊值映射。Stata 扩展缺失须继续按缺失处理；表头中缺少标签不等于证明不存在有限数值型特殊码。仅凭 assay 范围、观察分布或常用临床阈值不能批准一个有限值域。
4. 指南说明胱抑素 C 采取年龄分层子样本检测（70岁及以上全测、较年轻者随机抽取；印刷页12），而可用资料未证明当前 `bloodweight` 同时校正该检测子抽样。因此 blood_cystatin_c 不纳入这 15 项全样本假设族。该决定与登记簿一致；15 项不是把所有可见生物指标无条件全纳入。

### Wave 1 Stata 表头元数据核对（2026-10-30）

受保护服务器上的 metadata-only 报告已按精确来源字段与15项结局登记表对齐。计划结局字段均为连续数值型，表头未声明 value-label set 或 Stata tagged-missing 代码；这只描述文件元数据，**不能排除有限数值型特殊码**，不能据此确认有效值域。`qc1_va003` 同样没有表头值标签；其数值映射另由官方 Fieldwork Plan 附件2与字段标签共同支持为1=是、2=否。此核对未读取受访者取值，不改变任何结局规则的 `candidate_not_frozen` 状态，也不开放关联模型。

## 逐项来源映射和候选处理

| 结局概念 | Wave 1 字段 | 单位 | 官方方法/测量信息 | 当前候选规则与待审事项 |
|---|---|---|---|---|
| 白细胞计数 | `qc1_vb002` | 1000 cells/μL | CBC；县/乡镇检测点自动分析仪 | 保留官方单位；先核实特殊缺失码。指南未提供该 CBC 字段的逐项有效范围/截尾规则，不设人为上下限。 |
| 血红蛋白 | `qc1_vb004` | g/dL | CBC；县/乡镇检测点自动分析仪 | 同上；临床贫血切点不作为连续结局筛选阈值。 |
| 红细胞压积 | `qc1_vb005` | % | CBC；县/乡镇检测点自动分析仪 | 同上；不因偏离常用参考区间自动删除。 |
| 平均红细胞体积 | `qc1_vb006` | fL | CBC；县/乡镇检测点自动分析仪 | 同上；不设未由来源支持的上下限。 |
| 血小板计数 | `qc1_vb009` | 10^9/L | CBC；县/乡镇检测点自动分析仪 | 同上；不据临床阈值二分或筛样。 |
| 总胆固醇 | `newcho` | mg/dL | 酶比色法；表1报告 assay detection range 3–800 mg/dL | 检测范围不得直接用于筛值；保留连续原单位候选，是否限制空腹/是否变换待审。 |
| HDL-C | `newhdl` | mg/dL | 酶比色法；表1报告 assay detection range 3–120 mg/dL | 检测范围不是有效值边界；保留连续候选，不按 HDL 临床风险切点筛值。 |
| LDL-C | `newldl` | mg/dL | 酶比色法；表1报告 assay detection range 3–400 mg/dL | 检测范围不是有效值边界；保留连续候选。该字段为直接测定，仍需审核测量及非空腹解释。 |
| 甘油三酯 | `newtg` | mg/dL | 酶比色法；表1报告 assay detection range 4–1000 mg/dL | 7项关联的空腹字段/编码已由官方来源支持；fasting-only估计目标、权重适用性及有效值规则仍待审阅，因此继续阻断。一般非空腹血脂共识不足以替代研究估计目标审查。不得把检测范围作顶码或排除阈值。 |
| 葡萄糖 | `newglu` | mg/dL | 酶比色法；表1报告 assay detection range 2–450 mg/dL；指南提示非空腹值可能偏高 | 七项关联的 `qc1_va003` 映射已有官方证据（1=空腹、2=非空腹）；但估计目标、权重适用性、有效值规则及独立审阅未完成，故仍不可估。不按字段频数反推规则。 |
| 糖化血红蛋白 | `newhba1c` | % | 硼酸亲和 HPLC；表1报告 assay detection range 0–40%；指南讨论运输/冻存可能影响结果 | 不用临床风险切点二分；测量处理局限需披露，变换与敏感性待审；不从 Wave 3 导入规则。 |
| 高敏 C 反应蛋白 | `newcrp` | mg/L | 免疫比浊法；表1报告 assay detection range 0.1–20 mg/L | 不把检测范围作有效值上下限；右偏及变换方式需在看关联结果前冻结。 |
| 血尿素氮 | `newbun` | mg/dL | 尿素酶酶促紫外法；表1报告 assay detection range 5–100 mg/dL | 不把检测范围作有效值上下限；变换方式待审。 |
| 肌酐 | `newcrea` | mg/dL | 补偿 Jaffe 法；表1报告 assay detection range 0.1–25 mg/dL | 不把检测范围作有效值上下限；不自行作 eGFR 推导替代本结局。 |
| 尿酸 | `newua` | mg/dL | UA Plus 法；表1报告 assay detection limit up to 20 mg/dL | “up to”检测限不作为硬有效上限；保留连续结局候选，变换方式待审。 |

字段、单位和概念映射与本仓库 `blood_biomarker_crosswalk_v1.csv` 的 Wave 1 行对照。胱抑素 C 在 Wave 1 资料中为 `cystatinc`，作为年龄分层子样本指标排除于上述15项主假设族；如将来考虑纳入，须单独确认子抽样机制/权重并单独冻结假设族。

## 官方描述性 N 对账（2026-10-30）

使用服务器现有的受限、无标识符 `wave1_biomarker_value_profile_private.json`，将15个预设字段的有限数值记录数与 Blood Users' Guide 表4/表5明确标注的未加权 N 逐字段核对。15/15 与指南一致；校验只输出了整体匹配情况和不匹配字段名，没有读取/输出个人标识，也没有拟合关联。该对账支持变量映射、Stata缺失处理后的非缺失记录数与公开指南相符，但**不能证明有限数值特殊码不存在**、不能定义化验有效域、不能把assay检测范围变成排除线，也不能解码 `qc1_va003`。详细校验记录仅保留在服务器私有日志。

## 配置建议（仅候选）

- 将官方文档没有规定的有限特殊码、有效数值界限、LOD 代入/截尾及顶码规则标为 `unresolved`；由独立审阅者依据原始发行说明和必要的受控质量审计逐项裁决。不得为通过代码门禁而把未知写成“无特殊码”。
- 在逐项规则未审核前，不拟合 15 项中的任何 CHARLS 真实关联。后续候选默认只做 Stata 缺失值处理，连续值保留原始单位、不得自动非负筛选或依 assay detection range 剔除；这只是需审阅的最小处理候选，不等于已批准。
- 15 项变换目前一律未冻结。指南对某些指标的偏态描述可用于预注册身份/对数尺度敏感性候选，但不能按关联显著性、模型收敛或期望方向选择变换。标准化尺度须在同波同结局的冻结参考域计算，并与原单位效应并列保留。
- 结局缺失、暴露缺失、模型完整案例和年龄 domain 分别记录；不得把目标总体人数、观察血样数或候选目录数表述为任一配对的实际模型 N。

### 变换候选矩阵（供独立审阅；尚未冻结）

Blood Users' Guide 印刷第12页依据其加权密度图描述：总胆固醇、HDL、LDL、血糖和尿酸的均值/中位数较接近、分布看起来相对接近正态；CRP、HbA1c、甘油三酯、BUN、肌酐及胱抑素 C 右偏。该指南明确这些密度图为展示而省略了少数极端值；这些图不能被当成本项目的有效值筛选规则。根据这个公开的、关联分析前的分布描述，形成以下候选处理，最终仍由独立审阅者冻结：

| 指标组 | 2011 指南的描述 | 主要尺度候选 | 预设敏感性候选 | 限制 |
|---|---|---|---|---|
| CBC：白细胞、血红蛋白、红细胞压积、MCV、血小板 | Guide 未用上述密度图分类这些 CBC 结局 | 原始单位的 identity；模型若采用标准化系数，另保留可解释的原单位摘要 | 暂不根据关联结果另选 log/分段变换 | 不以临床阈值或指南 assay 范围删值/分组；需完成 Stata 特殊缺失规则审阅 |
| 相对对称的血液分析物：总胆固醇、HDL、LDL、尿酸 | Guide 描述为均值/中位数较接近、密度较相对对称 | 原始单位 identity | 关联前没有来源理由要求 log；如审阅人要求其他尺度，须单独说明依据并冻结 | 这只是相对分布描述，不证明回归残差正态或线性关系 |
| 右偏分析物：CRP、HbA1c、BUN、肌酐 | Guide 描述为右偏 | 原始单位 identity 作为可比的首选候选 | 自然对数尺度作为预先指定敏感性候选，仅在有效值规则完成且所有纳入值严格为正时考虑 | 不用 log 可行性倒推排除零/负值；不使用 assay detection range 作删值界限；若 log 前提不满足则该敏感性不适用并记录，不改主分析样本 |
| 血糖、甘油三酯 | Guide 描述为右偏/可能受空腹状态影响 | 原始单位 identity | fasting-only (`qc1_va003==1`) 主分析候选；全部观察血样加二元 fasting 协变量为敏感性候选，均须审阅估计目标和权重适用性 | 14个登记系数仍未获准拟合；映射已来源核实，有限特殊码与方法审阅仍待完成 |

该矩阵仅把 Guide 中的先验分布描述转化为可审阅的尺度候选，不代表变量有效值已确认、模型已准入或任何系数已拟合。任何对数敏感性需要在查看暴露—结局关联之前冻结，并作为明确的敏感性分析报告；如果进行推断，必须预先说明其多重检验家族，不能把其 p/q 混入 K=240 主要结果或按显著性挑选最终尺度。

## 官方来源锚点

- CHARLS, *Blood Data Users' Guide*: 采血与空腹说明印刷页4；方法和检测限表印刷页6；结果/极端值、HbA1c 与胱抑素 C 子样本说明印刷页12–13。项目归档件：[`sources_official/CHARLS_2011_Blood_User_Guide.pdf`](../sources_official/CHARLS_2011_Blood_User_Guide.pdf)；可检索文本：[`sources_official/CHARLS_2011_Blood_User_Guide_extracted.txt`](../sources_official/CHARLS_2011_Blood_User_Guide_extracted.txt)。
- Wave 1 原始变量名/单位的项目映射：[`blood_biomarker_crosswalk_v1.csv`](blood_biomarker_crosswalk_v1.csv)。这一映射本身不是有效值或模型准入批准。
- Wave 1 空腹字段/编码来源对账：[`wave1_fasting_code_source_reconciliation_2026-10-30.md`](wave1_fasting_code_source_reconciliation_2026-10-30.md)。这核实字段来源与1/2编码，不批准估计量或运行模型。
- 历史外部背景（不构成当前分析规则）：EAS/EFLM joint consensus, [*Fasting is not routinely required for determination of a lipid profile*](https://eas-society.org/wp-content/uploads/2022/05/2016_Consensus-lipid-profile-fasting.pdf)。此前曾引用该共识支持甘油三酯非空腹候选；该候选已被当前用户决定撤销。此一般临床共识不能替代 CHARLS Wave 1 `qc1_va003` 官方编码、研究估计目标或独立审阅，也不解锁甘油三酯模型。

## 审阅状态

本文件补齐来源定位与需裁决事项，并作为 Wave 1 pilot 计划指纹的一部分。它**不**批准 `communityID` 方差近似、目标 domain、结局有效值规则、模型协变量或任何真实关联运行。审阅人需结合受保护的 Wave 1 元数据/QA 和冻结配置，对每条规则决定通过、修订或阻断，并签署绑定哈希的记录。

## 2026-10-30 candidate registry to official crosswalk alignment check

A metadata-only consistency check compared the 15 private candidate outcome concepts against 2011 rows in `blood_biomarker_crosswalk_v1.csv`. All 15 matched on concept ID, source field, and unit; no missing mappings or field/unit discrepancies were found. The candidate file still marks all 15 outcome rules as not frozen, leaves finite numeric special-code handling unresolved, and keeps the two fasting-sensitive concepts blocked. This is a catalog/plan consistency check only: it does not validate participant values, choose a validity range, approve transformations, estimate model sample sizes, or fit associations. Reproducibility note: the candidate document and exact diagnostics remain in server-private review storage; no respondent-level data were read.
