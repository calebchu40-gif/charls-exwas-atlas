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

2026-10-29 对照 CHARLS 官方样本页再次细化抽样/年龄路由：入户筛查后，先从年龄超过40岁的成员随机选一人；若其年龄≥45则作为主要受访者并访问配偶，40–44则进入 refresher 预留路径。该叙述不单独确定血检分析权重分母，因此血检纳入仍按 Wave 1 Blood Guide/Weight 及逐人来源对账冻结。官方页面还把县级单位按地区、城乡类别、人均 GDP 排序后进行 PPS；这是抽样时的分层/排序说明，不等于公开 PSU 文件中存在可直接用于方差估计的 stratum ID。来源：[CHARLS 官方 Sample 页面](https://charls.pku.edu.cn/en/About/Sample.htm)。

1. 官方 Wave 1 下载页列出的 PSU 数据与当前核验的 PSU.dta 表头一致：可以把其社区键视为 PSU 候选标识，但目前没有证据显示它含可连接到个人/家庭记录的拆分子 PSU 键或显式方差层。
2. Wave 1 Community data 中存在 `sub_commuID`，但个体问卷模块及 PSU 文件没有该个人级字段。进一步的受保护键结构 QA 将空格形式的空值规范化后发现：非空子区记录只涉及拆分父社区，个体记录仅有父 `communityID`；对同一父社区存在多个子区的情形，仍不能确定某名受访者属于哪个被抽中的子区。精确 QA 计数与 ID 留在服务器受保护区。
3. 暂未发现官方 Wave 1 replicate weights/variance stratum 文件，也未找到官方指定的近似方差估计方案。不能用地理字段拼造分层，也不能仅因权重存在就假设方差估计已解决。
4. 设计准入仍保持阻断。可由独立复杂抽样审阅者评价不同估计目标下社区聚类近似方案能支持什么推断；若无法支持目标总体方差，应降低估计目标/发布措辞或停止推断，不能以普通回归标准误冒充调查设计方差。

## 下一步审阅问题

- 2011 实际抽样分层、县级单位、社区PSU和30个子区的层级关系是什么？哪些是选择单元，哪些仅为隐式排序变量？
- 在公开数据缺少正式方差层/复制权重和拆分社区个人映射时，哪些 design-based variance 估计是可辩护的？社区聚类近似适用于何种 estimand、哪些自由度/单 PSU 处理？
- bloodweight 的权重调整已知不能代替抽样设计变量；在估计血检参与校正关联时，可否获得合规、可复核的方差，还是应限定为特定样本中的加权关联并弱化总体推断？

在这些问题获得独立审查结论并绑定到当前来源 manifest、准备表和冻结方案之前，不拟合正式关联模型。

### 2011 官方 Codebook 对 PSU 字段的交叉核验（2026-10-29）

重新检查本机保存的官方 2011 Codebook 提取文本第15节（印刷页1340–1341）。PSU 数据块列出 `communityID`、`province`、`city`、`urban_nbs`、`areatype`，未列县级抽样单位 ID 或方差 strata；本轮 PSU 文件实际表头一致，另有版本字段。加上受控键拓扑 QA 显示 province/city 名称组合不能充当官方 county-unit 一对一键，当前发行文件不足以直接复原县级第一阶段分层/PPS 单元。确切私有聚合数留在本机受控 QA 目录，不进入此仓库。

这把“尚未找到映射”的证据提升为“已核对当前官方 Codebook 对 PSU 产品的全部公开字段清单，但未发布 county-unit/strata 字段”。若用户获准账号中后续出现官方技术补充，应重新审核；当前不能从地区标签、文本地名或 `communityID` 编码模式自行拼造抽样设计。外部方法审阅仍需决定：在无法复原县级层及拆分子社区归属时，是否存在可报告的社区级近似 estimand，或应停在描述统计。

### 空白键复核更正（2026-10-29）

第一轮快速 key summary 未把仅含空格的 `sub_commuID` 当作缺失值，导致将其误计为有效子区标识。用去空格并将空字符串转为缺失后，确认子区编号只覆盖拆分父社区中的少量社区记录；对这些父社区，个体只有父社区键，无法从已审 Community/PSU/个人文件恢复其子 PSU 归属。该更正没有改变设计门状态，但把阻断原因从“未做键结构核查”精确到“拆分社区缺少个人子区归属”。

候选方法和审查问题见 [`wave1_variance_estimator_decision_matrix_2026-10-29.md`](wave1_variance_estimator_decision_matrix_2026-10-29.md)。

## 官方来源

- [CHARLS 官方 2011 Wave1 (Baseline) 数据与文档清单](https://charls.pku.edu.cn/en/Data/a2011_CHARLS_Wave1__Baseline_.htm)：列出 Wave1文档和 All Data、PSU、Weight、Community、Blood等数据产品。
- [CHARLS 2011 National Baseline Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/CHARLS_nationalbaseline_users_guide.pdf)：社区PSU、分层抽样和大型社区拆分说明。
- [CHARLS 2018 Wave 4 User's Guide](https://charls.pku.edu.cn/en/data/User2018.pdf)：Sample_Info.dta 和 PSU 跨波说明；仅用于解释 Wave 4 文档列出的文件用途，不外推 Wave1变量。
- [CHARLS 2015 Wave 3 数据页](https://charls.pku.edu.cn/en/Data/a2015_CHARLS_Wave_3.htm) 与 [2018 Wave 4 数据页](https://charls.pku.edu.cn/en/Data/a2018_CHARLS_Wave_4.htm)：证明这些后续波次分别发布自己的 Sample Information，不能替代基线字段。

### Source-bound Wave 1 rebuild and component-key reconciliation (2026-10-29)

The current protected intake was rechecked with the metadata-only preflight. The four user-confirmed official Wave 1 files still match the reviewed local SHA-256 fingerprints and official document/source-page entries. The status is `verified_official_source`; this establishes byte/source identity, not the statistical design.

Using that manifest, the current repository preparation script rebuilt a fresh Wave 1 respondent table into a new versioned directory under the protected local CHARLS workspace. The previous prepared tables were left intact. The new table's manifest binds it to the reviewed four-file source set; the source-provenance gate accepts this versioned output. The aggregate-only reconciliation reads only IDs and community keys, writes no identifiers, and remains in the protected QA directory.

The rebuilt person frame has a unique nonmissing respondent ID. The 2011 Codebook's reported nonmissing count for `ind_weight_ad2` matches the National Baseline/Blood Guide target count at the aggregate level. The protected audit further confirms that the Weight file has a residual set of positive adjusted-weight IDs outside the respondent spine; their person-record disposition remains unresolved. All IDs in the released Blood file join to the person frame, and the positive `bloodweight` records align with the Blood Guide's reported complete-sample count. Exact component counts and key differences remain in private QA. This reconciles the published denominator totals at aggregate level, but not every target-person-to-demographic-row link.

### 2026-10-29 protected ID-only follow-up across All Data modules

To determine whether the residual positive-weight IDs were only artifacts/strays in `Weight.dta`, a new protected audit verified the source-bound Wave 1 frame and current official-file fingerprints, temporarily extracted the official All Data archive under the owner-only private root, and read only the `ID` column from each module plus `ID`/`ind_weight_ad2` from Weight. Every residual positive-weight ID occurred in at least one other All Data module, including individual health/work modules; the IDs and exact module-level counts remain in the local-only QA JSON. The temporary extracted archive was removed automatically when the audit ended. This rules out a simple “Weight-only ID” explanation, but module-key presence does not prove the person completed the target interview, had valid age/DOB data, was blood-eligible, or belongs in the analytic denominator. The frame/denominator gate remains partial and model readiness remains closed. Reproducible aggregate-only code: [`scripts/audit_2011_weight_ids_across_modules.py`](../scripts/audit_2011_weight_ids_across_modules.py).

The official Blood Data Users' Guide states that `bloodweight` adjusts for household and individual survey nonresponse plus nonparticipation in blood collection. Thus it is the source-supported starting weight for Wave 1 models with blood assay outcomes, subject to pair-specific exposure module completeness and age-domain review. It does not resolve the survey PSU/strata variance problem, nor does it justify applying this weight to every non-blood phenotype.

The official PSU community key also joins, but that does not provide the missing county-stage stratum/selection-unit fields or each respondent's final subcommunity PSU assignment. Therefore `sample_frame_and_denominators`, pair-specific module eligibility, `final_psu_mapping`, and `variance_method_review` remain open; formal model readiness remains `not_passed`.

The reproducible code is [`scripts/audit_2011_official_frame_reconciliation.py`](../scripts/audit_2011_official_frame_reconciliation.py). It requires the reviewed prepared-table provenance, limits raw reads to `ID`, `communityID`, `ind_weight_ad2`, and `bloodweight`, enforces protected-root paths, and emits aggregate-only private JSON. No questionnaire, exposure, or outcome values are read; it does not estimate associations.

