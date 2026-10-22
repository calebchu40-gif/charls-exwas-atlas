# CHARLS ExWAS Atlas 当前目录快照（2026-10-21）


> **当前目录口径（2026-10-21，最近重建）：**目录7,868行（E/P 7,246、C 622）；候选E/P概念1,247个（E=977、P=279、交集9；E-only=968、P-only=270）；E/P概念—源字段链接6,185条全部匹配目录；全来源crosswalk 6,350条（C165，其中162条匹配、3条目录外设计/资格元数据）。工作与职业候选继续加入2018多工作/主工作分类、工伤保险最高赔付、2011–2020工资支付来源、2020劳动合同期限与雇主起始日期，以及2018跨访工作状态转换、2013/2015 FA006_W2工作史回补、社保缴费知情与未覆盖原因，以及七个工作/经营/最近工作日期概念；另纳入工作连续性、最近工作离职原因和更正既往状态后的2020回顾性离职题（锁定不可分析）；FC018起始日期核验项为C类路由信息。工作地点仍仅保留粗类别，地址字符串不进入关联矩阵。详见[`audit/employment_unmapped_batch_review_2026-10-21.md`](audit/employment_unmapped_batch_review_2026-10-21.md)。波次元数据共现对（非样本量）：2011=103,929、2013=106,042、2015=109,387、2018=88,393、2020=12,448。未读取个人数据、未运行关联模型。


## 当前构建状态

- 覆盖CHARLS 2011、2013、2015、2018、2020五轮纵向重复访问；不是五个独立横断面周期。
- 候选E/P概念1,247个：暴露侧973、表型侧279、双角色9；E-only 968、P-only 270。候选概念不等于最终分析指标。
- E/P概念—源字段链接6,185条，均匹配主目录；全来源crosswalk 6,350条（C类165条，其中162条匹配、3条为目录外设计/资格元数据）。
- 网站字段目录7,868行：E/P 7,246行、C 622行。
- 元数据共现对：2011=103,929、2013=106,042、2015=109,387、2018=88,393、2020=12,448；只是字段元数据共现，不能解释为样本数或有效关联人数。
- 就业/工作组织子类尚有38行、27个字段码未链接概念，按官方题目、波次路由和角色继续审核。
- 本轮工作候选修订详见[`employment_unmapped_batch_review_2026-10-21.md`](employment_unmapped_batch_review_2026-10-21.md)。
- 正式ExWAS模型0；未读取个人级CHARLS记录，未生成关联结果。

## 最近修订

- 2026-10-21：2018 `FC013`依据问卷/Codebook新增单波P候选`health_related_household_agricultural_workdays_missed_2018`，限自家农业工作题组；问卷允许0–366、Codebook观测最大365，需核发布字典。与2013 FC013分开保留，详见[`health_work_absence_2018_review_2026-10-21.md`](health_work_absence_2018_review_2026-10-21.md)。E/P概念1,160（E895/P274/双角色9），E/P源链接5,897；2018元数据共现79,985对，非样本量。


- 2026-10-21：2011/2013 `FB001`转列首次工作时间年龄/年份C类单位选择器；2020同名字段为农活地点。详情见[`lifecourse_timing_selector_review_2026-10-21.md`](lifecourse_timing_selector_review_2026-10-21.md)。全来源crosswalk6,108条（C158，155条匹配、3条目录外）；目录7,818行（E/P7,205、C613）。
- 2026-10-21：2013 `FC013`按官方题干和路由改列健康相关工作缺勤P候选，单位为过去一年缺勤天数，限定农业工作模块人群；0值只表示无缺勤，跳题缺失不置零。候选概念`health_related_workdays_missed_2013`，审计见[`health_work_absence_review_2026-10-21.md`](health_work_absence_review_2026-10-21.md)。E/P概念1,160个（E895/P273/双角色9），E/P源字段链接5,897条；2013 metadata-coavailability增加到96,271对，不是有效样本量。


