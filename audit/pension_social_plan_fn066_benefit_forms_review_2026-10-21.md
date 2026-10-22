# 社会养老金FN066预期待遇形式与计划专属金额复核（2013/2015）

## 复核结论

按2013/2015代码本，FN066的按月待遇与一次性待遇不能共用同一构念。字段按计划类别、待遇形式与波次分别整理：

- 2013农村养老金：`fn066_w2_1_1_`月额、`fn066_w2_2_1_`一次性额。
- 2015新农保：相应同后缀变量分别列月额、一次性额；代码本明确波次标签为New Rural Pension。为避免未经证实地把“Rural”与“New Rural”强行视为完全同构，两个波次保持不同Concept ID。
- 居民养老金：`fn066_w2_1_2_`/`fn066_w2_2_2_`分别为月额/一次性额；城镇居民养老金：`fn066_w2_1_3_`/`fn066_w2_2_3_`分别为月额/一次性额。按计划分别保留，不跨计划合并。
- 各计划前置父字段`fn066_w2_1_`、`fn066_w2_2_`、`fn066_w2_3_`选择月额或一次性额，已转C类测量格式元数据；金额仅在子项，不参与配对。

上述字段处于FN060–FN066社会养老金缴费/待遇题组。问卷有不同计划参保、既往缴费及转入计划提示和跳题路径，真实分析分母须按波次问卷核定。一次性金额不能年化，未被选中的支付形式不得按0处理。

## 官方依据

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`：FN060–FN066题组路由及月/一次性待遇提问。
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`：FN058路由与FN060–FN066题组；待遇形式提问。
- `sources_official/CHARLS_2013_Codebook_extracted.txt`、`sources_official/CHARLS_2015_Codebook_extracted.txt`：按方案分别定义父选择器和月额/一次性金额子项、单位标签。

映射规则在`build_pension_exposure_crosswalk.py`；C类父项由`measurement_protocol_crosswalk_v1.csv`、`catalog_role_override_review_v1.csv`和`apply_catalog_role_overrides.py`维护。本审计仅使用公开问卷/代码本，不读取个人级记录；代码本发布的频数未用于估算分析样本量。
