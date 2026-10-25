# 居住地聚落类型 C/E 重叠字段同步（2026-10-25）

本批同步两条与 E 角色精确重合的 C 字段：2015 `BB001_W3_2` 与2020 `BA008`，对应 `residential_settlement_type`。字段均限定到确切波次、字段及模块，并要求官方问卷和 Codebook 文件可用。

这代表居住地址环境，不是户籍登记类别，也不是已测量的环境污染物。2015包含七类、2020包含四类；问卷描述和地址时间范围需按波次保留，不能用数值码直接跨波合并。任何城乡归并都应预先定义并报告理由。C角色用于查找来源与测量信息，既不是默认调整变量，也不能用于调整这个字段自身的暴露效应。

字段级记录见 [`residential_settlement_c_overlap_review_v1.csv`](residential_settlement_c_overlap_review_v1.csv)，来源定义见 [`residential_settlement_exposure_crosswalk_v1.csv`](residential_settlement_exposure_crosswalk_v1.csv)。本次未读取参与者记录、代码本频数或权重，也未拟合关联模型。