- 2026-10-21：2013/2015 `DC008`经问卷核实为CAPI自动记录的时钟时间（小时、分钟），不是词表回忆用时或认知表现；转列C类施测时点元数据。全来源crosswalk6,108条（C158，其中155条匹配、3条目录外）；目录7,818行（E/P7,205、C613）。审计见[`cognition_unassigned_series_triage_v1.md`](cognition_unassigned_series_triage_v1.md)。


- 2026-10-21：家庭房产出售所得用途字段新增54条2013/2015类别槽位链接，形成1个暂不可分析的E候选；官方问卷要求用途百分比，但当前公开字段目录未识别比例组件，所有映射锁定DO NOT ANALYZE，待核微观发布字段、房产槽位和分母。见[`household_sale_proceeds_allocation_mapping_review_2026-10-21.md`](household_sale_proceeds_allocation_mapping_review_2026-10-21.md)。


- 2026-10-21：新增两项工作环境候选，各覆盖2011/2013/2015/2018四波：当前工作地点相对居住地位置（不推算通勤距离，2020同名FD004排除）及不在职受访者最近一份工作的雇主单位类别（区别于当前雇主，2011选项据问卷转录）。详见[`workplace_location_2011_2018_mapping_review_2026-10-21.md`](workplace_location_2011_2018_mapping_review_2026-10-21.md)与[`most_recent_job_employer_type_2011_2018_mapping_review_2026-10-21.md`](most_recent_job_employer_type_2011_2018_mapping_review_2026-10-21.md)。


- 2026-10-21：再次全量复扫并修正DB029S1–S7、HD012、DA029/DA030、FC019/FC020/FC021/FG014的2011问卷来源；2020慢病辅助项改指向实际英文问卷。修复脚本已纳入重建流水线，audit CSV和站点JSON的错误通用2011路径残留为0，目录计数不变。详情见[`2011_questionnaire_source_identity_correction_2026-10-21.md`](2011_questionnaire_source_identity_correction_2026-10-21.md)。


- 2026-10-21：2011受访者金融资产以他人姓名登记的HC021/HC022已接入2013/2015/2018同概念；个人收入映射脚本的全部2011来源统一指向正确的`CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`。详情见[`respondent_assets_held_other_name_2011_mapping_review_2026-10-21.md`](respondent_assets_held_other_name_2011_mapping_review_2026-10-21.md)。

- 2026-10-21：2020个人工资扣款题`GA004`已纠正为C类金额形式选择器（1=月、2=年、3=工资百分比、4=无），并补入`GA004_1/_2/_3`分别连接至既有月金额、年金额和工资百分比概念；不合并不同单位，不由跳题推断零。详见[`personal_wage_deductions_2020_review_2026-10-21.md`](personal_wage_deductions_2020_review_2026-10-21.md)。

- 2026-10-21：新增2020家庭疫情经济专题26条字段—概念映射；GF015_S4与GF016_S8因官方材料冲突锁定DO NOT ANALYZE。疫情期间家庭收入、开支压力及应对字段均为单波家庭层级回顾性候选。见[`household_covid_economic_2020_review_2026-10-21.md`](household_covid_economic_2020_review_2026-10-21.md)。

- 2026-10-21：新增CHARLS 2020家庭疫情经济专题26条字段—概念映射：农业/自雇收入变化及条件金额、日常开支压力、账单支付困难、应对方式及条件金额。GF015_S4和问卷/Codebook定义冲突的GF016_S8均锁定DO NOT ANALYZE。全部限于2020家庭层级回顾项目，不与其他波次直接合并。详见[`household_covid_economic_2020_review_2026-10-21.md`](household_covid_economic_2020_review_2026-10-21.md)。全项目E/P概念1,150、链接5,812条、目录7,803行；2020目录共现11,173对，不是样本量。

