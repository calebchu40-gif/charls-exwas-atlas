# 历史户籍/居住关系 C/E 重叠字段同步（2026-10-25）

将7条精确波次 C 角色行链接至已来源审阅的 `social_context_remainder_crosswalk_v1.csv` 暴露候选：2011/2013 `BC011`、2011/2013 `BC013`、2011 `BC014`，以及2015/2018 的 `BC001_W3_2`。更新器同时核对每一行的 E/C 角色、精确模块键和官方问卷、Codebook 文件。

这些是历史户籍位置关系、变迁原因或上一轮户籍类别，多个题项只在满足回顾史/返访路由时提问。更新保留逐波参照类别和问卷路由；不将历史类别当作当前户籍、环境污染剂量或自动调整建议。目标字段自身不得作为模型的调整变量。

字段级表见 [`hukou_history_c_overlap_review_v1.csv`](hukou_history_c_overlap_review_v1.csv)，逐波路由与响应类别见 [`social_context_remainder_crosswalk_v1.csv`](social_context_remainder_crosswalk_v1.csv)。未读取参与者记录、代码本频数或权重，也未拟合关联模型。
