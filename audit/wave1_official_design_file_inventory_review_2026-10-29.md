# Wave 1 官方抽样设计文件清单复核

**日期：2026-10-29**  
**状态：核查了官方公开发行清单及官方设计文档；未找到可解除现有子 PSU/方差字段门的新增 Wave 1 文件。**

## 官方 Wave 1 公开发行清单

CHARLS 官方 2011 Wave 1 (Baseline) 页面列出的分析文档包括 Household Questionnaire、Physical Examination Questionnaire、User's Guide、Codebook、Community Questionnaire 和 Blood Data User's Guide；下载数据清单列出 All dataset、各问卷模块、PSU、Weight、Community data 和 Blood data。页面没有列出独立的 Wave 1 Sample Information 文件、replicate weights 文件或 variance-strata 文件。

因此，按官方公开基线发行清单，本项目当前检查的 All Data、PSU、Weight、Community 和 Blood 产品已经覆盖该页面列出的相关产品类别。该发现不排除 CHARLS 账号内存在额外受限技术文件或后续更正；但当前不能把另一个波次的 Sample_Info 预期为 2011 缺失字段的替代。

## Sample Information 的跨波解释限制

CHARLS 2018 Wave 4 User's Guide 把 Sample_Info.dta 描述为回应状态、横截面标记、死亡状态和访谈日期，并另列 Sampling Weights；同一指南称 PSU information 与此前波次相同。这说明 Sample_Info 的已记录用途主要是样本状态/跟踪元数据，不能据此认定它提供 2011 子 PSU respondent crosswalk 或方差层。

2015 和 2018 页面确实列有各自的 Sample Information 文件，但这不证明相同文件/字段存在于 2011，也不允许用后波样本状态文件代替 2011 PSU 映射。

## 对当前设计门的影响

1. 官方 Wave 1 下载页列出的 PSU 数据与当前核验的 PSU.dta 表头一致：可以把其社区键视为 PSU 候选标识，但目前没有证据显示它含可连接到个人/家庭记录的拆分子 PSU 键或显式方差层。
2. Wave 1 Community data 中存在 sub_commuID，但个体问卷模块及 PSU 文件未见对应个人级字段。仅有社区层的子区字段不足以确定某名受访者属于哪个被抽中的子区。
3. 暂未发现官方 Wave 1 replicate weights/variance stratum 文件，也未找到官方指定的近似方差估计方案。不能用地理字段拼造分层，也不能仅因权重存在就假设方差估计已解决。
4. 设计准入仍保持阻断。可由独立复杂抽样审阅者评价不同估计目标下社区聚类近似方案能支持什么推断；若无法支持目标总体方差，应降低估计目标/发布措辞或停止推断，不能以普通回归标准误冒充调查设计方差。

## 下一步审阅问题

- 2011 实际抽样分层、县级单位、社区PSU和30个子区的层级关系是什么？哪些是选择单元，哪些仅为隐式排序变量？
- 在公开数据缺少正式方差层/复制权重和拆分社区个人映射时，哪些 design-based variance 估计是可辩护的？社区聚类近似适用于何种 estimand、哪些自由度/单 PSU 处理？
- bloodweight 的权重调整已知不能代替抽样设计变量；在估计血检参与校正关联时，可否获得合规、可复核的方差，还是应限定为特定样本中的加权关联并弱化总体推断？

在这些问题获得独立审查结论并绑定到当前来源 manifest、准备表和冻结方案之前，不拟合正式关联模型。

## 官方来源

- [CHARLS 官方 2011 Wave1 (Baseline) 数据与文档清单](https://charls.pku.edu.cn/en/Data/a2011_CHARLS_Wave1__Baseline_.htm)：列出 Wave1文档和 All Data、PSU、Weight、Community、Blood等数据产品。
- [CHARLS 2011 National Baseline Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/CHARLS_nationalbaseline_users_guide.pdf)：社区PSU、分层抽样和大型社区拆分说明。
- [CHARLS 2018 Wave 4 User's Guide](https://charls.pku.edu.cn/en/data/User2018.pdf)：Sample_Info.dta 和 PSU 跨波说明；仅用于解释 Wave 4 文档列出的文件用途，不外推 Wave1变量。
- [CHARLS 2015 Wave 3 数据页](https://charls.pku.edu.cn/en/Data/a2015_CHARLS_Wave_3.htm) 与 [2018 Wave 4 数据页](https://charls.pku.edu.cn/en/Data/a2018_CHARLS_Wave_4.htm)：证明这些后续波次分别发布自己的 Sample Information，不能替代基线字段。

