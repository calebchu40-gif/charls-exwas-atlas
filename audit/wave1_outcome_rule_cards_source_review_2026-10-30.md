# Wave 1 血液结局逐项来源规则卡（供冻结与方法审阅）

**日期：**2026-10-30  
**状态：**来源核对与候选规则；未获独立审阅，不是有效值批准，也不开放关联模型。  
**范围：**用户预设 pilot105 / K150 / K90 中的 15 项 Wave 1 常规血液指标。未读取任何受访者化验取值。

## 来源核对结论

1. CHARLS 2011 Blood Users' Guide 的采血说明（印刷页4）写明调查要求过夜空腹，但非空腹样本仍会采集且空腹状态会记录；同一指南提示非空腹样本的血糖可能偏高。Wave 1 字段 `qc1_va003` 的数值编码仍未在已核对的官方 Codebook、用户指南或 Stata 表头中找到可追溯映射。因此不能构造葡萄糖空腹限制，也不能将 Wave 3 编码移植到 Wave 1。
2. 指南表1（印刷页6）把化学分析的数值列为**assay detection limits**；它不是个体观测的有效范围、排除阈值、截尾规则或临床诊断界值。指南第6节（印刷页12–13）还说明部分密度图省略了少数极端观测，但没有列出观测、算法或可复现删值规则。故不得把表1范围当作筛除上下限，也不得凭样本分位数删值/winsorize。
3. Wave 1 Blood 文件头信息与已审核资料未提供这些指标的附属值标签/可执行有限特殊值映射。Stata 扩展缺失须继续按缺失处理；表头中缺少标签不等于证明不存在有限数值型特殊码。仅凭 assay 范围、观察分布或常用临床阈值不能批准一个有限值域。
4. 指南说明胱抑素 C 采取年龄分层子样本检测（70岁及以上全测、较年轻者随机抽取；印刷页12），而可用资料未证明当前 `bloodweight` 同时校正该检测子抽样。因此 blood_cystatin_c 不纳入这 15 项全样本假设族。该决定与登记簿一致；15 项不是把所有可见生物指标无条件全纳入。

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
| 甘油三酯 | `newtg` | mg/dL | 酶比色法；表1报告 assay detection range 4–1000 mg/dL | 7项关联在权威 Wave 1 `qc1_va003` 空腹编码及规则审核前保持阻断；一般非空腹血脂共识不足以替代该研究的测量规则审查。不得把检测范围作顶码或排除阈值。 |
| 葡萄糖 | `newglu` | mg/dL | 酶比色法；表1报告 assay detection range 2–450 mg/dL；指南提示非空腹值可能偏高 | 七项关联继续标记不可估，直到获得权威 Wave 1 空腹码映射；不猜编码、不按 `qc1_va003` 频数反推。 |
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

## 官方来源锚点

- CHARLS, *Blood Data Users' Guide*: 采血与空腹说明印刷页4；方法和检测限表印刷页6；结果/极端值、HbA1c 与胱抑素 C 子样本说明印刷页12–13。项目归档件：[`sources_official/CHARLS_2011_Blood_User_Guide.pdf`](../sources_official/CHARLS_2011_Blood_User_Guide.pdf)；可检索文本：[`sources_official/CHARLS_2011_Blood_User_Guide_extracted.txt`](../sources_official/CHARLS_2011_Blood_User_Guide_extracted.txt)。
- Wave 1 原始变量名/单位的项目映射：[`blood_biomarker_crosswalk_v1.csv`](blood_biomarker_crosswalk_v1.csv)。这一映射本身不是有效值或模型准入批准。
- 甘油三酯非空腹候选的外部临床实验室背景：EAS/EFLM joint consensus, [*Fasting is not routinely required for determination of a lipid profile*](https://eas-society.org/wp-content/uploads/2022/05/2016_Consensus-lipid-profile-fasting.pdf)。该共识支持一般临床 lipid profile 的非空腹测量，不替代 CHARLS Wave 1 变量映射、暴露研究的估计目标冻结或独立方法审阅。

## 审阅状态

本文件补齐来源定位与需裁决事项，并作为 Wave 1 pilot 计划指纹的一部分。它**不**批准 `communityID` 方差近似、目标 domain、结局有效值规则、模型协变量或任何真实关联运行。审阅人需结合受保护的 Wave 1 元数据/QA 和冻结配置，对每条规则决定通过、修订或阻断，并签署绑定哈希的记录。
