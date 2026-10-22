# 进食、家务与备餐帮助字段复核（2026-10-17）

## 决定

在“社交与家庭联系”候选目录中新增三个条件性照护支持概念：`informal_help_eating`、`informal_help_household_chores`、`informal_help_meal_preparation`。三者覆盖2013、2015、2018波中DB012_W2、DB016_W2、DB017_W2。值码为1=Yes、2=No。它们都在相应ADL/IADL困难题之后询问，表示调查记录中有人帮助，不是对所有受访者调查的社会照护覆盖率，也不等同正式照护服务利用。

## 题目与路由

| 概念 | 字段/波次 | 官方问卷题意与适用限制 |
|---|---|---|
| 进食帮助 | `db012_w2`，2013/2015/2018 | “是否有人帮助进食”。若没有进食困难，前置题跳过帮助项；仅在报告有进食困难者中观察。 |
| 家务帮助 | `db016_w2`，2013/2015/2018 | 2013/2015问卷明确为“是否有人帮助做家务”；2018也是家务帮助。只在报告家务困难者中追问。**冲突：2013/2015官方codebook把`db016_w2`字段标签写成“是否有人帮助准备热餐”，与问卷DB016_W2题干冲突。字段映射保留但标为DO NOT ANALYZE，须先核对所用发布版本/变量别名。** |
| 备餐帮助 | `db017_w2`，2013/2015/2018 | “是否有人帮助准备热餐”。只在报告备餐困难者中追问；2013与2018问卷还规定养老院居住者跳过该追问。 |

2020问卷中的DB017_W2语义是是否有人帮助购物（不是备餐）；未将其映射到以上任一概念。2011相关字段结构也未确认与这些后续波次帮助题等价，故不补推。缺失、结构性跳题、未进入辅助模块和明确回答“No”必须分开。

## 来源证据

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`：DB012_W2问是否有人帮助进食；DB016_W2原文问是否帮助做家务；DB017_W2问是否帮助准备热餐，并有养老院跳题。
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`：DB016_W2及DB017_W2分别问家务帮助和备餐帮助，支持对2013/2015 codebook标签冲突的发现。
- `sources_official/CHARLS_2018_Questionnaire_extracted.txt`：DB012_W2进食帮助、DB016_W2家务帮助、DB017_W2备餐帮助及相应功能困难前置题/路由。
- `sources_official/CHARLS_2013_Codebook_extracted.txt`、`sources_official/CHARLS_2015_Codebook_extracted.txt`、`sources_official/CHARLS_2018_Codebook_extracted.txt`：字段存在及1=Yes、2=No答案标签；尤其2013/2015 DB016_W2变量标签与同波问卷题干不同。

## 分析限制

这些字段是有条件的帮助暴露候选，不应把前置困难字段作为常规协变量后不加说明地“控制掉”其目标构念，也不得将未问/跳题编码为无帮助。分析前需核对原始文件目标受访者、代理回答限制、居住机构路由、特殊缺失值和波次问卷版本；并定义适用分母。对`db016_w2`的2013/2015映射，在官方变量别名冲突解决前不得建模。当前只使用字段目录、公开问卷和codebook，没有读取个人级记录或计算样本数。

复现脚本：`scripts/build_social_exposure_crosswalk.py`；总目录构建：`scripts/build_ep_atlas_metadata.py`。检索JSON：`site-prototype/dist/social_exposures_v1.json`；字段审计表：`audit/social_exposure_crosswalk_v1.csv`。

