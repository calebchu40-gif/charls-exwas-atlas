# CHARLS ExWAS Atlas 当前目录快照（2026-10-23）

本快照基于本日完成的全量元数据流水线。仅汇总公开字段元数据和官方来源审核状态；没有拟合ExWAS关联模型，也没有将个体作答或身份信息写入仓库/网站。

- 网站字段目录角色分片7,769行：E 4,723、P 2,067、C 979；双角色E/P在E与P分片各出现一次。
- E/P候选概念1,409个：暴露侧1,131、表型侧287、双角色9；E/P概念—源字段映射6,598行。全来源crosswalk 6,812行，其中6,793行匹配目录、19行未匹配目录。
- 五个常规波次元数据层面的非自配对共现为2011 120,052、2013 126,301、2015 128,984、2018 98,667、2020 12,598。它们不是受访者人数、逐对样本量或分析资格。
- E/P目录有3,208行带非空已审/官方类别标签文本，覆盖3,182个波次—字段码；456条E目录角色行仍显示`not yet reviewed`。连续测量、测量组件和计数可已完成语义审阅而没有类别值标签。2013/2015/2018疾病控制/既往访谈变化48个字段、2020既往访谈变化18个字段，以及2011/2020自知疾病6个字段均已补入逐波官方类别；本轮另补2013–2018自知疾病11个字段，频数未复制，详见[`self_awareness_response_label_review_2026-10-23.md`](self_awareness_response_label_review_2026-10-23.md)。22个连续残疾发生年份字段标注calendar year，见[`disability_onset_year_unit_review_2026-10-23.md`](disability_onset_year_unit_review_2026-10-23.md)。
- 另对2018当前住房产权关系9个E候选字段核对Codebook：仅1个字段有完整0/1标签，8个字段只有“0=Do Not Own”出现在频数型Codebook摘录中，均未推断缺失类别，也未复制频数。目录元数据与住房专题查询现显示这一完整/部分区分；详见[`housing_current_owner_relation_labels_2018_review_2026-10-23.md`](housing_current_owner_relation_labels_2018_review_2026-10-23.md)。因此通用值标签待核E字段由633降至624。
- 本轮修复连续行为变量审核状态传播：73条波次—字段行从泛化的未核验状态改为有来源的连续测量/年龄年份语义。细节见[`behavior_numeric_measure_status_sync_2026-10-23.md`](behavior_numeric_measure_status_sync_2026-10-23.md)。
- 另有608条养老金数值/计数或无离散类别字段从通用待核状态改为“官方代码本字段已定位；未列离散类别”；其余6条源审核记录已有更具体状态而予以保留。此状态不代表单位、路线或发行版编码已核。详见[`pension_numeric_status_sync_2026-10-23.md`](pension_numeric_status_sync_2026-10-23.md)。
- 收入/家庭支出类别中有51条精确代码本条目显示数值摘要但未列分类菜单；另为五波工资/奖金收入字段转录`1=Yes; 2=No`类别，频数未复制、波次题目范围仍分开审核。详情见[`income_numeric_and_receipt_label_sync_2026-10-23.md`](income_numeric_and_receipt_label_sync_2026-10-23.md)。
- 为2015、2018、2020体力活动目的字段补录9条逐波四选项标签；频数未复制，且这描述“为什么活动”，不能当作活动剂量。详见[`physical_activity_purpose_labels_2026-10-23.md`](physical_activity_purpose_labels_2026-10-23.md)。
- 为2011、2013、2015、2018的前列腺疾病DA030确诊时间组件补上年份/年龄单位状态，年份与年龄分开，保留男性限定路线并注明不含前列腺癌；Codebook摘要极值不作为有效范围。详见[`prostate_illness_diagnosis_time_units_2026-10-23.md`](prostate_illness_diagnosis_time_units_2026-10-23.md)。
- C类目录有329行仍显示`not yet reviewed`；该项不意味着所有连续测量都应有类别标签，也不意味着每条C记录都进入E/P关联。
- 现有逐字段`DO NOT ANALYZE`锁定89条；唯一精确`conflict`状态为0，但2011 `FB010`问卷与Codebook编码差异仍单独锁定。正式模型数为0，没有发布关联估计。
- 官方抽样权重与方差设计限制已写入公开主页；2013样本标记的源文件恢复、逐波模块权重、PSU源版本匹配及可用于方差估计的分层/复制权重仍是正式分析门槛。详见[`survey_design_weight_review_v1.md`](survey_design_weight_review_v1.md)。

## 验证

本轮全量元数据流水线及`--finalize-only`传播构建均完成；111项测试通过；延迟加载器Node测试、`node --check site-prototype/dist/app.js`和`git diff --check`通过。E/P/C三份目录分片与主目录筛选结果完全一致；89条`DO NOT ANALYZE`锁定与分流清单完全一致。首页不加载目录JSON；Pages部署包排除仅供构建/审计的主目录JSON，公开行为与E/P/C分片及专题目录按需加载。私有派生表ID/波次验证中2011/2015/2018/2020为PASS、2013因缺少两个必需样本标记为CHECK；逐波权重覆盖汇总见[`survey_design_weight_review_v1.md`](survey_design_weight_review_v1.md)。公开元数据重建未读取任何CHARLS个人记录。提交`1ef4069`已推送；公开E分片以无缓存、版本参数请求返回HTTP 200，显示9条2018当前住房产权关系字段，其中1条完整0/1标签、8条部分代码本标签状态，与本地生成内容一致；公开站点已包含此次更新。

