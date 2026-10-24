# 婚姻史事件日期字段复核

更新：2026-10-24。对 2011 `BE007`/`BE008` 和 2013 `BE009_1`/`BE009_2` 逐字段检查了官方问卷与 Codebook。按波次分别映射为首次婚姻结束年份、首次婚姻结束原因、最近一次婚姻年份和月份四个 E 候选来源字段。它们是回顾性生命历程事件，不能替代当波婚姻状态。字段保留原波次、模块、题目路线和官方来源；日期字段不制造类别标签，2011 `BE008`只显示问卷支持的配偶去世/离婚类别，2013 月份字段保留 `0=Do not remember`，不把 0 当成一月或缺失。

2013 最近婚姻日期字段受婚姻史回访路线和访谈类型限制；2011 首次婚姻信息受婚姻史回答路径限制。详细分母和授权发行版特殊值仍需在实际分析前验证。相关 C 检索记录也保留为背景候选，但若该字段是目标暴露本身，不得把它当作自身的调整变量。它们不构成固定协变量集合。

2015 问卷表明 `BE009` 仅在 `BE003_W2_1 > 0` 时询问，但 2015 官方 Codebook 对两个组成字段均标注 `No Observations`。因此本项目不将 2015 `BE009_1`/`BE009_2` 映射成 E 暴露，不把 Codebook 摘要解释成实际发行数据必然无值；字段保留为来源可用性与路由元数据，需获准发行版 QA 后再决定其分析角色。

可复现映射：`audit/marital_history_exposure_crosswalk_v1.csv` 与 `scripts/build_marital_history_exposure_crosswalk.py`。C/E 重叠更新器为 `scripts/apply_marital_history_c_overlap_review.py` 与 `scripts/apply_marital_history_exposure_source_review.py`；2015 无观测边界见 `audit/marriage_date_2015_no_observation_review_v1.csv` 和 `scripts/apply_2015_marriage_date_no_observation_review.py`。未读取个人记录或 Codebook 频数。新增四个概念使 E/P 概念总数增至 1,449；当前 E/P 元数据候选组合数随之更新，但不是有效样本量或关联结果。
