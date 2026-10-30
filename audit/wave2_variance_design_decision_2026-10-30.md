# Wave 2 方差设计准入决策记录

**日期：**2026-10-30  
**状态：**未准入正式模型；本文仅依据公开抽样设计与 Wave 2 发布说明确定需要满足的方差设计条件，不读取个体记录或受保护 QA 输出。

## 本轮核实的官方证据

CHARLS 官方 Wave 2 Release Note（VersionID 20151118）将 `PSU.dta` 描述为包含省、市名称和地区类型；同一文件说明横断面标记 `crosssection`、纵向标记 `longitudinal` 及各自权重口径，但没有在发布说明中给出方差估计用的分层 ID、复制权重或方差软件设置。官方样本设计页描述的基线抽样则是县/区按地区、城乡和人均 GDP 排序分层，县/区内以 PPS 抽取村/社区作为 PSU；页面还记载有 30 个大社区被拆分抽样、部分社区因行政边界变化涉及两个县级单位。

**受控本机官方 PSU 包表头核验（2026-10-30）：** `2013_319_PSU.zip` 的 SHA-1 为 `74c78392b668375937e78ce5da4f06f5ba83f0f9`，与 CHARLS 官方 Wave 2 数据页列出的 PSU 文件值一致；ZIP 仅含 `PSU.dta`。只读取 Stata 元数据可见 450 行、8 列：`communityID`、省/市名称（中英文）、`urban_nbs`、`areatype`、`versionID`。未见县级抽样单位 ID、显式方差层或复制权重字段。这里的 450×8 是文件表头结构核验；未读取字段值或受访者记录。

以上信息说明“已发布 PSU 表”不等价于“已获得可直接用于复杂抽样方差估计的完整设计变量”。省、市、地区类型属于地理/设计背景字段，不能据此自行拼出官方 strata。Wave 2 Release Note 也没有说 Wave 2 的方差结构可直接照搬 Wave 1；必须针对 Wave 2 的样本和释放字段单独论证。

## 当前分析决定

1. **暂不将 Wave 2 关联模型设为可运行。** `crosssection` 与模块权重解决的是样本资格/非应答调整的一部分，不会补出 PSU 内抽样协方差、分层变量或有限总体修正信息。
2. **不把县级编码前缀、城市/农村、地区类型或省份自行指定为官方 strata。** 即使这些变量能生成稳定分组，也没有公开来源证据表明该编码等同实际抽样层；社区拆分和县界变化会进一步使简单地理前缀近似失真。
3. **不把“每县三个 PSU”的公开描述当作充分的方差设计输入。** 这说明总体抽样方案，不能单独给出本次发布样本中每个访谈社区的设计层归属、重复/拆分 PSU 对应关系或各层内实际 PSU 数。
4. **可继续进行来源绑定的字段/样本框 QA 与候选估计量文档工作，但不计算真实关联、标准误、置信区间或显著性。** 公开网站继续显示正式关联结果为 0。

## 解除门槛所需证据

针对拟定的每个 Wave 2 估计量，方法审查至少需要确认：

- 该目标总体及 `crosssection`/模块响应资格和对应权重的适用范围；
- 受访者能唯一映射到官方抽样 PSU，且对拆分社区、替换社区及跨县边界记录的处理有可追溯来源；
- 官方提供或可辩护重建的分层/抽样设计变量、PSU 处理、singleton strata 规则，以及权重是否适合对应分析子总体；
- 方差估计方法能够表示 CHARLS 的多阶段 PPS 设计，且由独立调查统计方法审查者书面复核；
- 对任何近似设计，明确其无法恢复的设计信息、估计目标限制、诊断和敏感性分析；若不能证明近似可辩护，则停止该目标的推断分析，只保留描述性目录/覆盖信息。

在上述证据未闭环前，不能以软件可执行、结果看起来合理、样本量充足或显著配对数量作为批准理由。完成设计审查后仍需单独冻结变量有效性、协变量/DAG、完整假设家族、多重比较及披露控制。

## 来源

- CHARLS [Wave 2 Release Note, VersionID 20151118](https://charls.pku.edu.cn/en/data/Release2013.pdf)，第 1–2 页：发布模块、`PSU.dta` 描述、横断面/纵向样本标记与权重、生物标志物权重。
- CHARLS [Wave 2 official data page](https://charls.charlsdata.com/pages/Data/2013-charls-wave2/en.html)：PSU archive SHA-1 and release listing.
- CHARLS [Sample design description](https://charls.pku.edu.cn/en/About/Sample.htm)：2011 基线多阶段 PPS 抽样、按地区/城乡/GDP 排序、社区作为 PSU、30 个社区拆分及县界变化说明。
- 当前项目的 Wave 2 权重/目标估计量复核：[`wave2_weight_estimand_source_review_2026-10-24.md`](wave2_weight_estimand_source_review_2026-10-24.md)。
- Wave 2 anthropometry/weight gate：[`wave2_anthropometry_release_weight_gate_2026-10-29.md`](wave2_anthropometry_release_weight_gate_2026-10-29.md)。
