# 2011–2018 受访者性别来源与派生字段复核

更新：2026-10-24。逐字段核对 2011、2013、2015、2018 官方问卷和 Codebook，并参考 CHARLS 网站托管的 Harmonized CHARLS Documentation Version D 中性别 QA 规则。没有使用或披露个体记录、代码本频数或关联结果。

## 复核结论

对 9 条模块限定的 C 记录分别记录字段含义和来源：2011 `rgender`；2013/2015/2018 `ba000_w2_3` 访员记录输入；2013/2015 `xrgender`；2018 两个模块中的 `xrgender`；以及 2018 `zfrgender`。问卷和 Codebook 支持受访者性别响应的 `1=Male; 2=Female` 标签，网站仅展示标签、不复制频数。

这些字段不能视为多个独立的受访者性别测量。`ba000_w2_3` 是访员记录/预载输入，不能无条件代替发布的 `xrgender`。2018 问卷说明了按访谈类型和前波信息更新 `XRGender` 的路由，并在其他路径沿用 `ZRGender`；`ZFRGender` 因而作为前波路由参考元数据保留，不推断其分类含义或当波性别值。2018 `xrgender` 在人口背景和健康功能模块各出现一次；目录按模块分别保留，但标注为重复来源记录，不能计成两项测量。

Harmonized CHARLS Documentation Version D 描述前四波跨人口、健康/居住模块报告形成统一性别变量及其方法标志。本项目把它作为 QA 参考，不将第三方 `RAGENDER/RAFGENDR` 冒称 CHARLS 原始变量，也没有据此改写本目录的原始字段。每个波次仍需在获准发行版核对生成版本、模块冲突、缺失和目标样本。C 类条目只是字段目录；不代表固定调整集或每一模型均应纳入性别。

可复现更新器：`scripts/apply_gender_source_derivation_review.py`，已加入全量与 finalize-only 元数据流程。模块限定字段清单：`audit/respondent_gender_source_derivation_crosswalk_2011_2018_v1.csv`。原协变量就绪审计：[`official_age_gender_harmonization_review_2026-10-23.md`](official_age_gender_harmonization_review_2026-10-23.md)；模块身份边界：[`module_qualified_source_identity_review_2026-10-22.md`](module_qualified_source_identity_review_2026-10-22.md)。
