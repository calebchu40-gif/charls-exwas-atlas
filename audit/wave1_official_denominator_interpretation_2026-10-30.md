# Wave 1 官方分母口径核对

**日期：**2026-10-30  
**范围：**官方基线指南表格口径；受保护目录的文件级链接诊断不在本公开记录中。

## 官方文件中的不同计数

CHARLS 2011 National Baseline Users' Guide 将成功访谈总数报告为 **17,708 人、10,257 户**。指南 Table 4 的年龄/性别/户籍描述表为 **17,587 人**，并明确说明缺少年龄、性别或户籍信息的个体未纳入该表。因此，17,587 是这三个描述变量齐全的表格子集，不是另一个完整访谈框，也不能替代血检指南中用于目标样本的 17,708。

同一指南的 Table 5 仍以 17,708 为总数，并报告直接访谈与代理访谈构成；这再次说明 Table 4 少掉的 121 人是描述表字段缺失导致的表格分母差异。官方文字没有进一步给出这 121 人分别缺哪些字段，不应推断具体缺失组合。

## 与发行文件对照结果的区别

受保护环境中的文件链接诊断仍待解释。为避免公开由个体级文件派生的小单元链接结果，本记录不列出相关发行文件逐人计数或模块交叉情况；请以官方指南的已发表总体口径为准。文件级诊断只留在受控 QA 环境，并且不能单独证明样本资格。

因此须区分两个问题：

1. 官方指南 17,708 与 17,587 的 **121 人差异**：指南说明为描述表缺少年龄、性别或户籍者未纳入 Table 4。
2. 受保护发行文件之间的链接诊断：仍待解释，且不属于官方表格脚注所说明的表格分母差异；细节留在受控 QA 环境。

Blood 文件 11,847 条与指南完整血样样本数相符；Blood IDs 及其正权重 `bloodweight` 均链接到当前个人主表。这个血检响应者链接结果不能单独证明完整目标框、年龄/配偶资格或复杂抽样方差已经全部通过。

## 对当前设计决策的影响

- 完整访谈/血检目标的官方人数仍依据 17,708 的指南口径；不得把 Table 4 的 17,587 误当成完整样本框。
- 文件间链接差异不能靠总体计数推断资格；完整框的年龄/资格重建仍须遵循官方路由与来源。
- 这项计数澄清不解决 Wave 1 最终 PSU/分层与方差方法，也不批准模型。正式关联模型仍为 0。

## 官方来源

- [CHARLS 2011 National Baseline Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/CHARLS_nationalbaseline_users_guide.pdf)：访谈总数、Table 4 的排除脚注、Table 5 的访谈/代理分母。
- [CHARLS 2011 Blood Data Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)：完整血样目标与样本量。
- [CHARLS 2011 Wave 1 data directory](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)：发行文件与指南目录。

本记录只包含官方已发布的聚合计数和方法解释，不包含个人标识、由受限数据派生的小单元链接结果、关联统计量或受限运行输出。
