# 农业劳动状态与工时/收入字段审计（2026-10-21）

> **来源身份更正（2026-10-22）：**已用正式2011基线家户问卷逐项复核FC001–FC011题干、分支、量纲和软核查：FC001=No跳至FC008；FC006范围0–16小时并设>16软核查；FC008=No跳至FC013；FC011问卷列0–24小时、>16触发检查。值码与变量标题另由2011 Codebook核对。正确问卷与检索摘录见 `sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc` 和相邻 `_extracted.txt`；不再使用误标为2011的2013文件。

## 本轮范围

根据CHARLS 2011基线家户问卷、2013/2015/2018问卷及对应代码本，补充9个就业暴露候选概念、28条波次字段映射。只将题目明确指向个人劳动条件的封闭/连续变量纳入；不把农业劳动总项、受雇为其他农户务农、自家家庭农业劳动混成单一工时。代码本频数未复制到目录或网站。

| 候选概念 | 波次字段 | 测量定义、单位 | 条件/说明 |
|---|---|---|---|
| `farm_wage_work_at_least_10days_2011_2018` | 2011/2013/2015/2018 `fc001` | 过去一年是否为其他农户/雇主从事有偿农业工作至少10天；1=Yes, 2=No | 2011–2015题干称“其他农户”，2018称“其他农户/雇主”。属于FA001广义过去一年农业工作的具体有偿子项，二者不能当成独立、不重叠暴露。|
| `farm_wage_months_past_year_2011_2013` | 2011/2013 `fc004` | 过去一年有偿农业劳动月份，0–12月 | 仅在FC001=Yes的农户有偿农业路径中。2020复用`fc004`表示工作地点，所以2020未映射。|
| `farm_wage_days_per_week_2011_2013` | 2011/2013 `fc005` | 正常工作月每周工作天数，0–7天/周 | FC001=Yes后询问。不是全年总天数。|
| `farm_wage_hours_per_day_2011_2013` | 2011/2013 `fc006` | 正常工作日每天工作小时，问卷范围0–16小时 | FC001=Yes后询问；问卷将>16列为软核查，不自动截断/剔除。|
| `farm_wage_monthly_income_2011_2013` | 2011/2013 `fc007` | 工作月份中的平均月工资，元/工作月 | FC001=Yes后询问；不是年工资，不自动乘以FC004；名义金额需保留年份与价格基期。|
| `household_agricultural_work_at_least_10days_2011_2018` | 2011/2013/2015/2018 `fc008` | 是否在过去一年为自家从事农业劳动至少达到题干阈值；1=Yes, 2=No | 2018问卷写至少10天，2018代码本标题却写至少一个月；2018状态题`DO NOT ANALYZE`，等待正式路由说明解决分歧。|
| `household_agriculture_months_past_year_2011_2018` | 2011/2013/2015/2018 `fc009` | 自家农业劳动月份，0–12月 | FC008=Yes后询问。2018由于FC008阈值冲突，`DO NOT ANALYZE`。|
| `household_agriculture_days_per_week_2011_2018` | 2011/2013/2015/2018 `fc010` | 正常工作月每周工作天数，0–7天/周 | FC008=Yes后询问。2018由于FC008阈值冲突，`DO NOT ANALYZE`。|
| `household_agriculture_hours_per_day_2011_2018` | 2011/2013/2015/2018 `fc011` | 正常工作日每日劳动小时，问卷范围0–24小时 | FC008=Yes后询问；问卷对>16设软核查，不自动截断。2018因FC008阈值冲突`DO NOT ANALYZE`。|

## 官方材料和证据定位

- 2011：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`中FC001–FC011（目录列在当前主要工作模块）；值标签/变量标题查`sources_official/CHARLS_2011_Codebook_extracted.txt`。问卷显示FC006的0–16小时范围及超过16小时的软核查；FC011显示0–24小时范围并提示检查超过16小时的答案。
- 2013：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`及`CHARLS_2013_Codebook_extracted.txt`；农场雇佣与自家劳动题组在问卷约145–151页/代码本约738–740页。
- 2015：`sources_official/CHARLS_2015_Questionnaire_extracted.txt`及`CHARLS_2015_Codebook_extracted.txt`；FC008明确No跳过后续自家劳动测量。
- 2018：`sources_official/CHARLS_2018_Questionnaire_extracted.txt`写FC008过去一年至少10天；`sources_official/CHARLS_2018_Codebook_extracted.txt`将FC008标题写作“Self-Employed (Household) Farm Work (for at Least One Month Last Year) or Not”。目前未见可以消解此门槛不一致的更高优先级发布说明，故将2018 FC008及其FC009–FC011后续题列为DO NOT ANALYZE。
- 自动生成的逐字段定义、映射状态、来源和单位见`audit/work_exposure_crosswalk_v1.csv`；官方答案标签见`audit/work_exposure_value_labels_v1.csv`；网站概念卡见`site-prototype/dist/work_exposures_v1.json`。

## 处理边界

- 2011–2013 `fc004`只表示为其他农户有偿务农月份。字段目录中2020 `fc004`表示工作地点，是不同题目；不得跨波复用这一短变量名。
- `fc001`是FA001广义农业工作下的具体有偿劳动项；自家劳动`fc008`又有单独筛选条件。不要把几类筛选变量合并为一个“农业就业”二元项，也不要仅因候选对可共现就认为互不重叠。
- FC009–FC011在问卷中可出现0值；遵循原值标签与条件分母，不把跳题补成0或No。FC011的问卷范围0–24与软检查>16是不同信息，不据软检查阈值自动裁切。
- FC007是工作月份平均月收入，不等同所有工作合计年收入；通胀/币值可比处理需另立分析规约。
- 本轮没有读取个人级数据，没有计算真实配对样本量、调查加权统计或关联估计。

## 构建核验

`python scripts/build_work_exposure_crosswalk.py`生成81个工作/退休/就业暴露概念及227条字段映射；`python scripts/build_work_exposure_value_labels.py`处理227条标签/语义行。全量入口`python scripts/build_ep_atlas_metadata.py`成功。新增9个概念、28条E/P链接全部匹配；2018自家农业FC008及FC009–FC011在字段级状态中标记DO NOT ANALYZE。最新总目录854个候选E/P概念（E594、P269、双角色9），E/P唯一字段链接5,280条，C crosswalk23条（20条匹配、3条既有资格/权重说明）；字段目录7,631行（E/P 7,153、C 478）。

复核结论：2011版本的农业劳动筛选与测量定义可由正确基线问卷支持，既有字段映射范围和条件路由无需变更。FC011的问卷输入范围与软核查阈值不同，目录保留原始回答并将范围解释留给数据质控；没有依据自动截断或剔除高值。2018 FC008问卷与Codebook的10天/一个月标题冲突依然未解决，该波FC008及条件后续项继续锁定。未读取个人记录。
