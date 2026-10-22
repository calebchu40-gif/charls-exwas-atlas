# 企业补充养老金缴费比例与DB待遇形式（2013/2015）审计（2026-10-21）

## 字段审定

企业补充养老金（问卷FN030后续）包含两个值得区分的未覆盖指标：

- `fn035_w2_2`：受访者自付比例。问卷先问本人和单位的“合计月缴费”，再问其中本人支付百分比，代码本定义为`Percentage of Self Pay`，问卷范围0–100。因此概念定义为“个人占合计月缴费的比例”，分母不是工资，不能与2018个人缴费占工资比例互换。只在2013、2015字段映射中出现；题目在非当前领取待遇的计划参与者路径中。
- `fn036_w2_1/_2/_3`：预期待遇形式分别为月金额（元/月）、月待遇百分比（百分比含义/分母未写清）及一次性金额（元）。根据FN030参与状态、FN032=1 DB计划路由回答；只将三个有明确单位/形式的数值子项映射到三个独立Concept ID，不合并货币与百分比、不推算比例的分母。
- `fn036_w2`父项：其代码本答案类别是1=月金额、2=月百分比、3=一次性金额，属于响应形式选择，不是待遇数值；在2013、2015均作为C类施测元数据排除出E/P配对。实际数值只在`fn036_w2_1/_2/_3`中。

## 官方来源

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`：FN030补充养老金的参加/领取路由、FN032定义型/缴费型计划、FN033–FN040跳题；FN035合计月缴费及本人比例；FN036定义给付计划待遇形式。
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`：相同字段和范围限制。
- `sources_official/CHARLS_2013_Codebook_extracted.txt`、`sources_official/CHARLS_2015_Codebook_extracted.txt`：`fn035_w2_2`自付比例、FN036三类子字段及其单位。

映射代码位于`build_pension_exposure_crosswalk.py`；父项C类转换由`catalog_role_override_review_v1.csv`、`measurement_protocol_crosswalk_v1.csv`及`apply_catalog_role_overrides.py`维护。代码本频数不用于样本量或分析证据，未读取个人级记录。
