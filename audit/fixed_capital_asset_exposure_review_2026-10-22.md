# 农用固定资产与其他生产性资产字段审计（2026-10-22）

本轮按各波官方 Household Income / Assets 问卷与 Codebook 核对 HA066–HA068。没有读取受访者记录，也没有抄录或使用 Codebook 附带的频数、均值、最小值、最大值或观测数。字段级映射由 `scripts/build_household_asset_exposure_crosswalk.py` 生成，纳入 `audit/household_asset_exposure_mapping_v1.csv` 与概念摘要。

## 可纳入的候选字段

- HA066 固定资本资产清单：拖拉机、脱粒机、2011–2015的机引农具、抽水机/水泵、加工机械；2018问卷改列拖拉机、脱粒机、收割机、抽水机/水泵、加工机械、播种机、农用飞机及“以上皆无”。清单所有权选择项与每类资产的当前估值分开映射。2018农用飞机估值明确以万元记录，其余估值以元记录。
- HA067 生产或自营活动中其他固定资本的当前估值：问卷指示不要重复计入HA066已报项目。2018题目明确问主要受访者及配偶的非农用固定资本，并举店铺、厂房、仓库等经营性房产为例；因此2018字段不与早期家户口径直接合并。
- HA068 其他价值至少500元的耐用品或固定资产：状态和金额分别映射。金额受“Yes”路径限制，不能把No、未答、不知道或拒答改成0。

## 跨波边界

2011与2013 HA066使用家户成员口径；2015改为“您和配偶”；2018明确限定为主要受访者及配偶，并在资产与他人共有时只计两人所拥有的部分。相应所有权与估值概念按口径拆开，不将 household、couple、couple-owned-share 概念强行合并。2011–2015选项式清单的未选/空白不等于“No”；2018逐项变量以0表示“No”、资产项编号表示“Yes”，且 none-of-list 项号也随波次变化（早期为6，2018为8）。

HA067的2018题目新增了“非农用固定资产”的明确范围；HA068则明确排除前面已列资产。上述题目虽可作为物质资源/家庭经济环境候选暴露检索，但它们不构成个人所有权证明，也不能通过跨项求和直接构造净财富。

## 排除与分析门槛

2015 Codebook 将 `ha066_1` 父项及 `ha066_1_6_`“每项资产面值”格式字段列为无观测项，不生成候选指标；本映射仅使用有具体资产身份的 `ha066_1_1_` 至 `ha066_1_5_` 与所有权清单字段。连续估值需保留原始零值、特殊缺失、条件路由及软/硬核查边界；任何正式建模前仍须按获准取得的数据版本核实实际分布、有效分母和分析权重。

## 官方来源

- 2011：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`（HA066–HA068）及 `sources_official/CHARLS_2011_Codebook_extracted.txt`。
- 2013：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`（HA066–HA068）及 `sources_official/CHARLS_2013_Codebook_extracted.txt`。
- 2015：`sources_official/CHARLS_2015_Questionnaire_extracted.txt`（HA066–HA068）及 `sources_official/CHARLS_2015_Codebook_extracted.txt`。
- 2018：`sources_official/CHARLS_2018_Questionnaire_extracted.txt`（HA066_W4、HA067_W4、HA068）及 `sources_official/CHARLS_2018_Codebook_extracted.txt`。

映射仍是候选字段登记，不表示某个暴露已获准用于分析，也不暗示特定波次样本量。站点只呈现官方字段元数据及限制，不发布个体记录或 Codebook 的描述统计。
