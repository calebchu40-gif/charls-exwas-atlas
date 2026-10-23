# 养老金连续/计数字段代码本定位状态同步（2026-10-23）

本轮将官方代码本中已定位、但没有离散响应类别可转录的养老金字段状态传播至主目录和网站。输入为 [`pension_codebook_value_labels_v1.csv`](pension_codebook_value_labels_v1.csv)，由 `scripts/build_pension_codebook_value_labels.py` 从对应波次官方CHARLS代码本提取；主目录更新由 `scripts/build_charls_atlas_catalog.py` 完成，并通过完整元数据流水线生成最终站点目录。

源审核表共有614个波次—字段条目符合“`official codebook field located; continuous/count or no categorical labels`”且没有类别标签。最终主目录中608个条目显示该专门状态；另外6个2018字段已有更具体的已审状态，因此保留原状态：`fn033_w2`、`fn056_w2_8`、`fn066_w2_1`、`fn066_w2_2`、`fn105_w4_1`、`fn105_w4_2`。脚本仅更新值标签为空且原审核状态为空或通用`not yet reviewed`的条目；不会覆盖现有审定状态、值标签或分析锁。

网站中文说明为：**官方代码本已找到该字段但未列离散类别；数值/计数含义、单位和路由仍需结合问卷核对**。该状态只说明代码本字段定位完成，不证明发行数据编码、计量单位、特殊值、跳题路线、跨波可比性或分析资格已核实；也不表示该字段应强行补造类别标签。

本轮只处理公开官方代码本和字段元数据，没有读取或发布CHARLS个人记录，也没有拟合关联模型。验证包括完整元数据流水线、59项测试，以及33条`DO NOT ANALYZE`锁定清单逐字段校验。
