# 2015 FN068养老金资格/家庭支持题与Codebook字段对应关系复核更正（2026-10-22）

> **撤销此前“问卷没有FN068_W3题号”的结论。**该结论只检查了较早页面。CHARLS官方2015 Wave 3问卷第180页明确列出FN068_W3、第185页继续列出该题及两个追问；官方PDF的可检索文本和本地问卷摘录均能定位题干。此前把这些字段全部排除在E/P之外的判断不成立。

官方问卷第185页的FN068_W3询问在村/社区最初开展所选居民类养老金时，受访者是否已经达到领取年龄并能直接领取、自己无需缴费（不包括子女缴费）；FN068_W3_1询问当地是否要求子女也参保，受访者才能免本人缴费并直接领取；FN068_W3_2询问哪些子女按当地要求开始缴费。Codebook相应列出按新农保、城乡居民、城镇居民养老金分列的“Received and Not Payment”“Not Personal Payment”以及“Payment by Who”字段。

## 当前处理

- `fn068_w3_1`、`fn068_w3_2`、`fn068_w3_3`：作为三个计划路线下“初次开展时达到年龄并直接领取、无需本人缴费”E候选；此处“无需本人缴费”明确排除子女缴费。
- `fn068_w3_1_1_`、`fn068_w3_1_2_`、`fn068_w3_1_3_`：作为“当地是否要求子女参保后受访者可免本人缴费”E候选；保留计划上下文和历史情景。
- `fn068_w3_2_1_s1/s2`、`fn068_w3_2_2_s1/s2`、`fn068_w3_2_3_s1/s2`：是“哪些子女缴费”问题的家属名册选项槽位，保留为C类家属名册选择元数据，不公开或单独关联子女身份槽位。

所有变量均为2015 Wave 3的历史计划实施情境，不等于当前养老金领取、当前个人缴费或缴费金额。题目路由、结构性缺失及计划种类必须保留。Codebook频数不转录为网站样本量；没有读取受访者微观记录。

## 官方依据

- `sources_official/CHARLS_2015_Questionnaire.pdf`：印刷页185的FN068_W3/W3_1/W3_2题干和选项。
- `sources_official/CHARLS_2015_Codebook_extracted.txt`：FN068按计划拆分的状态、子女代缴槽位字段。
- CHARLS官方2015 Wave 3数据文档页：https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html

映射逻辑在 `scripts/build_pension_exposure_crosswalk.py`，角色与名单槽位规则在 `audit/catalog_role_override_review_v1.csv`、`scripts/apply_catalog_role_overrides.py`。
