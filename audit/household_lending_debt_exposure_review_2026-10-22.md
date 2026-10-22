# 家户借出款、利息收入与非抵押负债字段审计（2026-10-22）

本轮按官方2011基线家户问卷、2013/2015问卷和对应Codebook核对HA069–HA073。没有读取受访者记录，也没有使用或转录Codebook中的频数、金额分布或观测数。映射由`scripts/build_household_lending_debt_crosswalk.py`生成，当前字段交叉表为`audit/household_lending_debt_crosswalk_v1.csv`。

## E候选构念

2011与2013 HA069–HA072题意可分为四个家户层候选概念：

- HA069：家户是否有借给其他家庭或个人、截至调查时仍未收回的款项；保留官方Yes/No响应，不从空白推断否。
- HA070：仅在HA069=Yes路线下报告的未收回借款总额（元）；属于家户应收款本金，不能与利息收入混为一项。
- HA071：家户过去一年从借出款项取得的利息收入（元）。HA069=No会跳至HA071，故该指标不应限定为当前仍有未收回借款的家户。
- HA072：家户当前欠其他家庭、个人或工作单位的负债总额（元），问卷明确排除抵押贷款；与受访者个人负债、金融机构贷款、房贷余额或净财富概念分开。

四个概念只在2011与2013建立跨波链接；2015 Codebook将HA069–HA072均列为“No Observations”，在网站目录保留为C类停用字段，不当作零、无债或可分析缺失值。未假设2018存在同题字段。

## HA072无精确金额时的处理

2011和2013问卷说明：如果受访者无法或不愿回答HA072精确金额，转问HA073展开式区间题。2011发布字段为`ha073_1`–`ha073_6`阈值组件，Codebook将最后一个阈值字段列为No Observations；2013字段为`ha073_bracket_min`及`ha073_bracket_max`。这些组件在目录中列作C类回答协议元数据，不当作精确债务数额、独立暴露或可直接等价的跨波指标；不取区间中点，也不把未回答改为零。未来若要利用区间信息，须先根据获准发行版字典确认组件存储和值码，再预先规定区间删失/敏感性分析方案。

## 数据层级、路由和分析门槛

上述金额是家户财务题组回答，不是主要受访者个人资产/债务，也不能与2011 household-member长表的金融资产、未偿银行贷款相加。HA070受HA069肯定路线限制；HA071的参考期为过去一年；HA072为当前存量且排除抵押贷款。金额值、特殊缺失、零值、权重和实际有效分母须在获准取得的数据发行版本上另行核实。概念映射表示可检索候选，不表示已经通过分析资格审查。

## 官方来源

- 2011：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`（HA069–HA073）及`audit/CHARLS_2011_Codebook_extracted.txt`。
- 2013：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`（HA069–HA073）及`sources_official/CHARLS_2013_Codebook_extracted.txt`。
- 2015：`sources_official/CHARLS_2015_Codebook_extracted.txt`（HA069–HA072 No Observations）。

站点只显示字段身份、单位、候选概念和路由限制；不显示个体记录或Codebook描述统计。
