# CHARLS 五个主波官方设计文件表头复核

**日期：**2026-10-30  
**状态：**来源/表头元数据核验完成；不构成调查方差设计准入。  
**范围：**受保护本地入库中的 Wave 1–5 PSU、样本信息、权重，以及 Wave 1/3 Blood 发行包中与设计有关的字段。

## 目的

在已经确认 Wave 1 缺少完整公开方差键、且逐波分析不能默认沿用同一设计规格后，集中核对本地已入库的官方设计文件是否提供了县级抽样单位、方差分层、复制权重或拆分社区最终 PSU 映射。只核对官方发行包 SHA-1、压缩包成员名和 Stata 文件元数据表头；没有读取任何受访者字段值，也没有运行模型。

## 核验结果

对 Wave 2–5 本轮核对的 ZIP，SHA-1 与对应 CHARLS 官方数据页所列值逐一匹配（大小写不敏感）。Wave 1 则沿用本人确认的官方来源清单及本地 SHA-256 指纹；CHARLS 所查 Wave 1 页面未列发布校验和。核对的产品包括：

| 波次 | 官方产品 | 表头中与样本/设计有关的字段 | 新识别的正式方差变量 |
|---|---|---|---|
| 2011 | PSU、Weights、Blood | PSU 产品含 `communityID`、省市名称、NBS城乡/地区类型、版本；权重及 Blood 各有其 ID、适用权重字段 | 未发现县级抽样单位 ID、显式方差层、复制权重或拆分子社区到个人的最终 PSU 映射 |
| 2013 | PSU、Weights | PSU 产品与上述 PSU 字段结构一致；Weights 含横断面/纵向标记、各类权重、访谈年月、ID 与社区键 | 未发现县级抽样单位 ID、显式方差层、复制权重或拆分子社区最终映射 |
| 2015 | Sample_Infor、Weights、Blood | Sample_Infor 含 ID、家庭/社区键、`crosssection`、死亡标记、访谈年月；Weights 含 ID/社区键及横断面权重；Blood 含 `Blood_weight` 和社区键 | 文件表头没有额外正式方差层或复制权重；仍缺拆分子社区最终 PSU 映射 |
| 2018 | Sample_Infor、Weights | 两类文件含 ID/家庭/社区键、横断面标记/访谈年月及对应横断面权重 | 未发现显式方差层、复制权重或新的最终 PSU 映射 |
| 2020 | Sample_Infor、Weights | 字段结构与 2018 同类产品相近，含 ID/家庭/社区键、横断面标记/访谈年月及横断面权重 | 未发现显式方差层、复制权重或新的最终 PSU 映射 |

CHARLS 2020 Wave 5 User Guide 的数据集章节明确写明“PSU information is the same as previous waves”，并将 `Sample_Infor.dta` 描述为记录响应样本、横断面资格、死亡和访谈时间，将权重文件描述为横断面权重。这与本地 2018/2020 文件表头一致：后续 Sample_Infor 和 Weights 文件没有补入可见的县级设计层或复制权重字段。Wave 2 发布说明也没有把省市、城乡或地区类型定义为方差 strata；这些字段不得自行拼成正式分层变量。

## 对准入的影响

1. 官方产品来源及文件字节校验通过，只证明本次检查文件与对应官方发行清单一致；不证明其抽样设计信息足以估计正确的标准误。
2. `communityID` 是官方发布的社区键/PSU 相关键，但公开表头与设计说明没有解决大社区拆分后个人属于哪个子 PSU、县级隐式排序分层如何进入方差估计等问题。
3. 访谈权重、血检权重、`crosssection` 标记解决目标样本或非应答校正的一部分，不替代 PSU/分层信息；不得用“有权重”推断“完整复杂抽样方差可估”。
4. Wave 1 和 Wave 2 的正式关联模型继续为 0。2015 Blood 的 `Blood_weight` 不使方差门自动通过。任何单层近似仍须先由独立调查抽样统计审查书面裁决，并按波次、目标估计量及年龄域分别说明。

## 可复核的官方来源

- [2011 Wave 1 官方数据与文档目录](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)
- [2013 Wave 2 官方数据目录](https://charls.charlsdata.com/pages/Data/2013-charls-wave2/en.html)
- [2015 Wave 3 官方数据目录](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html)
- [2018 Wave 4 官方数据目录](https://charls.charlsdata.com/pages/Data/2018-charls-wave4/en.html)
- [2020 Wave 5 官方数据目录](https://charls.charlsdata.com/pages/Data/2020-charls-wave5/en.html)
- [2020 Wave 5 User Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_User_Guide_English.pdf)，第 28 页：Wave 5 PSU 信息与前波相同；Sample_Infor 与横断面权重文件用途。
- [CHARLS 官方抽样设计说明](https://charls.pku.edu.cn/en/About/Sample.htm)：县/区排序分层与 PPS、村/社区 PSU、大社区子区抽样及边界变化说明。

本备忘录不包含受访者记录、ID、逐人匹配结果、派生小单元统计或任何关联结果；全部原始文件及详细 QA 仍留在受保护的本机目录。
