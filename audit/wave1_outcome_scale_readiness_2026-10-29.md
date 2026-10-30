# Wave 1 血液结局：单位、测量范围与尺度预设审查

**日期：2026-10-29**  
**状态：元数据整理完成；结局有效值规则、变换和最终分析尺度均未获批准。**

## 2026-10-31 当前状态更正

本文件中 2026-10-30 以前写作“qc1_va003 数字编码未核实”的内容，是当时已检索来源范围下的历史记录，现由后续官方来源核对更新：CHARLS 2011 Fieldwork Plan 附录2与 Wave 1 Blood 表头共同支持 1=空腹、2=非空腹。该映射只确认字段含义，不解决有限数值型特殊码，也不证明 bloodweight 校正了进入空腹子样本的选择。

因此血糖和甘油三酯仍待估计目标、权重适用性、结局特殊码规则及独立方法审阅；其余13项也仍待结局规则与方法审阅。用户已选定的 communityID 聚类、无自造分层、WR Taylor 近似仍须独立审阅。当前正式关联模型为0，未通过冻结配置和 readiness 门前不运行。


本表根据项目公开 crosswalk 和 CHARLS 2011 Blood Sample Users' Guide 整理，不包含参与者记录或任何样本分布。对受控 Wave 1 Blood 文件仅以 metadata-only 方式核对了相关变量标签和值标签：可见变量标签提供测量名称/单位，但相关检测字段和 `qc1_va003` 均未关联 value-label set。表中“指南测定范围”是实验室 assay metadata，不是 CHARLS 分析有效值过滤线；不能据此删除超界观测、推断特殊缺失码或认定顶码。CHARLS Wave 1 官方指南描述血常规由各地实验室检测，未给这五项逐分析物的检测范围。胱抑素 C 不在当前15项普通血检结局家族内：其年龄分层抽测资格和权重需独立闭环。

### 官方指南中三类“范围/极端值”信息的区分（2026-10-31）

逐页复核官方 Blood Sample Users' Guide 后，结局规则卡明确区分以下信息，避免把测定能力误当成分析清洗规则：

1. 第7页的 assay 表标题明确是检测方法、批内/批间变异和 **detection limits**。这些是方法学测定范围；指南没有说超出界限的发布值应编码为缺失或删除。
2. 第14–15页的 Table 5 列出若干生化指标的描述统计和 observed ranges。它们是指南分析样本的观察范围，不是独立于样本的有效域定义。
3. 第11页说明密度图为展示省略了少数极端观测；这是一项图形展示处理，指南没有将其定义为分析数据剔除方案。

