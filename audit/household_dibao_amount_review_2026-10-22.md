# 家户低保补助金额跨波映射审计（2026-10-22）

## 映射决定

新增候选概念 `household_dibao_assistance_amount_2011_2015`，覆盖2011、2013、2015三波家户过去一年收到的最低生活保障（Dibao）补助金额。来源字段按官方文件逐波指定：2011为 `household_income.gd001_c`；2013和2015为 `Household_Income.gd001`。字段单位均为过去一年家户收到的人民币金额。该概念是家户层社会保障/资源暴露候选，不是受访者个人收入，也不代表符合资格或实际受益人数。

## 波次解释与限制

- 2011问卷把是否收到低保的 `GD001`（1=Yes、2=No）和金额 `GD001_C`分开。只有按官方路由适用的金额记录可作金额分析；不能把2011门控项和金额组件混作同一变量，也不能将结构性缺失当作0。
- 2013、2015问卷的 `GD001` 直接问过去一年收到多少低保，并明确“不适用填0元”。两波代码本把字段列为数值金额。保留0值含义和波次问法，不将2011的二题结构强行覆盖到后两波。
- 金额由家户财务信息受访者报告，需在获准数据环境中核实主键、财务回答者链接、单位、极端值和特殊缺失代码。不得把家户金额复制到每位成员或微观数据加入公开网站。
- 代码本中的均值、范围和观测数不用于估计或样本量说明，本轮仅核对字段身份和测量设计；没有读取个人作答值，也没有拟合模型。

## 来源与复建

2011依据 `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` 和 `sources_official/CHARLS_2011_Codebook_extracted.txt`；2013、2015依据各波官方问卷与Codebook。逐波字段表为 `audit/household_dibao_amount_crosswalk_v1.csv`，由 `scripts/build_household_dibao_amount_crosswalk.py` 生成，并接入 `scripts/build_ep_atlas_metadata.py` 主流水线。该指标保留跨波候选身份，但最终合并前仍须按原问卷路由、非适用填零规则和家户调查设计确定分析口径。
