# CHARLS ExWAS Atlas 当前目录快照（2026-10-23）

本快照基于本日完成的全量元数据流水线。仅汇总公开字段元数据和官方来源审核状态；没有拟合ExWAS关联模型，也没有将个体作答或身份信息写入仓库/网站。

- 网站字段目录7,544行：E 4,566、P-only 1,903、C 911、双角色E/P 164。
- E/P候选概念1,408个：暴露侧1,130、表型侧287、双角色9；E/P概念—源字段映射6,598行。全来源crosswalk 6,804行，其中6,792行匹配目录、12行是目录外C元数据。
- 五个常规波次元数据层面的非自配对共现为2011 120,052、2013 126,301、2015 128,984、2018 98,667、2020 12,598。它们不是受访者人数、逐对样本量或分析资格。
- E/P目录有3,199行带非空已审/官方类别标签文本，覆盖3,173个波次—字段码；853条E/P目录角色行仍显示`not yet reviewed`。连续测量、测量组件和计数可已完成语义审阅而没有类别值标签。2013/2015/2018疾病控制/既往访谈变化48个字段、2020既往访谈变化18个字段，以及2011/2020自知疾病6个字段均已补入逐波官方类别；本轮另补2013–2018自知疾病11个字段，频数未复制，详见[`self_awareness_response_label_review_2026-10-23.md`](self_awareness_response_label_review_2026-10-23.md)。22个连续残疾发生年份字段标注calendar year，见[`disability_onset_year_unit_review_2026-10-23.md`](disability_onset_year_unit_review_2026-10-23.md)。
- 本轮修复连续行为变量审核状态传播：73条波次—字段行从泛化的未核验状态改为有来源的连续测量/年龄年份语义。细节见[`behavior_numeric_measure_status_sync_2026-10-23.md`](behavior_numeric_measure_status_sync_2026-10-23.md)。
- 另有608条养老金数值/计数或无离散类别字段从通用待核状态改为“官方代码本字段已定位；未列离散类别”；其余6条源审核记录已有更具体状态而予以保留。此状态不代表单位、路线或发行版编码已核。详见[`pension_numeric_status_sync_2026-10-23.md`](pension_numeric_status_sync_2026-10-23.md)。
- 收入/家庭支出类别中有51条精确代码本条目显示数值摘要但未列分类菜单；另为五波工资/奖金收入字段转录`1=Yes; 2=No`类别，频数未复制、波次题目范围仍分开审核。详情见[`income_numeric_and_receipt_label_sync_2026-10-23.md`](income_numeric_and_receipt_label_sync_2026-10-23.md)。
- 为2015、2018、2020体力活动目的字段补录9条逐波四选项标签；频数未复制，且这描述“为什么活动”，不能当作活动剂量。详见[`physical_activity_purpose_labels_2026-10-23.md`](physical_activity_purpose_labels_2026-10-23.md)。
- 为2011、2013、2015、2018的前列腺疾病DA030确诊时间组件补上年份/年龄单位状态，年份与年龄分开，保留男性限定路线并注明不含前列腺癌；Codebook摘要极值不作为有效范围。详见[`prostate_illness_diagnosis_time_units_2026-10-23.md`](prostate_illness_diagnosis_time_units_2026-10-23.md)。
- C类目录有331行仍显示`not yet reviewed`；该项不意味着所有连续测量都应有类别标签，也不意味着每条C记录都进入E/P关联。
- 现有逐字段`DO NOT ANALYZE`锁定33条；唯一精确`conflict`状态为0，但2011 `FB010`问卷与Codebook编码差异仍单独锁定。正式模型数为0，没有发布关联估计。
- 官方抽样权重与方差设计限制已写入公开主页；2013样本标记的源文件恢复、逐波模块权重、PSU源版本匹配及可用于方差估计的分层/复制权重仍是正式分析门槛。详见[`survey_design_weight_review_v1.md`](survey_design_weight_review_v1.md)。

## 验证

`python scripts/build_ep_atlas_metadata.py --finalize-only`成功完成；73项测试通过；延迟加载器Node测试通过；`node --check site-prototype/dist/app.js`通过；网站目录33个JSON均可解析；E/P/C三份目录分片与主目录筛选结果完全一致；33条`DO NOT ANALYZE`锁定与分流清单完全一致；`git diff --check`通过。首页不加载目录JSON；Pages部署包排除仅供构建/审计的主目录JSON，公开行为与E/P/C分片及专题目录按需加载。私有派生表ID/波次验证中2011/2015/2018/2020为PASS、2013因缺少两个必需样本标记为CHECK；逐波权重覆盖汇总见[`survey_design_weight_review_v1.md`](survey_design_weight_review_v1.md)。公开元数据重建未读取任何CHARLS个人记录。分片站点已部署：GitHub Actions Validate #78、Pages #23成功；线上app.js?v=58和E/P/C分片HTTP 200，部署主目录HTTP 404。

2026-10-23 work-field status synchronization: exact wave/code matches to the reviewed work crosswalk moved 170 E/P rows from the generic `not yet reviewed` state to the source-specific continuous/open-response or no-discrete-category status. The current catalog has 677 E/P rows in the generic state, 3,199 rows with nonempty official/reviewed labels, and 339 total entries carrying this specific work-field status. These are metadata-review counts, not independent indicators or analysis eligibility. The full metadata pipeline and 83 tests passed; no respondent data or frequencies were used. See [`work_numeric_catalog_status_sync_2026-10-23.md`](work_numeric_catalog_status_sync_2026-10-23.md).