据此，默认清洗规则仍为：遵守 Stata 系统缺失表示；保留其余可解析有限值作为待审候选；不因 detection limits、Table 5 observed ranges、临床风险阈值或密度图省略做逐人过滤。有限数值型 sentinel 是否存在仍待解决，故这条候选不能被写成“所有有限值均经官方验证”，也不能单凭此段关闭结局准入。来源：[CHARLS 2011 Blood Sample Users' Guide，第7、11、14–15页](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)。

### 15项共同处理候选及字段级状态

已核的 Wave 1 Blood header 将15项结局列为数值型 float，未附 value-label set，也未声明 Stata tagged-missing 元数据。已核官方 Wave 1 Blood Guide、National Baseline Users' Guide 与 Codebook 未给这15项的有限数值型特殊缺失码表。此为已检索来源中的“未发现定义”，不是对其他未取得内部文档或有限 sentinel 不存在的证明。提交独立审阅的共同候选为：Stata 系统缺失按缺失处理；其他可解析有限值暂保留；identity scale；不按检测限、观察范围、临床阈值或分布删值。15项均为候选而非批准规则。血糖和甘油三酯的 `qc1_va003` 编码已由官方来源核实为1=空腹、2=非空腹；尚未决定其估计目标和 `bloodweight` 对条件性子域的适用性，故这两项仍阻断拟合。

## 15项目录和暂定报告尺度

| 结局 | Wave 1 字段 | 原始单位（报告原始效果） | 指南测定范围（仅方法元数据） | 当前处理决定 |
|---|---|---|---|---|
| 白细胞计数 | `qc1_vb002` | 1000 cells/μL | 指南未列逐项范围 | identity/raw-finite 处理为待审候选；有限 sentinel 未知；原单位效果候选 |
| 血红蛋白 | `qc1_vb004` | g/dL | 指南未列逐项范围 | identity/raw-finite 处理为待审候选；有限 sentinel 未知；原单位效果候选 |
| 红细胞压积 | `qc1_vb005` | % | 指南未列逐项范围 | identity/raw-finite 处理为待审候选；有限 sentinel 未知；原单位效果候选 |
| 平均红细胞体积 | `qc1_vb006` | fL | 指南未列逐项范围 | identity/raw-finite 处理为待审候选；有限 sentinel 未知；原单位效果候选 |
| 血小板计数 | `qc1_vb009` | 10^9/L | 指南未列逐项范围 | identity/raw-finite 处理为待审候选；有限 sentinel 未知；原单位效果候选 |
| 甘油三酯 | `newtg` | mg/dL | 4–1000 mg/dL | `qc1_va003`编码1/2已核实；估计目标及权重适用性未决；有限 sentinel 未知，identity/raw-finite仍待审 |
| 肌酐 | `newcrea` | mg/dL | 0.1–25 mg/dL | identity/raw-finite 处理为待审候选；有限 sentinel 未知；不按检测范围过滤 |
| 血尿素氮 | `newbun` | mg/dL | 5–100 mg/dL | identity/raw-finite 处理为待审候选；有限 sentinel 未知；不按检测范围过滤 |
| 高密度脂蛋白胆固醇 | `newhdl` | mg/dL | 3–120 mg/dL | identity/raw-finite 处理为待审候选；有限 sentinel 未知；不按检测范围过滤 |
| 低密度脂蛋白胆固醇 | `newldl` | mg/dL | 3–400 mg/dL | identity/raw-finite 处理为待审候选；有限 sentinel 未知；不按检测范围过滤 |
| 总胆固醇 | `newcho` | mg/dL | 3–800 mg/dL | identity/raw-finite 处理为待审候选；有限 sentinel 未知；不按检测范围过滤 |
| 血糖 | `newglu` | mg/dL | 2–450 mg/dL | `qc1_va003`编码1/2已核实；估计目标及权重适用性未决；有限 sentinel 未知，identity/raw-finite仍待审 |
| 尿酸 | `newua` | mg/dL | 上限20 mg/dL（指南所列） | identity/raw-finite 处理为待审候选；有限 sentinel 未知；不按检测范围过滤 |
| C反应蛋白 | `newcrp` | mg/L | 0.1–20 mg/L | identity/raw-finite 处理为待审候选；有限 sentinel 未知；不按检测范围过滤 |
| 糖化血红蛋白 | `newhba1c` | % | 0–40% | identity/raw-finite 处理为待审候选；有限 sentinel 未知；不按检测范围过滤 |

## 统一估计尺度建议（待独立审阅，不是模型批准）

1. 每个结局保留经来源审查后的原始单位系数、置信区间和单位说明；不静默换算单位。
2. 为跨结局展示，可增加标准化系数：在冻结的血检目标域/估计总体内，按适用权重计算同一结局的加权均值与标准差，再以该标准差缩放；同一波次、同一结局在所有暴露和模型间共用一个参考尺度。原始系数仍为主解释尺度。
3. 目前不冻结 log 或其他变换。对于偏态结局，应在查看配对结果前，以官方有效值规则、预先规定的诊断和审阅决定是否设置变换/敏感性模型；如果采用 log，必须明确结果是 log 结局尺度效应，不误报成原始单位差或百分比变化。
4. 指南测定范围仅描述检测方法能力，**不是**默认上下限。正式过滤必须由该发布版本明确的特殊缺失/顶码/有效域证据支持；若无可追溯规则，则该结局保持阻断或按审阅人批准的保守方案处理，不从经验范围或样本分位数反推。
5. 血糖和甘油三酯保留空腹状态信息。官方 Fieldwork Plan 附录2与 Blood 表头支持编码 1=空腹、2=非空腹；这只完成编码核实，不证明 bloodweight 校正空腹选择。需先审阅估计目标、权重适用性与测量规则。
6. CBC 与中心实验室化学检测的处理/测量流程不同，不应把中心实验室所列范围套用到 CBC。Cystatin C 的年龄分层随机测定应独立定义目标域/权重，不纳入这15项共同主族。

## 本轮的实际结论

- Wave 1 官方四类输入已入受控目录且来源身份已确认；这是当前情况，取代旧版文件中“输入尚未入库”的历史描述。
- 本轮只使用公开手册和公开 catalog 元数据整理量纲/测定范围，未读取参与者答案、未生成任何分布/计数，也未拟合 CHARLS 关联。
- 目前正式模型仍为0。来源门通过不等于设计或分析放行。剩余准入包括最终PSU/方差审阅、结局有效值与特殊码、空腹估计目标及权重兼容性、冻结配置和独立方法审阅。
- 变量键及字段单位来源见 [`blood_biomarker_crosswalk_v1.csv`](blood_biomarker_crosswalk_v1.csv)；实验室方法资料见 [`blood_assay_method_metadata_2011_2015_2026-10-22.md`](blood_assay_method_metadata_2011_2015_2026-10-22.md) 和 [CHARLS Blood Sample Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)。官方Wave 1页面列明该数据与文档产品：[CHARLS 2011 Wave 1 data page](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)。

## 2026-10-31 — 补充 AI 方法复核意见（不构成准入）

对公开结局规则卡、尺度审计及空腹估计量材料进行的独立 AI 文档复核认为，“Stata missing 视为缺失、保留其余有限发布值、不按 assay detection range 或观察分布过滤”可以作为透明候选提交人工审阅，但不能据此放行模型。其理由是：现有发布表头未定义有限数值型 sentinel，且指南 assay 范围不是个体有效值界限；同时，两项材料都不能证明有限 sentinel 不存在。

复核要求冻结时逐项说明单位、缺失处理、保留有限值的理由与 sentinel 不确定性、禁止按检测范围/临床阈值/分布删值的约束、变换决策，以及发现新官方特殊码证据时必须重新审阅。指南公开 N 对账只支持总量一致，不能证明每个数值都有效。葡萄糖与甘油三酯仍须单独解决 fasting estimand 和 `bloodweight` 适用性。该复核是 AI 辅助意见，**不等同于外部/具名方法审阅，不是批准记录，不改变 15 项 `candidate_not_frozen` 或关闭的 readiness 门**。

## 空腹记录与结局测量解释（背景；编码结论以官方来源复核为准）

CHARLS 2011 Blood Sample Users' Guide 说明采血前要求隔夜空腹，但非空腹者仍接受采血，且空腹状态记录在数据中；指南报告血样参与者中超过92%为空腹（指南印刷页约8–9，PDF页14–15）。官方 Fieldwork Plan 附录2与 Wave 1 Blood 字段标签共同支持 `qc1_va003` 编码 1=空腹、2=非空腹。该映射仅确认测量条件编码，不证明 `bloodweight` 校正了进入空腹子样本的选择。非空腹样本不自动判为无效；对血糖和甘油三酯，估计目标、权重适用性及敏感性方案仍须在查看关联结果前冻结。

同一指南描述的偏态/近似正态是指南作者对其分析样本的分布观察，不构成 CHARLS 的通用转换或异常值剔除规则。指南为图示而省略少数极端值，也不能转化为本项目的过滤线。葡萄糖、甘油三酯、HbA1c的采样/运输注意事项应作为解释限制与预先设定的敏感性方案输入；不得依据本项目观察到的分布选择变换、截尾点或样本。指南指出胱抑素C仅在血样参与者中的70岁以上人群及70岁以下随机子样本测量，故它仍需单独解决分析物抽样资格与权重，不进入15项共同结局族。

## 2026-10-30 受控字段元数据及值域 QA 补充

- 对官方 Blood 文件做了 metadata-only 扩展审计：15项结局均存为 Stata `float`，显示格式为 `%9.0g`；`qc1_va003` 存为 `int8`、格式 `%8.0g`。这些是存储/显示元数据，不提供数值含义；16个审计字段仍无附属 value-label set。
- 追加检查 Stata header 的 tagged-missing 元数据后，16个字段均未声明 `.a`–`.z` 用户缺失标签。这个结果不能排除有限数值型占位码，也不能代替 Wave 1 官方有效域/特殊码说明；有限值规则仍未冻结。
- 随后在授权服务器仅读取15项预设结局列，输出受限、无标识符的汇总诊断至 `private/qa_outputs/wave1_biomarker_value_profile_private.json`（mode 600）。没有读取ID、没有使用权重、没有拟合关联，也未向公共仓库或网站复制报告。
- 该汇总未发现负值、非有限值或数值解析失败；部分观测极值落在 Blood Guide 的 assay-method table 范围之外。具体字段/极值仅留在服务器受限 QA。它们只是需要源资料审查的信号；本项目没有据此判定无效、剔除记录或反推特殊码。
- 因此，连续结局的数值有效性/特殊码规则仍未冻结；`qc1_va003` 映射仍未解决。15项的单位、Guide assay 方法范围、原始尺度候选和未决状态见上表；assay范围不自动成为过滤线。

指南报告的临床高风险界值（例如血糖、血脂、CRP及血红蛋白界值）用于描述特定风险分类比例；它们不是本项目连续 ExWAS 结局的默认定义，也不构成 CHARLS 字段有效值范围。主图谱继续以经核实单位的连续化验值为候选；若未来希望展示阈值型结果，应逐项核对界值适用人群与来源，并在完整检验前预设为独立次要分析族，不能将二分结果与连续结局混成同一检验族或用观察结果挑阈值。官方指南的阈值表见印刷页16（PDF页21）。

## 2026-10-30 官方结局来源逐项核查补充（该日审阅状态；编码状态见 2026-10-31 更正）

- 复核了 [CHARLS 2011 Wave 1 官方数据页](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)、[2011 Blood Data Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)、2011问卷/Codebook，以及受控发行文件的header元数据。2011指南说明受访者被要求隔夜空腹，但非空腹仍采血且状态记入数据；已核材料没有给 `qc1_va003` 数字编码映射。文件头也没有附值标签或声明 Stata tagged-missing 元数据；有限数值型占位码仍不能因此排除。
- [CHARLS 2015 Blood Data Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf) 明确列出 Wave 3 的 `bl_fasting` 与甘油三酯顶码标志。它们是独立的 Wave 3 发布信息，**不能**据此推断 Wave 1 的 fasting 数字编码或 Wave 1 顶码规则。
- 为缩小下一步审阅范围，已生成受保护的 15 项 Wave 1 结局候选。字段/单位与指南 assay 范围已登记；有限特殊码仍未定。空腹编码现已来源核实，但血糖和甘油三酯仍须审阅估计目标与权重适用性；其他13项也须审阅有效值规则，所有候选处理仍未批准。
- 对105项固定试点假设，14项血糖/甘油三酯系数仍因估计目标、权重和结局规则未决而阻断；空腹编码本身已来源核实。此数是登记配对的计划分解，不是有效分析样本数、完成模型数或结果数。