- 2026-10-21：2011八个病种特异DA010“以上皆无”字段补入已有治疗方式概念，0个新概念；Codebook可确认字段身份/选项索引，但受访者级存储方向与分母仍待验证，故标注DO NOT ANALYZE。详见[`2011_disease_treatment_none_option_mapping_review_2026-10-21.md`](2011_disease_treatment_none_option_mapping_review_2026-10-21.md)。E/P字段链接更新为5,786条。
- 2026-10-21：家庭其他资产租赁收入字段按波次分成金额、状态和C类选择器；2011–2015 `HA064`不再作E，2013/2015金额字段补入可搜索目录，详见[`household_other_asset_rental_income_wave_harmonization_review_2026-10-21.md`](household_other_asset_rental_income_wave_harmonization_review_2026-10-21.md)。 网站新增独立浏览视图，按概念、编码和波次检索该组字段；页面JSON通过JS解析测试，页面/JSON HTTP 200。浏览器UI检查受本机URL策略阻止，未作绕行。
- 2026-10-21：根据逐波官方问卷与Codebook复核，扩展 `FE001` 的跨波映射：2011、2013、2015、2018为过去一年受雇工作月份，2018采用1–12值域并以“至少工作一天”定义工作月；2020同名 `FE001` 是多工作路线中其他工作的每周天数，单列概念。保留休假规则、问题路由、实际工作地点提示以及 `XSideJobDays=FE001×52` 且缺失乘积置零的CAPI派生边界。工作组织专题现为127概念/343字段映射；全项目E/P为1,124概念、5,786条字段链接。
- 同轮元数据共现数更新为2011=98,771、2013=98,281、2015=104,052、2018=82,193、2020=11,398；这些只是目录元数据可配对数，不是受访者样本量或统计结果。

- 更正2011养老金年月字段身份：以官方基线问卷和完整Codebook文本映射10个起领日期组件、2个缴费起始日期组件；按原计划与跳题路线解释，不合并不同事件。详见[`pension_2011_unmatched_date_components_review_2026-10-21.md`](pension_2011_unmatched_date_components_review_2026-10-21.md)。

- 新增2020上轮未工作后复工、复工原因、上轮工作后停止工作三项候选；分别保留FA013/FA015/FA016日期与路由。FA014/FA017确认题及FA018/FA019上轮状态纠错题不作为暴露；见[`work_transition_correction_2020_review_2026-10-21.md`](work_transition_correction_2026-10-21.md)。当时E/P概念1,113、源字段链接5,742，2020共现对8,998（历史构建数；当前数见本快照顶部）。

- 补入2011/2013轮转储蓄互助会参与及未偿金额、2015民间借贷参与及未偿金额四个波次专属概念；2015问卷与Codebook描述范围不完全相同，未强行跨波合并。未列入公开字段目录的`HC036_W3`文本题槽未建变量映射。详见[`rotating_savings_private_lending_2011_2015_review_2026-10-21.md`](rotating_savings_private_lending_2011_2015_review_2026-10-21.md)。


- 金融资产映射继续扩充：新增他人代持资产及报告价值、夫妻金融产品控制比例（2018扩展范围单列）、2013其他投资收入和公积金状态/余额；完整边界见[`respondent_financial_assets_2011_2018_review_2026-10-21.md`](respondent_financial_assets_2011_2018_review_2026-10-21.md)。


- 纠正2013 `GA002`为年/月工资收入单位选择器C类；年金额`GA002_1`与月金额`GA002_2`仍分开。该类别码不能当作连续工资暴露，见[`wage_amount_unit_selector_2013_review_2026-10-21.md`](wage_amount_unit_selector_2013_review_2026-10-21.md)。


- 2015/2018 `HC039_W3/HC040_W3`对外借款未偿应收款新增状态与金额候选；2015问卷和Codebook对字段标签冲突，两个2015映射显式锁定DO NOT ANALYZE，2018保留一致题义候选。见[`private_lending_receivable_2015_2018_review_2026-10-21.md`](private_lending_receivable_2015_2018_review_2026-10-21.md)。


- 新增现金/个人现金份额、金融机构存款、债券、股票、共同基金等金融资产候选共16概念、39条映射；夫妻共同现金、个人名下资产、过去一年持有与2018当前持有分别处理。详见[`respondent_financial_assets_2011_2018_review_2026-10-21.md`](respondent_financial_assets_2011_2018_review_2026-10-21.md)。


- 2015/2018 `HD004_W3`作为独立其他借款余额候选；2015 `HD005_W3/_1`作为题干未限定时间窗的诈骗经历/损失波次专属候选；四波`HD012`仅保留C类答题协助元数据。逐字题页核查见[`debt_and_fraud_2015_questionnaire_review_2026-10-21.md`](debt_and_fraud_2015_questionnaire_review_2026-10-21.md)。


