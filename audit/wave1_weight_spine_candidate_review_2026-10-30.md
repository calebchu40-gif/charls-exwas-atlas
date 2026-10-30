# Wave 1 权重样本框候选复核

**日期：**2026-10-30
**状态：**候选准备表已重建；样本框与设计尚未获得最终方法审查批准。
**隐私：**个体数据、ID 和精确逐人链接仅保存在受控本机目录；本记录只写公开文档支持的总体数和方法结论。

## 官方依据

CHARLS 官方 Codebook 将 Wave 1 `IND_WEIGHT_AD2` 定义为经过 household 与 individual non-response adjustment 的个人权重，并报告 `R1WTRESPB` 的非缺失描述统计 N 为 17,708；Codebook 说明个人权重在该受访者没有完成相应波次访谈时设为普通缺失。Wave 1 Blood Users' Guide 同样报告成功访谈 17,708 人，并将基线血检目标定义为主受访者和配偶。由此，按官方 `ind_weight_ad2` 为正的个人 ID 构建“已完成访谈候选框”有明确来源依据，较只用 `Demographic_Background` 模块行作框更能复现官方总访谈数。

官方资料：

- [CHARLS Codebook](https://charls.pku.edu.cn/en/team/Codebook.pdf)，Section A，个人权重及构造说明。
- [CHARLS 2011 National Baseline Users' Guide](https://charls.pku.edu.cn/en/data/User2011.pdf)，Wave 1 访谈和抽样设计说明。
- [CHARLS 2011 Blood Sample Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)，血检目标、样本量及 `bloodweight` 构造。

## 受控重建与校验

- 新的 Wave 1 候选准备表以官方 `Weight.dta` 中 `ind_weight_ad2 > 0` 的 ID 作 spine，并将其他模块左连接；它是独立输出，不覆盖原有以 `Demographic_Background` 为 spine 的准备表。
- 候选表共 17,708 行、17,708 个唯一 ID；`ind_weight_ad2` 无缺失或非正值。人数与官方 Codebook 和两份 Wave 1 指南公布的访谈总数一致。
- `Demographic_Background` 仍以左连接方式加入。官方个人主表缺行的少量权重样本保留在候选框中，其人口学字段保持缺失；不从健康、工作或家庭模块推补人口学变量。
- 11,847 条官方 Blood 记录全部各自匹配候选框一次；候选表中的 `bloodweight` 与原始 Blood 文件逐 ID 完全一致。此核验只读取 ID 和权重，不读取任何血液检测值。
- `bloodweight` 的正式来源是独立 Wave 1 Blood 文件；`Weight.dta` 中的 `bio_weight2` 不作为本项目该血检分析权重。此前对 `bio_weight2` 的额外比对不是适用权重检查，不能拿它否决 Blood 链接。

完整候选表、输入/输出 manifest 和 merge QA 仅位于 `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\derived_wave_tables_2011_weight_spine_candidate_20261030`。

## 结论及未通过门禁

这次重建把官方总访谈人数和已发布权重口径对齐，也证明原先的小规模分母差异来自个人主表的覆盖不足，而非 Blood ID 或 `bloodweight` 链接丢失。候选表为进一步方法审查提供了更完整的 Wave 1 respondent spine，但在独立审查批准其作为冻结分析框之前，不能替换已登记的准备表，也不能拟合关联模型。

仍需通过：

1. 独立审查确认正 `ind_weight_ad2` 的 Wave 1 完访样本框定义、主受访者/配偶身份及与目标估计量一致；
2. 对个人主表缺行者保留年龄/协变量缺失并核实其进入各具体暴露/结局模块时的适用性；
3. 冻结血检配对采用 `bloodweight` 的目标、年龄域及缺失/非应答规则；
4. Wave 1 最终 PSU、隐式分层及方差估计方案仍没有获批的完整设计规格；
5. 既有 105 项试点的冻结方案、血糖空腹代码与结局过滤仍需复核。

因此正式 CHARLS 关联模型仍为 0；本次只重建了候选样本表并核验样本键和权重。
