# 孤独条目的暴露角色补充审核（2026-10-17）

CHARLS 孤独条目已作为心理健康表型进入目录。本次结合用户提出的 ExWAS“可双向检索”需求，将既有两个孤独概念增加一个暴露角色：`mood_lonely`（2011/2013/2015/2018/2020 CES-D孤独条目）和 `affect_lonely_yesterday`（2013昨日情绪题）。这不是新建同义指标：两个概念 ID 与 P目录保持相同，角色标为E/P双角色；原始代码与既有逐波标签不变。

新增暴露角色映射预计6条：`mood_lonely` 5个波次字段（2011–2020逐波）及`affect_lonely_yesterday`的2013 `wb08`。CES-D“过去一周孤独频率”与“昨天孤独程度”的题干和取值尺度不同，因此保留两个概念，不作跨题/跨波统一计分。

## 方法边界

孤独是主观社会/心理状态，可作为后续健康结局的候选暴露；同一条目也可作为心理健康表型。作为暴露使用时，不应把条目与自身或包含该条目的总分作关联，也不能把同波横断关联解读成时间先后或因果。候选角色扩展只改变检索/分析设计选择，不等于已审定模型可用性；仍需遵循CHARLS官方代码本的特殊缺失、调查权重和纵向设计要求。

本轮使用已审核的问卷/代码本标签，不读取个人级回答；没有计算孤独比例、估计关联或生成关联结果。

## 重现文件

- 源生成脚本：`scripts/build_loneliness_exposure_role_crosswalk.py`
- E侧角色映射：`audit/loneliness_exposure_role_mapping_v1.csv`
- P侧既有映射：`audit/mood_item_variable_mapping_v1.csv`
- 总目录构建：`python scripts/build_ep_atlas_metadata.py`