- 2013–2018个人工资扣款已按总额/税/保险/住房公积金和年/月/工资比例拆分；父选择器归C类，2018不臆造问卷未提供的分项。见[`personal_wage_deductions_2013_2018_review_2026-10-21.md`](personal_wage_deductions_2013_2018_review_2026-10-21.md)。

- 2011/2013继承经历与财富转移字段拆分为是否继承、继承总额、来源类别、最大事件年份和最大事件金额；来源题是非互斥多选，区间题不代填金额。见[`inheritance_transfer_2011_2013_review_2026-10-21.md`](inheritance_transfer_2011_2013_review_2026-10-21.md)。

- 2011自评家庭生活水平及2013五种社会参照组相对生活水平分别列为主观社会经济位置候选；王/张情景评分按锚定题排除于E/P矩阵。见[`subjective_living_standard_2011_2013_review_2026-10-21.md`](subjective_living_standard_2011_2013_review_2026-10-21.md)。

- 2018诈骗题组按过去一年尝试诈骗、条件性类型/损失以及排除过去一年的既往财产损失经历、次数、最大损失金额/年份分别映射。多选答案存储和特殊值待获准数据核实。见[`fraud_exposure_2018_review_2026-10-21.md`](fraud_exposure_2018_review_2026-10-21.md)。

- 2011–2018 HD001未偿非住房贷款、HD003信用卡/消费信贷余额已纳入；2018贷款口径排除信用卡、消费信贷题包含京东白条/花呗，均与早期概念分开。见[`unpaid_debt_balance_2011_2018_review_2026-10-21.md`](unpaid_debt_balance_2011_2018_review_2026-10-21.md)。

- 2011/2013/2015/2018 HC033当前是否被雇主拖欠工资、HC034条件性欠薪金额分别纳入候选目录；保留2018的999拒答、HC033=是的金额路由、HC035区间题独立性及名义人民币通胀限制。见[`unpaid_wage_arrears_2011_2018_review_2026-10-21.md`](unpaid_wage_arrears_2011_2018_review_2026-10-21.md)。

- 2011/2013/2015/2018 FL008上一份非农工作周工时及FL009受雇工作月工资新增为回顾性候选；保留FL001路由、999997亏损特殊码及不同工资构成口径。见[last_nonfarm_job_hours_wage_2013_2018_review_2026-10-21.md](last_nonfarm_job_hours_wage_2013_2018_review_2026-10-21.md)。

- 2011 FJ001–FJ003侧业字段按FC019=1路由新增为独立波次候选；保留与2018排除家庭农业劳动、过去一年平均口径的差异，不把结构性跳题当0。见[`side_job_fields_2011_mapping_review_2026-10-21.md`](side_job_fields_2011_mapping_review_2026-10-21.md)。
- 2011/2013/2015 FL020的16项离职原因按多选选项分开映射；选中/未选中/缺失编码待获准数据核实，2018不同题组未强行合并。见[`work_exit_reasons_2011_2015_mapping_review_2026-10-21.md`](work_exit_reasons_2011_2015_mapping_review_2026-10-21.md)。

