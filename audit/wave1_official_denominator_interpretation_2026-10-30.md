# Wave 1 官方分母口径核对

**日期：**2026-10-30  
**范围：**官方基线指南表格与受保护目录中已经完成的 ID-only 聚合对照；未读取任何受访者答案或估计关联。

## 官方文件中的不同计数

CHARLS 2011 National Baseline Users' Guide 将成功访谈总数报告为 **17,708 人、10,257 户**。指南 Table 4 的年龄/性别/户籍描述表为 **17,587 人**，并明确说明缺少年龄、性别或户籍信息的个体未纳入该表。因此，17,587 是这三个描述变量齐全的表格子集，不是另一个完整访谈框，也不能替代血检指南中用于目标样本的 17,708。

同一指南的 Table 5 仍以 17,708 为总数，并报告直接访谈与代理访谈构成；这再次说明 Table 4 少掉的 121 人是描述表字段缺失导致的表格分母差异。官方文字没有进一步给出这 121 人分别缺哪些字段，不应推断具体缺失组合。

## 与发行文件对照结果的区别

受保护的 ID-only 核对显示：官方 Weight 文件有 17,708 条不同个人记录，其中 `ind_weight_ad2` 非缺失/正权重 ID 为 17,708；已重建的 `demographic_background` 个人主表及其唯一 ID 数为 17,705。另有 3 个正权重 ID 未出现在该人口学主表，但可在其他个人模块中找到；这些记录在 Blood 文件中均未出现。对应的精确身份只在内存处理、未写出；模块出现不能判定其访谈资格或血检资格。

因此须区分两个问题：

1. 官方指南 17,708 与 17,587 的 **121 人差异**：指南说明为描述表缺少年龄、性别或户籍者未纳入 Table 4。
2. 官方发行文件 Weight 17,708 与人口学主表 17,705 的 **3 人链接差异**：这是本项目发行文件 ID 对照中的待解释差异；它没有被上述官方表格脚注直接解释。

Blood 文件 11,847 条与指南完整血样样本数相符；Blood IDs 及其正权重 `bloodweight` 均链接到当前个人主表。这个血检响应者链接结果不能单独证明完整目标框、年龄/配偶资格或复杂抽样方差已经全部通过。

## 对当前设计决策的影响

- 完整访谈/血检目标的官方人数仍依据 17,708 的指南口径；不得把 Table 4 的 17,587 误当成完整样本框。
- 3 个未链接人口学主表的正权重 ID 不能靠总数推断资格。它们未出现在 Blood 文件，因此血检响应者链接未因此扩张或丢失；完整框的年龄/资格重建仍须遵循官方路由与来源。
- 这项计数澄清不解决 Wave 1 最终 PSU/分层与方差方法，也不批准模型。正式关联模型仍为 0。

## 官方来源

- [CHARLS 2011 National Baseline Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/CHARLS_nationalbaseline_users_guide.pdf)：访谈总数、Table 4 的排除脚注、Table 5 的访谈/代理分母。
- [CHARLS 2011 Blood Data Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)：完整血样目标与样本量。
- [CHARLS 2011 Wave 1 data directory](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)：发行文件与指南目录。

本记录只包含官方已发布的聚合计数和方法解释，不包含个人标识、个人记录、关联统计量或受限运行输出。
