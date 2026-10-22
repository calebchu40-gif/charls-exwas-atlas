# 2013/2015当前主要住房市场估值字段复核（2026-10-22）

## 字段身份与测量单位

2013及2015官方问卷`HA011`询问当前住房的市场价值；若受访者不知道自家房屋市场价，可按问卷提示报告附近类似住房。`HA011`是回答单位选择器：1=总价，单位为万元；2=单位面积价格，单位为千元/平方米。数值分别存于`ha011_1`和`ha011_2`。因此两个数值字段映射到两个不同候选概念，保留各自单位，不换算、不合并；父字段`ha011`改列C类测量格式元数据。

2015问卷明确`HA007=3`时跳过HA011/HA012；两波均需保留字段适用路由与拒答/特殊缺失代码。该指标是家庭报告的当前住房估价或附近类似住房估价，不等同于受访者个人名下财富。可分析样本和特殊缺失编码仍需用实际获批发行数据字典核实。

## 单独保留的其他住房估值题

本轮未将`ha023_1/_2`（曾经取得的新住房当时估价）、`ha034_*`（多个住房/家庭成员槽位）或`ha012_bracket_min/max`（无法直接报告精确数值时的区间追问）混入当前主要住房概念。它们的资产对象、时间点、槽位/路由或区间端点含义不同，应另行核对后再决定是否映射；区间端点不能直接作为连续精确市值。

## 来源与实现

官方来源：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`及对应Codebook、`sources_official/CHARLS_2015_Questionnaire_extracted.txt`及对应Codebook。金额候选写入`scripts/build_household_asset_exposure_crosswalk.py`，精确波次selector角色修正在`audit/catalog_role_override_review_v1.csv`中登记，并由`scripts/apply_catalog_role_overrides.py`标为C类；值单位及问卷来源写入`audit/measurement_protocol_crosswalk_v1.csv`。未读取个体回答或代码本频数作为样本数。