- 2013/2015 FN065居民类养老金预期领取时间父项归C；年龄/等待年数按计划拆开。见[`pension_2013_2015_expected_claim_timing_selector_review_2026-10-21.md`](pension_2013_2015_expected_claim_timing_selector_review_2026-10-21.md)。
- 2018商业`FN051_W4`、人寿保险`FN076_W4_a`、其他养老金`FN093_W2`是时间格式选择器而非状态；父项归C，实际数值按年龄/年数和问卷路由分开。见[`pension_2018_claim_timing_and_selector_correction_review_2026-10-21.md`](pension_2018_claim_timing_and_selector_correction_review_2026-10-21.md)。
- 2013–2018 `FN037_W2_2/_3`为余额最近查看年/月，归C测量时点；见[`pension_defined_contribution_balance_check_date_metadata_review_2026-10-21.md`](pension_defined_contribution_balance_check_date_metadata_review_2026-10-21.md)。
- 2013/2015 FN061开始缴费年月按三种居民计划和年月分开；见[`pension_2013_2015_resident_plan_contribution_start_date_review_2026-10-21.md`](pension_2013_2015_resident_plan_contribution_start_date_review_2026-10-21.md)。
- 2013/2015/2018 FN021父项为金额/工资比例形式选择器，转C；子项按货币金额与工资百分比分开，2018再保留原计划槽位。金额区间只表示区间追问。见[`pension_expected_benefit_amount_ratio_unit_split_review_2026-10-21.md`](pension_expected_benefit_amount_ratio_unit_split_review_2026-10-21.md)。
- 2011代码本`fn036`与问卷`FN036_w2`题号/子项结构不一致，原先直接连接子项的说明已撤回；保留为未链接C类元数据。见[`pension_2011_fn036_questionnaire_codebook_identity_review_2026-10-21.md`](pension_2011_fn036_questionnaire_codebook_identity_review_2026-10-21.md)。
- 养老金计划缴费要求：2015字段可作候选；2013问卷/代码本主体描述不一致、2018代码本漏列No，二者DO NOT ANALYZE。详见[`pension_plan_contribution_requirement_review_2026-10-21.md`](pension_plan_contribution_requirement_review_2026-10-21.md)。
- 2013/2015/2018 `FN038_w2`统一为计划特定最早离职并领取待遇年龄；不等于实际退休/开始领取年龄。2018宽泛“预期领取年龄”重复映射已移除。详见[`pension_earliest_employer_exit_benefit_age_review_2026-10-21.md`](pension_earliest_employer_exit_benefit_age_review_2026-10-21.md)。
- 2013/2015商业养老金`FN046_w2`开始缴费年月仅在未领取待遇路由询问，月份0为不记得；与实际领取和其他计划参加日期分开。详见[`pension_commercial_contribution_start_date_review_2026-10-21.md`](pension_commercial_contribution_start_date_review_2026-10-21.md)。
- 2018 `FN065_W2`父项1=年龄、2=距访谈年数，归C；两个数值子项分为预期领取年龄与等待年数，并保留具名方案循环及未领取路由。详见[`pension_2018_expected_receipt_timing_unit_selector_review_2026-10-21.md`](pension_2018_expected_receipt_timing_unit_selector_review_2026-10-21.md)。
- `FN069_W4`表示社区是否实施计划及个人参保资格，不代表实际参保；`FN084_W4`仅覆盖访员选择的最重要其他计划，详见对应审计。

## 方法与合规边界

- 借鉴NHANES PE Atlas字段目录、逐波字段—概念链接、配对覆盖索引、结果schema和检索界面；不移植NHANES抽样权重、周期合并和独立横断面假设。
- 不同年份、计划、单位、路由和多选槽位不自动合并；未知、拒答、跳题、未选项不推断为否/零。代码本频数不是分析样本量。
- 正式分析前须核对CHARLS许可、实际字段、个体/家庭连接、缺失及路由分母、抽样权重/分层/聚类和纵向估计目标。授权微观数据不进入协作者包。
- 原型只展示公开元数据、候选映射、字段编码和限制，不展示微观数据或未计算的关联。

## 继续计划

1. 继续筛查个人收入与家庭经济模块未映射字段，优先处理定义明确的负债、转移支付/继承和经济压力项；遇到问题文本缺失或问卷/代码本冲突时保留锁定状态，不凭字段名猜测。
2. 复核就业/退休与养老金剩余波次字段，整理未归属序列的逐波题目身份、路由、单位和值标签，把原始字段序列数与独立构念数分开报告。
3. 完善原型的字段筛选和细节呈现，建立可重复的目录/标签/配对索引QA并更新交接包。真实关联模型仅在获得所需数据权限、核实微观字段和分母、预先规定CHARLS抽样设计与纵向估计目标后启动。

## 资料入口

