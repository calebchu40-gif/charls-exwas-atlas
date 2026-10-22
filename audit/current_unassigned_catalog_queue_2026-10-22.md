# 当前空 Concept ID 目录队列（2026-10-22）

本次直接读取 `site-prototype/dist/catalog.json` 最终目录快照，按每条目录记录的 `epcf` 角色和 `candidate_concept_ids` 字段统计。只评估目录记录是否连接到候选概念；这不等同于变量的科学有效性、分析许可或模型资格。

| 目录角色 | 目录行 | 空 Concept ID 行 | 空 ID 波次字段码 |
|---|---:|---:|---:|
| E（暴露候选） | 4,566 | 0 | 0 |
| P（表型候选） | 1,903 | 0 | 0 |
| C（协变量/测量元数据） | 911 | 717 | 522 |
| 合计 | 7,544 | 717 | 522 |

空 ID 的 C 类记录中，429 行分类为 `covariate candidate`，288 行分类为 `measurement metadata`。这些记录不参与 E/P 配对矩阵。E/P 的零空 ID 只表示已连接候选概念，不代表所有候选都已完成人工审定；每个概念仍受来源证据、路由、测量对象、值标签、波次口径、`DO NOT ANALYZE` 锁定以及调查设计闸门约束。网站目前不含已审定的关联结果，模型数为零。

本快照用于纠正 [`unassigned_catalog_series_review_v1.md`](unassigned_catalog_series_review_v1.md) 中过时的“当前待审队列”标题和计数。旧专题表格继续保留为审计历史，不应用于推断当前未映射数量。
