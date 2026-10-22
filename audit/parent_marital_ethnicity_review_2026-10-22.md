# CHARLS亲属婚姻与民族背景候选审计（2026-10-22）

## 本次核查

本轮按未连接字段清单核查 Parent 长表剩余的 `ca010`、`ca024_w3` 和 `ca024_w3_1`。依据官方逐波问卷与 Codebook 确认题目身份、适用关系和代码标签；没有读取个人作答值，也没有从代码本频数推断任何可分析样本量。

| 波次和字段 | 官方含义 | 目录决定 | 主要边界 |
|---|---|---|---|
| 2013 Parent `ca010` | 受访者父亲当前婚姻状态；问卷提示同居伴侣按已婚处理 | 新增单波父亲婚姻状态E候选 | 限 `parentID=1` 且 `ca003=1` 生父；不是受访者本人婚史，也不是回顾童年环境。保留1–7原类别。 |
| 2015 Parent `ca024_w3` | 亲属是否属于少数民族；问卷在亲生父亲段明确该题 | 分别新增受访者生父、生母两个E候选 | 关系按Parent长表 `parentID=1/2` 分开；只保留亲生父母，不把配偶父母、继亲/养亲等合并。保留1=是、2=否和结构性缺失。 |
| 2015 Parent `ca024_w3_1` | 若 `ca024_w3=1`，询问亲属所属少数民族类别 | 分别新增生父、生母两个有条件的名义类别E候选 | 仅适用于少数民族状态为是的相应亲生父母记录；代码为无序类别。Codebook类别样本频数不复制到网站或分析。 |

Codebook将族别代码4标为`Man`；目录忠实保留官方标签，不把它替换为其他译名。族别类别可能稀疏，任何建模前必须检查实际有效单元格和披露风险；本轮仅增加字段映射，没有派生个人级暴露、没有跨波合并，也没有把亲属长表记录数当成受访者样本数。

## 构建与验证

可复建脚本：`scripts/build_parent_marital_ethnicity_crosswalk.py`，已加入主目录流水线 `scripts/build_ep_atlas_metadata.py`。审计输出 `audit/parent_marital_ethnicity_crosswalk_v1.csv` 为5条“波次—字段—构念”映射、5个候选概念；同一来源字段 `ca024_w3` 和 `ca024_w3_1` 分别指向生父/生母概念，这是由关系筛选器区分的，不是重复字段。

正式分析前须在获批数据环境中以respondent ID联结主表并按亲属关系过滤；2013还需核对 `ca003=1`。需检查 Parent 表中受访者ID/parentID唯一性、亲属记录资格、问卷跳题、特殊缺失及可估计类别。不得在本次公共原型或协作者交接包中放入任何微观数据、亲属组合结果或小单元统计。

官方依据：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`、`CHARLS_2013_Codebook_extracted.txt`、`CHARLS_2015_Questionnaire_extracted.txt`、`CHARLS_2015_Codebook_extracted.txt`；CHARLS官方页面分别为[2013 Wave 2](https://charls.pku.edu.cn/en/Data/a2013_CHARLS_Wave2.htm)和[2015 Wave 3](https://charls.pku.edu.cn/en/Data/a2015_CHARLS_Wave_3.htm)。