- [`../HANDOFF_合作者接手说明.md`](../HANDOFF_合作者接手说明.md)
- [`../logs/progress_log.md`](../logs/progress_log.md)
- [`DATA_ACCESS_AND_REPRODUCTION.md`](DATA_ACCESS_AND_REPRODUCTION.md)
- [`CHARLS_ExWAS分析规约_v0.1.md`](CHARLS_ExWAS分析规约_v0.1.md)
- [`nhanespewas_github_method_review_v1.md`](nhanespewas_github_method_review_v1.md)

- 2013 FN078及2013–2018征地养老金FN079_W2_8已将格式选择器归C，年龄与距访谈等待年数分开；2013新农保首次覆盖年份因问卷/代码本范围冲突标为DO NOT ANALYZE。详见[`pension_expected_claim_timing_selectors_2013_2018_review_2026-10-21.md`](pension_expected_claim_timing_selectors_2013_2018_review_2026-10-21.md)。

- 2013/2015土地征收经历、征收年份及征地养老金预期待遇金额形式父选择器已审核；详见[`pension_land_requisition_history_2013_2015_review_2026-10-21.md`](pension_land_requisition_history_2013_2015_review_2026-10-21.md)。

- 2013/2015土地征收经历、征收年份及征地养老金金额形式选择器已审核；详见[`pension_land_requisition_history_2013_2015_review_2026-10-21.md`](pension_land_requisition_history_2013_2015_review_2026-10-21.md)。金额形式父项只留在C类测量协议，不进入E/P crosswalk。

- 2011 FN081–FN083为问卷协助/代理访谈过程字段，现归C类测量元数据；详见[`proxy_interview_metadata_2011_review_2026-10-21.md`](proxy_interview_metadata_2011_review_2026-10-21.md)。

- 2011商业养老FN052按年缴费路径中的FN053年度保费、FN054所需缴费年数已分别映射；一次性缴费者跳过，详见[`commercial_pension_annual_contribution_2011_review_2026-10-21.md`](commercial_pension_annual_contribution_2011_review_2026-10-21.md)。

- 2011商业养老缴费承担者/缴费方式、企业补充养老金累计计划年限和选定居民养老金个人年度缴费已按问卷定义/路由完善，见[`commercial_pension_and_plan_contribution_2011_review_2026-10-21.md`](commercial_pension_and_plan_contribution_2011_review_2026-10-21.md)。

- 2013–2018征地养老金FN079_W2_10/_11已修正为仅当前领取者适用的实际领取年月和月金额，区别于预期年龄/等待年数及预期待遇金额，见[`land_requisition_pension_current_benefit_2013_2018_review_2026-10-21.md`](land_requisition_pension_current_benefit_2013_2018_review_2026-10-21.md)。

- 2011代码本DE010–DE012从错误E类改为三个单独的P候选，代码本值标签已核实，但官方问卷未找到对应题干；三项标为DO NOT ANALYZE，详见[`codebook_only_sleep_severity_2011_identity_review_2026-10-21.md`](codebook_only_sleep_severity_2011_identity_review_2026-10-21.md)。

- 2026-10-21：将2011 GE003“谁回答家户收入/支出问题”从自动E候选纠正为C类回答来源元数据；新增官方选项标签及复现说明。详见[`household_financial_respondent_metadata_review_2026-10-21.md`](household_financial_respondent_metadata_review_2026-10-21.md)。
- 2015/2018诈骗题组时间窗与损失定义拆分见[`fraud_exposure_2015_2018_wave_definition_review_2026-10-21.md`](fraud_exposure_2015_2018_wave_definition_review_2026-10-21.md)。

- 最新家户经济补充：GB010过去一年新牲畜/水产购买支出四波均已加入，2011/2013 HA025家户住房装修支出仍限定两波。见`household_agricultural_production_review_2026-10-21.md`和`household_renovation_expenditure_review_2026-10-21.md`。


2011/2013/2015家户社会捐助、征地补偿和住房拆迁补偿金额现按三类概念分开映射；条件路由和零值限制见`audit/household_transfer_compensation_review_2026-10-21.md`。

- 2026-10-21认知测验过程字段复核：将39条词表版本/刺激/任务状态/拒答原因记录从P转为C类测量元数据；E/P概念与链接数不变。未映射P字段现47行/47码，认知子类剩2行/1码。详见`cognition_unassigned_series_triage_v1.md`。
