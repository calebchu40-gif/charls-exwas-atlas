# 2018 成人教育年限 E/C 重叠字段复核

更新：2026-10-24。依据 2018 官方问卷和 Codebook 审核 `BD008_W2_1` 与 `BD008_W4_1`。两者都是年限连续字段，没有离散类别标签。`BD008_W2_1`询问成人教育总年限；`BD008_W4_1`明确询问从 `ZIWTime` 以来的年限。两者前置 `BD007` 成人教育多选题含 `None` 选项并跳过后续路线，因此缺失的年限回答不能自动当作 0。

两字段仍作为同一成人教育年限概念下不同来源路线的 E 候选，保留为 C 记录的部分原因是它们可能在其他估计目标中承担背景角色。它们不是通用调整变量：目标暴露为该字段时不得用该字段调整，且需保留问卷路线及时间窗。`W2_1` 与 `W4_1` 的时间参照不同，不把原始年数直接合并。

更新器：`scripts/apply_2018_adult_education_c_overlap_review.py`，并已加入全量与 finalize-only 构建流程。交叉表构建器已补充精确路由说明：`scripts/build_adult_education_training_crosswalk.py`。机器可读审核记录：`audit/adult_education_c_overlap_review_2018_v1.csv`。此审核没有使用个人记录或 Codebook 频数；它把 C 类通用待审计数从 25 降到 23。
