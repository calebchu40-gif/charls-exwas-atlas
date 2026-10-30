# Wave 1 `bloodweight` 与 `bio_weight2` 权重语义核对

**日期：**2026-10-30  
**状态：**来源语义已厘清；估计量及设计准入仍待审阅。  
**范围：**官方字段文档与服务器私有键覆盖诊断；不公开记录级数据或精确 QA 细节。

## 结论

Wave 1 Blood 文件中的 `bloodweight` 与 Wave 1 Weight 文件中的 `bio_weight2` 是两个不同字段，不能要求逐行数值相等，也不能用 `bio_weight2` 的记录覆盖来替代 Blood 样本权重准入。

- Blood Users' Guide 的 sample-weight 章节说明：因基线调查及血液采集未应答，CHARLS 构造并在数据中提供名为 `bloodweight` 的权重；该权重从基线个人权重出发，并校正血液采集未参与。
- CHARLS 2011 CodeBook 的 Weight 章节将 `bio_weight2` 定义为“Biomarker Weight with Household and Individual Non-response Adjustment”。它没有在字段名/标签中说明其校正血液采集未参与。
- 服务器受控元数据复核显示，Blood 文件 `bloodweight` 标签为 “Blood Weight with Household and Individual Response Adjustment”；Weight 文件另有 `bio_weight1`、`bio_weight2` 与 `ind_weight_ad2`。私有键对账显示两个权重字段的可用记录覆盖不同。此差异符合字段定义不同，**不是**需要把 Blood 样本按 `bio_weight2` 删除或判为权重错配的理由。具体覆盖 QA 仅在服务器 private/。

因此，Wave 1 血液表型分析的候选权重应直接使用 Blood 文件自身的 `bloodweight`，并从实际观测 Blood 记录构造设计数据；不要将不同的 Weight 模块字段当作其替代变量。官方目标人数、Person ID 表记录数与 Blood 观察样本数仍分别记录，不能通过扩展/填补记录数来“对齐”。此前对两种不同权重字段作相等性比较只是一项诊断，不构成权重选择依据；正式候选仍需在独立审阅中确认该权重对所定义的45+ domain及配对完整案例估计量是否适用。

## 准入边界

这项来源语义核对只解决“血液样本权重字段取自哪里”，不证明 Option A 近似方差充分，不解决官方 PSUs/分层缺失，也不通过年龄 domain、完整案例选择、非应答、结局测量规则或披露审查。此前记录的总体/Person ID 分母差异继续作为未解决的样本框对账限制；模型门仍关闭。

本轮未读取结局取值、未拟合关联、未把记录级数据或确切键覆盖 QA 上传 GitHub。受控服务器只保存汇总 QA。

## 官方来源

- CHARLS, *2011 Blood Data Users' Guide*, “Sampling and Sample Weights” section: [`sources_official/CHARLS_2011_Blood_User_Guide.pdf`](../sources_official/CHARLS_2011_Blood_User_Guide.pdf) 与可检索文本。
- CHARLS, *2011 CodeBook*, Section 14 “WEIGHT,” `bio_weight2` 标签和描述: [`audit/CHARLS_2011_Codebook_extracted.txt`](CHARLS_2011_Codebook_extracted.txt)。
