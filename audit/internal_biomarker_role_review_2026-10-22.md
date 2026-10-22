# 内部生物标志物自动E/P角色边界复核（2026-10-22）

## 复核问题

宽目录`charls_atlas_candidate_fields_v0.csv`有自动发现标签“internal biomarker / dual role requires review”。这层是NHANES式字段搜索目录的候选分组，并不自动生成E/P模型映射。审阅发现类别中共20个concept候选：13个2011血检分析物字段、7个2011–2015体格/生命体征概念（血压、脉搏、腰围、身高、膝高、步速）。它们在`ep_concept_source_crosswalk_v1.csv`的经审查映射角色均为P，尚无经审查E来源链接。

另有波次口径不一致：2011血检位于`Blood_Assays`，因此其中13项触发自动internal-biomarker E/P搜索角色；2015血检位于独立`Blood_Data_2015_Independent_Release`模块，没有触发相同自动角色，即使官方发布说明确认有相同分析物。因此自动类别覆盖差异反映模块名/发现规则，不代表实际测量模块或研究价值不同。

## 处理规则

- 保留自动双角色标签作为目录人工复核入口，但其状态仍是“自动发现，待审”；不能据此认定已映射为暴露或直接进入ExWAS。
- 公开E/P概念来源crosswalk继续只以已审证据连接血液指标到P角色。若将内部生物标志物当E，须针对研究目标预先给出时间顺序/生物学解释和相应人群/权重方案；横断面配对只解释为非方向性关联。每一Concept不得与自身配对。
- 血检专题页说明内部临床指标与外部环境化学暴露的区别，并指出宽目录自动标签和已审crosswalk角色的差异；字段JSON显示逐项角色边界。
- 血液指标跨波校准限制、2011胱抑素C抽样权重闸门见[`blood_biomarker_definition_review_v1.md`](blood_biomarker_definition_review_v1.md)。

本轮未改变E/P已审概念映射数、未生成任何模型，也未读取个人血检值。