2026-10-23 work-field status synchronization: exact wave/code matches to the reviewed work crosswalk moved 170 E/P rows from the generic `not yet reviewed` state to the source-specific continuous/open-response or no-discrete-category status. The current catalog has 677 E/P rows in the generic state, 3,199 rows with nonempty official/reviewed labels, and 339 total entries carrying this specific work-field status. These are metadata-review counts, not independent indicators or analysis eligibility. The full metadata pipeline and 83 tests passed; no respondent data or frequencies were used. See [`work_numeric_catalog_status_sync_2026-10-23.md`](work_numeric_catalog_status_sync_2026-10-23.md).

2026-10-23 work-field follow-up after CAPI/conflict synchronization: the complete E/P catalogue now has 670 rows still marked generic `not yet reviewed`, and 3,207 nonempty official/reviewed label rows across 3,181 wave-fields. Five 2020 questionnaire-derived CAPI formulas retain an explicit route-validation caveat; two employment field-identity discrepancies remain `DO NOT ANALYZE`. Pages run #30 and validation run #89 succeeded for the preceding 170-field status update (`5d60ca2`); these follow-up catalogue changes are being validated/published in the next commit. No effects were estimated.
Deployment verification after commit `00a0657`: Pages #31 and validation #90 succeeded; public `catalog_e.json` returned HTTP 200 and contains the newly synchronized work-field statuses.
Deployment verification after commit `00a0657`: Pages #31 and validation #90 succeeded; public `catalog_e.json` returned HTTP 200 and contains the newly synchronized work-field statuses.
2011 Codebook search-status update deployed in Pages #32 (Validate #92); public E catalog returned HTTP 200 with the specific “category labels not located” state. Current E/P status is 633 generic `not yet reviewed` rows and 3,207 nonempty label rows.

2026-10-23 smoking cessation source review: 2013/2015/2018/2020 age/year selectors are classified as C metadata. The 2018 questionnaire and Codebook reverse the DA062_1/DA062_2 component labels; both children remain searchable and locked from analysis, and the selector has no displayed category mapping. Current active locks=35; full rebuild and 86 tests pass. Commits `85509a4` and `b87aa15` are deployed: Pages #33/#35 and Validate #93/#96 succeeded. After `Cache-Control: no-cache` revalidation, the public E/C catalog shards match the local generated JSON exactly; the 2018 DA062 lock and all four 2011 fixed Age/Year markers were verified in their correct role shards.

- 2018年戒烟时间DA062子字段存在问卷与Codebook的年龄/年份标签冲突；DA062_1、DA062_2已保留为可检索但不可分析项，DA062选择器移为C类。2013、2015、2020戒烟时间选择器亦已从E类移为C类；2011 DA062S1/DA062S2及DA065S1/DA065S2固定“Age/Year”标记值均作为C类保存，真实回答字段DA062_1/DA062_2保留为E候选；核对及实现见[`smoking_cessation_2018_age_year_component_conflict_review_2026-10-23.md`](smoking_cessation_2018_age_year_component_conflict_review_2026-10-23.md)。


2018 HA004 household property value correction: the official code order is measure first and property slot second. Seven total-value/unit-value selectors are C measurement metadata; all 12 amount fields now map to the correct total or unit-area concept and reporting unit. The full pipeline and 108 tests passed. Details: [`household_property_value_2018_slot_unit_review_2026-10-23.md`](household_property_value_2018_slot_unit_review_2026-10-23.md).


2011–2015住房金额题组续审：剩余40个住房金额字段按官方问卷确认单位和连续测量性质；频数/极值不进入公开目录，授权发行版存储与特殊值仍待核。E住房类标签待核由40降至0；E总通用待核456。详见[`housing_numeric_value_metadata_review_2026-10-23.md`](housing_numeric_value_metadata_review_2026-10-23.md)。


## 2026-10-23后续更新：家庭房产出售款用途字段

10月21日关于“未找到百分比值字段”的记录经官方Codebook复核被更正。2013/2015共识别54个数值百分比源字段，并按单独候选概念写入E主目录和配对源目录；54个option-indexed选择槽转C类；4个其他用途自由文本字段只作C元数据。字段/槽位映射和有效分析分母仍需授权发行版QA，54个数值字段均进入`DO NOT ANALYZE`清单，锁定总数89。角色分片为E 4,723、P 2,067、C 979；完整目录写回和分片检查已通过，111项测试及锁定一致性验证通过。该处理不读取受访者记录、不公开自由文本或Codebook频数。详见[`household_sale_proceeds_allocation_mapping_review_2026-10-23.md`](household_sale_proceeds_allocation_mapping_review_2026-10-23.md)。
