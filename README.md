# CHARLS ExWAS Atlas 当前状态（2026-10-24）


## 最新工作：核实Wave 5年龄与性别官方派生公式

2026-10-23完成最后12条E类通用“not yet reviewed”状态的官方来源审核，包括2011家庭月支出、2013跨访谈期其他工作数量、2018/2020其他资产租金收入、2020工资变化方向、2011职业分类，以及保留分析锁的疫情应对和离职原因字段。通用待核E状态现为0；另有55条前访回答历史/路由C字段已按官方Codebook完成来源审核。E类待核清零不代表分析资格已确认。目录仍处于元数据和方法准备阶段，正式关联模型数为0。详细记录见[`audit/final_pending_field_review_2026-10-23.md`](audit/final_pending_field_review_2026-10-23.md)和[`audit/prior_wave_history_routing_metadata_review_2026-10-23.md`](audit/prior_wave_history_routing_metadata_review_2026-10-23.md)和[`audit/c_placeholder_legacy_field_review_2026-10-23.md`](audit/c_placeholder_legacy_field_review_2026-10-23.md)和[`audit/c_measurement_protocol_metadata_review_2026-10-23.md`](audit/c_measurement_protocol_metadata_review_2026-10-23.md)。个人收入与工资、社会照护、教育与户口审核分别见[`audit/personal_income_wage_metadata_review_2011_2020_2026-10-23.md`](audit/personal_income_wage_metadata_review_2011_2020_2026-10-23.md)、[`audit/social_care_caregiver_metadata_review_2011_2013_2026-10-23.md`](audit/social_care_caregiver_metadata_review_2011_2013_2026-10-23.md)、[`audit/education_hukou_value_label_review_2011_2020_2026-10-23.md`](audit/education_hukou_value_label_review_2011_2020_2026-10-23.md)。个人收入审核见[`audit/personal_income_wage_metadata_review_2011_2020_2026-10-23.md`](audit/personal_income_wage_metadata_review_2011_2020_2026-10-23.md)；社会照护审核见[`audit/social_care_caregiver_metadata_review_2011_2013_2026-10-23.md`](audit/social_care_caregiver_metadata_review_2011_2013_2026-10-23.md)；教育与户口字段审核见[`audit/education_hukou_value_label_review_2011_2020_2026-10-23.md`](audit/education_hukou_value_label_review_2011_2020_2026-10-23.md)。


2026-10-24逐行核对CHARLS 2020英文问卷的CAPI派生定义，确认Wave 5年龄`xrage`的新访/返访出生年规则及性别`xrgender`的前波记录冲突确认规则。已把8条2020候选C字段写入机器可读目录，转录问卷支持的类别标签，不复制频数；输入字段、预载字段与派生值分别标明角色。它们仍不是已批准的统一协变量或调整集。见[`audit/official_age_gender_harmonization_review_2026-10-23.md`](audit/official_age_gender_harmonization_review_2026-10-23.md)。

## 本地元数据重建

- `python scripts/build_ep_atlas_metadata.py`：全量重建所有波次来源交叉表、目录、配对索引和网站元数据；官方源文件或上游映射有变化时使用。
- `python scripts/build_ep_atlas_metadata.py --finalize-only`：仅在所有上游交叉表/审核文件已更新时，重建主目录和下游汇总/静态网站 JSON；适合只改值标签状态传播、目录前端或下游汇总的迭代。该模式不会重跑上游映射，源问卷、Codebook或交叉表变更后不可用它替代全量构建。

本地全量构建和`--finalize-only`均已通过当前项目测试；完整流水线用来保证源映射时，最终目录锁定校验、测试和受限格式扫描仍需照常运行。

## 2013官方样本标记补入

受控数据 QA 发现，现有2013分析表虽含权重列，但缺少官方`crosssection`与`longitudinal`样本标记，不能用权重是否缺失替代样本资格。待通过本人 CHARLS 账户下载官方`Weights.dta`后，将其放入`%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\incoming_2013_weights\Weights.dta`，并按[`audit/wave2_official_weight_intake_2026-10-23.md`](audit/wave2_official_weight_intake_2026-10-23.md)运行受控合并和复核。合并脚本默认另写私有 DTA、输出不含个体记录的汇总 QA，并在 ID 重复/缺失、匹配不全、标记缺失或现有权重值冲突时停止；不应把官方文件或派生个体数据放入项目同步目录或 GitHub。

当前E类通用待核队列已清零；C类前访回答历史/路由元数据、疾病占位/停用旧字段及测量设计字段已完成来源审核。另有456条由关键词自动发现的C类检索线索（300个不同字段码；与值标签待核行数不是同一统计），含年龄、性别等核心变量来源，也混有迁移史、疾病发生年龄和家庭名册字段；它们不是已核准的协变量，更不是统一调整集。网站已将其单独标为“自动关键词检索线索（未核验协变量）”。经逐波梳理的年龄、性别、教育、婚姻、户籍、城乡/居住地和调查设计准备情况见[`audit/core_covariate_readiness_2026-10-23.md`](audit/core_covariate_readiness_2026-10-23.md)；历史队列见[`audit/current_value_label_review_queue_2026-10-23.md`](audit/current_value_label_review_queue_2026-10-23.md)。这些计数不代表待新增的独立指标数；连续测量、金额和日期字段可能没有离散类别标签。

## 公开网站部署

网站使用 GitHub Pages，部署包只含`site-prototype/dist/`下的静态页面和候选变量元数据，不含CHARLS个体级数据。用户已明确接受整个仓库公开；仓库及Pages已公开上线。2026-10-22首次部署工作流成功（Run #1）；首页、`app.js`和候选配对JSON均经外部HTTP请求验证返回200。公开网址：[https://calebchu40-gif.github.io/charls-exwas-atlas/](https://calebchu40-gif.github.io/charls-exwas-atlas/)。站点更新或部署工作流变更推送到`main`后会自动部署；Actions仍保留手动运行入口。

网站现包含“候选配对查询”：可选一个波次、一个E概念和一个P概念，查看各自的CHARLS源字段、模块、标签与审计边界。页面只计算元数据层概念组合，不提供配对样本量或关联估计；目前已审查模型仍为0。

医保与医疗利用专项审计的逐字段状态也已进入主E/P目录：保险未选编码的不确定性、连续就诊/住院次数、条件路由和费用区间边界会随字段展示。完整题目与波次定义见[`audit/healthcare_access_definition_review_v1.md`](audit/healthcare_access_definition_review_v1.md)和[`audit/healthcare_access_value_label_review_v1.md`](audit/healthcare_access_value_label_review_v1.md)；这些状态不表示获准发行数据编码、分母或模型资格已经核实。

截至2026-10-24，公开元数据查询首版已上线；完整结果型ExWAS工作仍在变量审计和调查设计阶段。最新工作状态见[`audit/active_work_status_2026-10-23.md`](audit/active_work_status_2026-10-23.md)，年龄/性别构造复核见[`audit/official_age_gender_harmonization_review_2026-10-23.md`](audit/official_age_gender_harmonization_review_2026-10-23.md)，整体进度口径和剩余工期估算见[`audit/project_progress_estimate_2026-10-23.md`](audit/project_progress_estimate_2026-10-23.md)。

GitHub 官方说明：GitHub Free 个人仓库需要公开仓库才能使用 Pages；Pro/Team 等计划也支持私有源仓库发布 Pages。GitHub Pages 网站内容默认可被互联网公开访问，因此发布包必须保持为静态目录范围。见[Pages 发布源说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。


> **最新目录状态（2026-10-23）：**网站角色分片目录7,769行（E 4,723、P 2,067、C 979；双角色E/P在E、P分片各计一次）；候选概念1,409个（暴露侧1,131、表型侧287、双角色概念9），E/P来源字段映射6,598行。全来源crosswalk 6,812行，其中6,793匹配目录、19条未匹配。2011/2013/2015/2018/2020目录概念对共现为120,052/126,301/128,984/98,667/12,598；**仅表示字段元数据层面的潜在共现，不是人数、配对样本量或分析资格**。2018 HCAP及跨波拒答/施测/工具使用共15个字段列为C类；连续减法和动物流畅性计数维持原始数值候选并标明Codebook范围限制。E/P目录中有3,315行带非空值标签（3,238个波次—字段码），204行E目录角色仍显示`not yet reviewed`；另有170条工作/就业字段从通用待核状态改为有官方代码本来源的连续/开放回答或无离散类别状态，未添加虚构标签；5个2020问卷CAPI公式和2个问卷/代码本身份冲突字段也已同步到目录，后两者维持路由待核或DO NOT ANALYZE；另有33条2011工作字段在已提取代码本中未找到类别标签，网站明确展示“未定位”且不等同于“无类别”；22个连续残疾发生年份字段已注明calendar year，且11个2013–2018慢病自知字段的完整问卷选项已录入，频数未复制。另对2018当前住房产权关系9个字段核对代码本：1个字段显示完整0/1标签，8个字段明确标为Codebook摘录类别不完整，未推断缺失类别、未复制频数；5个当前住宅产权份额字段已按官方问卷确认为连续百分比，补入单位和路由/特殊值限制，不将代码本摘要极值当作有效范围；15个五波卧室/起居室/厕所字段已注明计数单位、住宅对象和软性检查限制；另审核10个五波家庭食品及外出就餐支出字段，记录元/周、家户层口径、自产食品与宴席排除差异；15个主购买者身份/名册选择器/共餐人数变量也已逐波记录测量层级和问卷路由；另将2011–2020楼层位置与2020入口台阶数按住宅层级及波次特异路线说明；厕所距离按米记录，并保留早期拆分选项与后期单题编码差异；2011/2013自报每日进餐次数的六档标签也已加入；2011–2018厨房及阳台数量作为家户住宅计数保留；四波I002宅基地面积以平方米记录，并注明农村宅基地定义及0值可能表示不适用；2018房产计数与七个出租状态槽位按问卷路线和拒答编码说明；实际租金与市场租金以元/月、按房产序号分开记录。已审来源与发行版待核状态分开显示；精确`conflict`标签计数为0，但2011 `FB010`问卷与Codebook编码差异已确认并单独标记`DO NOT ANALYZE`；FL020 16个多选选项含义已补录，但数值存储尚未验证，保持锁定；2011 `fn024`已纠正为未办理退休者当前参保类型，与2013既往参保题分开。2013 `fn056_w2_5`问卷选项/CodeBook类别表覆盖差异已裁定为非标签冲突；2018戒烟年龄/年份两个子字段存在问卷与Codebook标签直接冲突，均留在目录但锁定DO NOT ANALYZE；相关DA062选择器归C类；2011 DA062S1/DA062S2和DA065S1/DA065S2固定“Age/Year”代码本标记均归C类，真实时间回答仍由DA062_1/DA062_2表达。总分析锁定数更新为89。未拟合关联模型。

**私有派生数据 QA（2026-10-23）：**2015/2018/2020 的个体横截面权重覆盖与官方`crosssection=1`计数一致。现存2013派生表缺少`crosssection`和`longitudinal`标记，验证状态为`CHECK`；该波必须恢复官方权重来源并重建后，才能判断缺权重记录的资格。五波ID完整性检查通过，但这一检查不代表可运行正式模型。逐波汇总见[`audit/survey_design_weight_review_v1.md`](audit/survey_design_weight_review_v1.md)。

2026-10-23全量元数据重建：同步了既有官方交叉表中的类别标签和连续测量语义；73条行为连续变量行从泛化未核验状态改为有来源的连续量/年龄年份说明，另有608条养老金数值/计数或无离散类别字段显示代码本字段已定位，51条收入/家庭支出字段显示代码本数值摘要，五波工资收入类别按波次转录且省略频数。连续型状态不等同于类别值标签，特殊值、单位、路由和分析资格仍待发行版审核。最新快照见[`audit/current_directory_snapshot_2026-10-23.md`](audit/current_directory_snapshot_2026-10-23.md)，状态传播细节见[`audit/behavior_numeric_measure_status_sync_2026-10-23.md`](audit/behavior_numeric_measure_status_sync_2026-10-23.md)和[`audit/pension_numeric_status_sync_2026-10-23.md`](audit/pension_numeric_status_sync_2026-10-23.md)、[`audit/income_numeric_and_receipt_label_sync_2026-10-23.md`](audit/income_numeric_and_receipt_label_sync_2026-10-23.md)。

2026-10-22网站数量核对：修正生命历程目录旧版“15组/117字段”说明，并移除住房索引标题中的静态字段数。页面现按JSON目录实时呈现命中量；核验当前生命历程为18个概念组/471个源字段，住房目录817条源字段。详情见[`audit/site_prototype_count_consistency_2026-10-22.md`](audit/site_prototype_count_consistency_2026-10-22.md)。

2011 `FN064_1`–`FN064_4`、`FN070_1`–`FN070_4`的Codebook阈值类别现已恢复到网站标签：每个字段只显示Codebook实际列出的类别，不抄录频数，不推断未列类别。它们仍是条件路由下的阈值回答组件，不是待遇金额；八项继续显示`DO NOT ANALYZE`，直到支付周期、阈值序列与路线问题解决。前端现对全部`Review.Flag`带有`DO NOT ANALYZE`的E/P字段显示警示。见[`audit/pension_2011_fn064_fn070_storage_route_review_2026-10-22.md`](audit/pension_2011_fn064_fn070_storage_route_review_2026-10-22.md)。

2026-10-22官方CHARLS-HCAP Data Alert/User Guidance已核验并纳入认知条目页面；新增2018仙人掌命名及修订评分候选，明确识字/视力/文化偏倚和十词记忆跨波不可直接比。详见`audit/hcap_wave4_cognition_bias_guidance_review_2026-10-22.md`。

环境暴露候选续审已区分住户/住宅层与2011社区告知人层：后者目前有100个概念、187条字段映射且仅覆盖2011，含社区水源和燃料户数、供暖/卫生/电力、社区污染评级与距离、天气及灾害等；它们不是个人剂量。住户住宅候选跨波覆盖饮水、厕所、烹饪/取暖燃料、室内环境等，但同名字段存在波次换码/构念变化（如2020 I016为tap water、I017为淋浴设施、I021为烹饪燃料）。见[`audit/community_environment_candidate_review_2026-10-22.md`](audit/community_environment_candidate_review_2026-10-22.md)及既有[`audit/food_environment_crosswalk_audit_v1.md`](audit/food_environment_crosswalk_audit_v1.md)。


2013 Wave 2人寿保险缴费频率`FN056_W2_5`原唯一标签冲突已按官方问卷选项定义解除。季度选项仍会显示，并注明CodeBook类别表没有列出、季度金额子字段另标无观测；未传播CodeBook频数，也未从表格缺项推断原始数据值。详见[`audit/life_insurance_frequency_wave2_category_coverage_review_2026-10-22.md`](audit/life_insurance_frequency_wave2_category_coverage_review_2026-10-22.md)。

2015 `DA061_W3`已按官方问卷核明为回顾上一波吸烟状态（不是2015当轮状态）；2018 `DA061_W4`则引用上轮既往记录后询问当前状态。`DA059`因返访路由可跳题，空值不代表从未吸烟。详细说明及网站关系提示见`audit/concept_overlap_resolution_2026-10-22.md`，跨波状态构造前必须保留时间参照与路由分母。

2026-10-22续审：FM033四个已观测类别和FM011=3路由已核实，从旧菜单冲突锁定中移出；未观测的商业保险选项不推断编码，空白保留为缺失。FM032/FM035端点的成对字符串存储和路径已核实，但极端特殊码仍未解释，继续锁定。当前锁定数33；审计见[`audit/pension_2011_fm032_fm033_fm035_route_storage_review_2026-10-22.md`](audit/pension_2011_fm032_fm033_fm035_route_storage_review_2026-10-22.md)。

本轮认知标签导入和C类施测字段复核见[`audit/cognition_label_ingestion_and_role_rebuild_2026-10-22.md`](audit/cognition_label_ingestion_and_role_rebuild_2026-10-22.md)。结果表schema已配备结构/样本流/设计状态校验器[`scripts/validate_exwas_result_table.py`](scripts/validate_exwas_result_table.py)，4项合成规则测试通过；这不代表CHARLS模型已拟合。

慢病辅助题的84条非空审定值标签现已逐波精确进入主目录；新增13个标签展示，并统一2011 DA020S2多选选项的说明，避免误把未选中代码当作No。具体字段和路由限制见[`audit/chronic_disease_ancillary_label_ingestion_2026-10-22.md`](audit/chronic_disease_ancillary_label_ingestion_2026-10-22.md)。

工作类复选框中53个已有明确官方选项标签的字段也已加入检索目录，并在网站标签旁直接显示“未选中不等于No”的说明；没有因此推断选项存储或分析资格。见[`audit/work_checkbox_value_label_ingestion_2026-10-22.md`](audit/work_checkbox_value_label_ingestion_2026-10-22.md)。

另补入个人收入/家庭经济、借贷和养老的7个逐波官方类别标签；家庭借贷否定路由、养老缴费来源和主观晚年依靠的含义均保留在审计中。见[`audit/additional_income_debt_pension_label_ingestion_2026-10-22.md`](audit/additional_income_debt_pension_label_ingestion_2026-10-22.md)。

补入2011/2015共16个养老金参与/资格选项标签，并在C类元数据中显示2018年/月格式选择器；不把资格、参与、领取或条件性多选合并解释。见[`audit/pension_and_format_selector_label_ingestion_2026-10-22.md`](audit/pension_and_format_selector_label_ingestion_2026-10-22.md)。

2020家庭疫情经济候选变量另有13个官方问卷/Codebook标签进入目录；网页直接显示“发行数据编码、路由及适用人群/分母仍待核”，两条冲突锁定选项继续空白。见[`audit/covid_economic_candidate_label_display_2026-10-22.md`](audit/covid_economic_candidate_label_display_2026-10-22.md)。

工作问卷菜单再补入28个官方类别标签；完整菜单但Codebook字段/类别不完整的FL014显示来源状态。6个CAPI派生字段及4个字段身份/编码冲突项继续空白，见[`audit/work_questionnaire_category_label_ingestion_2026-10-22.md`](audit/work_questionnaire_category_label_ingestion_2026-10-22.md)。

慢病首次诊断/知悉的日历年与年龄，以及复发中风最近事件的年/月/年龄组件，已按对应波次Codebook加入单位元数据；时间组件不合并、不推断有效范围。审计见[`audit/chronic_disease_diagnosis_time_unit_review_2026-10-22.md`](audit/chronic_disease_diagnosis_time_unit_review_2026-10-22.md)和[`audit/recurrent_stroke_timing_unit_review_2026-10-22.md`](audit/recurrent_stroke_timing_unit_review_2026-10-22.md)。

同轮另复核了2011 FN064/FN070八个预期待遇阈值字段：保持类别与阈值标签；受控表显示FN064存在路由/格式选择器不一致，FN070展开回答缺少格式选择器，支付形式和完整序列仍不明，八项继续锁定且不作金额处理。见[`audit/pension_2011_fn064_fn070_storage_route_review_2026-10-22.md`](audit/pension_2011_fn064_fn070_storage_route_review_2026-10-22.md)。

继续审计2013 FN036_W2、FN077_W2和FN094_W2三组区间端点：所有非空边界行符合对应问卷路线，但每组都出现仅保存单边界的记录；FN036/FN094区间记录没有支付形式选择器。FN077虽然明确元/月，端点不成对，不能当作具体待遇金额。六字段仍标DO NOT ANALYZE as numeric；详见[`audit/pension_2013_bracket_bounds_local_route_review_2026-10-22.md`](audit/pension_2013_bracket_bounds_local_route_review_2026-10-22.md)。


2011 FM019多选养老金来源题已用受控本地派生表验证选项码存储；空字符串仍无法区分未选与未施测，且发现公开问卷路由外的选择记录，因此5个来源槽保留DO NOT ANALYZE。详见[`audit/pension_2011_fm019_checkbox_storage_review_2026-10-22.md`](audit/pension_2011_fm019_checkbox_storage_review_2026-10-22.md)。 另对2011 FM039进行了本地存储核验：成对字符串上下界及代码本极大上界可复现，但FM038格式选择器在区间记录中为空；已撤回“仅金额分支”旧说明，两个区间字段继续锁定。详见[`audit/pension_2011_fm039_bracket_storage_review_2026-10-22.md`](audit/pension_2011_fm039_bracket_storage_review_2026-10-22.md)。

本轮将2011 `fm031`按官方Codebook的No Observations改为C类停用字段，保留FM032端点但不推断其可分析；详见[`audit/pension_2011_fm031_no_observations_review_2026-10-22.md`](audit/pension_2011_fm031_no_observations_review_2026-10-22.md)。

2013 `zda005_6_`按官方问卷仅列五种残疾、Codebook中额外槽只有13条“No”且无“Yes”类别，转为C类源质量元数据，未映射P字段由35降至34；已在网站保留具体解释并排除关联矩阵，见[`audit/phantom_disability_slot_2013_review_2026-10-22.md`](audit/phantom_disability_slot_2013_review_2026-10-22.md)。

本轮正确使用2011基线问卷更正DE010–DE012：它们是四个领域（疼痛、睡眠、行动、认知）标准化健康锚定情景中的睡眠题，转C类，排除个人表型矩阵；2011 BA005的二元返家题与Codebook相符，撤销旧来源错误留下的分析锁定，仍与2013三档题分开。剩余89条锁定字段及关闭证据见[`audit/do_not_analyze_triage_2026-10-22.md`](audit/do_not_analyze_triage_2026-10-22.md)。

个人其他投资收入审计：2011/2013 HC023/HC024按同一过去一年、个人层级题意设两个跨波候选概念；2011负最小金额待发行版字典核实；2015 Codebook No Observations字段转C类。2013 GA004单位选择字段审计见`audit/2013_individual_transfer_income_unit_selector_review_2026-10-22.md`。详见[`audit/other_investment_income_2011_2015_review_2026-10-22.md`](audit/other_investment_income_2011_2015_review_2026-10-22.md)。
土地出租审计：2011/2013/2015按耕地、林地、牧场、水塘分别映射家户层HA060金额；2018四字段按主要受访者/配偶口径单列，2015无观测父项转C。见[`audit/land_rental_income_2011_2018_review_2026-10-22.md`](audit/land_rental_income_2011_2018_review_2026-10-22.md)。
固定资本资产审计：HA066–HA068新增43个候选概念，覆盖2011–2018农用固定资本所有权/估值及其他生产性资产；家户、本人/配偶与两人产权份额分开，2018农用飞机单位保留万元；2015无观测父项/格式项列C。详见[`audit/fixed_capital_asset_exposure_review_2026-10-22.md`](audit/fixed_capital_asset_exposure_review_2026-10-22.md)。
家庭借贷与负债审计：2011/2013 HA069–HA072映射为4个家户候选概念，2015同组无观测字段转C；HA073区间回退题仅作回答协议元数据。详情见[`audit/household_lending_debt_exposure_review_2026-10-22.md`](audit/household_lending_debt_exposure_review_2026-10-22.md)。
本轮新增亲属背景候选：2013受访者生父当前婚姻状态，以及2015受访者生父/生母少数民族身份与族别。全部按Parent长表亲属关系、官方跳题与值标签处理；详情见[`audit/parent_marital_ethnicity_review_2026-10-22.md`](audit/parent_marital_ethnicity_review_2026-10-22.md)。网站目录保留全部搜索类别；当前有12个字段身份跨类别重复展示，完整类别键下没有重复行。
本轮还新增过去一年家户低保金额候选，映射2011 `gd001_c`和2013/2015 `gd001`；已按官方问卷区分2011金额资格题和2013/2015不适用填零规则。详见[`audit/household_dibao_amount_review_2026-10-22.md`](audit/household_dibao_amount_review_2026-10-22.md)。
家户GD003的捐助、征地补偿、住房拆迁补偿来源勾选项与各自金额字段分开索引；共同None选项列C类元数据，非勾选/缺失存储仍须获准的数据字典确认。详见[`audit/household_transfer_receipt_review_2026-10-22.md`](audit/household_transfer_receipt_review_2026-10-22.md)。
模块限定字段匹配、重复源项与2015血检独立发布标识的收尾审计见[`audit/module_qualified_source_identity_review_2026-10-22.md`](audit/module_qualified_source_identity_review_2026-10-22.md)。

2026-10-22：2018 `ga000_w4`与2020 `gb001`家庭财务回答者字段依据官方问卷/Codebook改列C类回答来源元数据，排除于E/P关联矩阵；2018特殊码待发行字典确认，见[`audit/financial_respondent_source_review_2026-10-22.md`](audit/financial_respondent_source_review_2026-10-22.md)。
2026-10-22人口学类复核新增历史学历与条件婚期候选（2013 `bd001_w2_3`、`be004_1/_2`），并将9个身份证/户口本生日及预载核验字段、2020 `xrresidencesurveyhome`改列C类；字段路由、单位和隐私限制见[`audit/education_marriage_history_2013_review_2026-10-22.md`](audit/education_marriage_history_2013_review_2026-10-22.md)与[`audit/demographic_preload_birthdate_surveyhome_roles_review_2026-10-22.md`](audit/demographic_preload_birthdate_surveyhome_roles_review_2026-10-22.md)。 2013户口类型/登记地变化史新增条件性原因、状态与年份候选，户口原因类别保留农业/非农业路线差异；3个“其他，请注明”开放文本字段转C类。问卷跳转与不分析边界见[`audit/hukou_transition_2013_remainder_review_2026-10-22.md`](audit/hukou_transition_2013_remainder_review_2026-10-22.md)。 2013/2015受访者生物学父母学历按父母身份分别列为早期家庭SES代理候选，其他亲属槽位未混入；见[`audit/biological_parent_education_exposure_review_2026-10-22.md`](audit/biological_parent_education_exposure_review_2026-10-22.md)。

本轮新增家庭房产出售所得用途的2013/2015候选映射54条；问卷要求用途比例但发布字段目录未识别比例组件，所有选项槽均标记DO NOT ANALYZE，详见[`audit/household_sale_proceeds_allocation_mapping_review_2026-10-21.md`](audit/household_sale_proceeds_allocation_mapping_review_2026-10-21.md)。

历史阶段快照（其数字早于本文顶部的最新重建口径，仅作历史记录）：候选E/P概念1,160个（E侧895、P侧274、双角色9）；E/P来源链接5,897条全匹配；全来源crosswalk6,055条（C158，155条匹配、3条目录外权重/资格元数据）；网站目录7,818行（E/P7,205、C613）。养老金映射1,042条/257个概念，未归类字段序列202条（不是独立指标）。波次元数据共现对：2011=97,963、2013=96,271、2015=102,072、2018=79,985、2020=11,398；不是样本量。2013/2015/2018 `FN038_w2`现映射为计划特定最早领取资格年龄，见[`audit/pension_earliest_employer_exit_benefit_age_review_2026-10-21.md`](audit/pension_earliest_employer_exit_benefit_age_review_2026-10-21.md)；商业养老金开始缴费日期的路由与月份编码见[`audit/pension_commercial_contribution_start_date_review_2026-10-21.md`](audit/pension_commercial_contribution_start_date_review_2026-10-21.md)；2018 FN065年龄/等待年数单位选择见[`audit/pension_2018_expected_receipt_timing_unit_selector_review_2026-10-21.md`](audit/pension_2018_expected_receipt_timing_unit_selector_review_2026-10-21.md)。近期纠正预期待遇时间及金额单位选择器为C，拆分年龄/等待年数、月金额/工资比例；2013/2018缴费要求题保留冲突审核状态。2013 FN078及2013–2018征地养老金FN079_W2_8年龄/年数选择器拆分见[`audit/pension_expected_claim_timing_selectors_2013_2018_review_2026-10-21.md`](audit/pension_expected_claim_timing_selectors_2013_2018_review_2026-10-21.md)。土地征收经历/年份和征地养老金金额选择器审核见[`audit/pension_land_requisition_history_2013_2015_review_2026-10-21.md`](audit/pension_land_requisition_history_2013_2015_review_2026-10-21.md)。2011代理访谈/问卷协助字段的C类修正见[`audit/proxy_interview_metadata_2011_review_2026-10-21.md`](audit/proxy_interview_metadata_2011_review_2026-10-21.md)。2011商业养老保险按年缴费金额与所需缴费年限审核见[`audit/commercial_pension_annual_contribution_2011_review_2026-10-21.md`](audit/commercial_pension_annual_contribution_2011_review_2026-10-21.md)。2011商业缴费者、缴费方式及计划缴费年限定义见[`audit/commercial_pension_and_plan_contribution_2011_review_2026-10-21.md`](audit/commercial_pension_and_plan_contribution_2011_review_2026-10-21.md)。实际领取年月/当前月待遇路由和波次特殊码审计见[`audit/land_requisition_pension_current_benefit_2013_2018_review_2026-10-21.md`](audit/land_requisition_pension_current_benefit_2013_2018_review_2026-10-21.md)。2011–2015 FL020离职原因16项多选映射及编码限制见[`audit/work_exit_reasons_2011_2015_mapping_review_2026-10-21.md`](audit/work_exit_reasons_2011_2015_mapping_review_2026-10-21.md)。2011 FJ001–FJ003侧业字段按FC019=1路由已新增三个2011专属候选（见audit/side_job_fields_2011_mapping_review_2026-10-21.md）；DE010–DE012现按P候选显示但锁定不得分析，待核实题目身份，详见[`audit/codebook_only_sleep_severity_2011_identity_review_2026-10-21.md`](audit/codebook_only_sleep_severity_2011_identity_review_2026-10-21.md)。当前欠薪状态与金额HC033/HC034映射见[`audit/unpaid_wage_arrears_2011_2018_review_2026-10-21.md`](audit/unpaid_wage_arrears_2011_2018_review_2026-10-21.md)。2013–2018工资扣款组件、单位选择器及跨波限制见[`audit/personal_wage_deductions_2013_2018_review_2026-10-21.md`](audit/personal_wage_deductions_2013_2018_review_2026-10-21.md)；2011/2013继承来源及金额字段边界见[`audit/inheritance_transfer_2011_2013_review_2026-10-21.md`](audit/inheritance_transfer_2011_2013_review_2026-10-21.md)；主观绝对/相对生活水平指标及情景题边界见[`audit/subjective_living_standard_2011_2013_review_2026-10-21.md`](audit/subjective_living_standard_2011_2013_review_2026-10-21.md)；2018诈骗尝试与财物损失字段见[`audit/fraud_exposure_2018_review_2026-10-21.md`](audit/fraud_exposure_2018_review_2026-10-21.md)；HD001/HD003贷款与信用余额的跨波边界见[`audit/unpaid_debt_balance_2011_2018_review_2026-10-21.md`](audit/unpaid_debt_balance_2011_2018_review_2026-10-21.md)。2013 `GA002`按年/月工资金额单位选择器列为C类；详见`audit/wage_amount_unit_selector_2013_review_2026-10-21.md`。2015年HC039_W3/HC040_W3应收款字段与Codebook标签冲突，目录锁定DO NOT ANALYZE，详见`audit/private_lending_receivable_2015_2018_review_2026-10-21.md`。2011八个DA010“以上皆无”字段已接回既有治疗概念但标记DO NOT ANALYZE，见[`audit/2011_disease_treatment_none_option_mapping_review_2026-10-21.md`](audit/2011_disease_treatment_none_option_mapping_review_2026-10-21.md)；网站现新增“家庭资产租赁收入”逐波检索视图。家庭其他资产租赁收入金额、状态和选择器跨波拆分见[`audit/household_other_asset_rental_income_wave_harmonization_review_2026-10-21.md`](audit/household_other_asset_rental_income_wave_harmonization_review_2026-10-21.md)；2020疫情期间家庭收入变化、财务压力与应对字段审计见[`audit/household_covid_economic_2020_review_2026-10-21.md`](audit/household_covid_economic_2020_review_2026-10-21.md)。模型0，未读取个体数据。完整现状见[`audit/current_directory_snapshot_2026-10-22.md`](audit/current_directory_snapshot_2026-10-22.md)，专题审计见`audit/`，许可边界见[`audit/DATA_ACCESS_AND_REPRODUCTION.md`](audit/DATA_ACCESS_AND_REPRODUCTION.md)。


2020 CAPI派生工作状态/年化副业量的公式及限制见[`audit/capi_work_derived_variables_2020_review_2026-10-21.md`](audit/capi_work_derived_variables_2020_review_2026-10-21.md)；更正后的2011养老金年月字段与原始跳题路径见[`audit/pension_2011_unmatched_date_components_review_2026-10-21.md`](audit/pension_2011_unmatched_date_components_review_2026-10-21.md)。

工作暴露目录本轮新增就业组织、非农工作安排、雇主福利与农户雇主数候选，并修正2011问卷来源引用；详见[`audit/current_work_organization_field_review_2026-10-21.md`](audit/current_work_organization_field_review_2026-10-21.md)。

2011问卷误标来源的影响、已修正构建脚本以及仍待逐项复核的专题清单见[`audit/2011_questionnaire_source_identity_correction_2026-10-21.md`](audit/2011_questionnaire_source_identity_correction_2026-10-21.md)。2011 `BA005`已修正为与2013三档频率分开的二元每周返家候选。


本轮新增2011/2013家户住房装饰/装修支出候选；2015同名字段因官方Codebook标记No Observations而排除，见[`audit/household_renovation_expenditure_review_2026-10-21.md`](audit/household_renovation_expenditure_review_2026-10-21.md)。2011 GE003回答者角色转为C类元数据。


本轮还将GB010四波家户牲畜/水产购买支出映射为独立农业购买流量，见[`audit/household_agricultural_production_review_2026-10-21.md`](audit/household_agricultural_production_review_2026-10-21.md)。


2011/2013/2015家户社会捐助、征地补偿和住房拆迁补偿金额现按三类概念分开映射；条件路由和零值限制见`audit/household_transfer_compensation_review_2026-10-21.md`。


2011 DE007–DE009、DE013–DE018是对假设人物的健康评价，已依据官方问卷改列C类锚定情景元数据并加入五级响应标签；详见`audit/health_anchoring_vignette_metadata_review_2026-10-21.md`。

2013/2015认知词表题组中的DC008经官方问卷确认为CAPI记录的时钟时间，已列为C类施测元数据，见`audit/cognition_unassigned_series_triage_v1.md`。

2011/2013首次工作时间父项FB001现作为C类单位选择器（年龄/日历年），原年龄/年份子字段保留，暂不自动换算；见`audit/lifecourse_timing_selector_review_2026-10-21.md`。

2018 FC013为健康原因造成的自家农业工作缺勤单波表型候选，与2013同码题分开；其路由和范围差异见`audit/health_work_absence_2018_review_2026-10-21.md`。


2026-10-22：补入2013/2015家户月度GE009家政/佣工、当地交通、娱乐支出六条字段链接，0与-9999按问卷指示区分，见[`audit/household_monthly_expenses_2013_2015_review_2026-10-22.md`](audit/household_monthly_expenses_2013_2015_review_2026-10-22.md)。

2026-10-22：2013/2015当前住房HA011总价与单位面积价格拆为不同候选概念、HA011父字段为C类单位选择器，见`audit/current_home_market_value_2013_2015_review_2026-10-22.md`。其中2015 HA007=3时跳过估价题；不把总价与元/平方米口径合并，旧房当时价值、多套房槽位及估值区间留待单独核实。

2026-10-22 additions: see the financial-respondent, monthly household expenditure, current-home market value, and demographic record/hukou location audits dated 2026-10-22.

2026-10-22社区灾害开放文本复核：2011 `ji002_other`为“其他灾害请注明”文本，不是标准暴露类别；从E候选移列C类元数据，禁止公开文本或纳入E/P矩阵。见[`audit/community_other_disaster_open_text_review_2026-10-22.md`](audit/community_other_disaster_open_text_review_2026-10-22.md)。

历史快照（已被2026-10-22最终全量重建取代）：早期审计曾记录E/P/C未连接字段队列，后续逐项复核并完成角色调整。当前状态以本文顶部为准：未映射E/P均为0；C类字段用于测量、路由及来源元数据，不进入关联配对。早期队列证据仍保存在audit/unassigned_catalog_series_review_v1.md，仅供追溯，不应作为当前待办清单。

目标人群必须按波次解释：2011–2018的刷新样本补入使各波可评估45岁以上的横截面总体；2020 Wave 5手册指出2018年后较年轻队列不再具全国代表性，不能仅凭权重宣称覆盖全部45岁以上。2020目标年龄域仍待官方样本信息与权重源文件校验，哈希及核验步骤见[`audit/wave5_sampling_file_source_verification_2026-10-22.md`](audit/wave5_sampling_file_source_verification_2026-10-22.md)。详见[`audit/wave_specific_target_population_and_age_coverage_2026-10-22.md`](audit/wave_specific_target_population_and_age_coverage_2026-10-22.md)及网站“逐波目标人群”说明。

2026-10-22养老金续审：2013 `fn064_w2_2_`接入既有居民养老转入来源概念，值码1–3按官方Codebook核对，严格保留FN063_w2=Yes条件路径；2015同码只见单一标签，留待获批字典确认。审计audit/pension_resident_transfer_source_2013_2015_review_2026-10-22.md。当时目录链接数6,255，全来源crosswalk 6,431（后续养老金区间映射见最新状态），2013共现对111,294（元数据可用性，不是样本量）。

2026-10-22：FN098子女名单链接字段复核后，2013/2015/2018共50个槽位转为C类元数据；FN097老年经济支持来源仍为E候选。最新目录7,408行（E/P 6,660、C 748；唯一身份7,396）；空Concept ID队列E 326/239码、P 35/35码、C 582/402码。详见`audit/child_roster_old_age_support_selector_review_2026-10-22.md`。

2026-10-22续审：2015 Codebook将GA004旧年度/月度拆分18槽标记“No Observations”，转列C类inactive legacy metadata；E/P候选源金额字段保留。当前目录7,408行（E/P 6,660、C748；唯一身份7,396）；未映射E320/233码、P35/35、C584/404。详见`audit/inactive_2015_individual_transfer_income_slots_review_2026-10-22.md`。

2026-10-22养老金区间续审：12个2011金额上下界字段接入已有待遇金额概念，未新增概念；FN045另2条无观测槽转C。当前E/P字段链接6,271，全crosswalk6,447，目录E/P6,660/C748；空Concept队列E320/233、P35、C584/404。见`audit/pension_2011_unfolding_bracket_bounds_review_2026-10-22.md`。


2026-10-22 2011养老金路由精确区分及目录更新：FN015/FN016确认属于当前领取者（FN002=4），新建路由专属概念；FN065/FN066属于已参保者（FN039=4），与2013 FN063_W2/FN064_W2共用已参保路线概念。FN048父字段按官方问卷/Codebook转为C类格式元数据，fn048_1/2保留独立E概念。完整目录重建成功：7,454字段行（E 4,609、P 1,861、C 820、双角色164），1,378候选概念，6,459来源链接，6,636全源crosswalk其中6,624匹配、12个C元数据未匹配；波次字段元数据共现2011=115,500、2013=117,960、2015=120,216、2018=94,393、2020=12,598（非样本量）。网站JS语法检查通过。未读取微观数据、未运行关联分析。具体审计见 `audit/pension_2011_fn015_fn016_source_identity_conflict_review_2026-10-22.md`、`audit/pension_2011_residual_review_2026-10-22.md`。


2026-10-22 2013养老金残余字段复核：FN007单位来源、FN009来源单位类型、FN010来源单位粗空间关系、FN031企业补充养老金参保地、FN044商业养老金参保地、FN059三类社会养老金参保地，按官方问卷/Codebook映射为带路线的E候选；问卷选项标签包含Codebook未观测类别，但不含频数。FN016_W2省份、FN056_W2_6缴费周期选择器、FN056_W2_9待遇金额格式选择器及FN056_W2_3_1开放文本均按规则转为C。FN036/FN077/FN094的6个字符串Min/Max Bracket字段单独链接为区间边界并锁定DO NOT ANALYZE as numeric。重建后2013未映射E=0；全目录7,454字段行（E 4,605/P 1,861/C 824/双角色164），候选概念1,387（E 1,117/P279/双角色9），来源链接6,476，全crosswalk6,653行/6,641匹配/12个C未匹配。目录元数据共现2011=115,500、2013=119,778、2015=120,216、2018=94,393、2020=12,598（非样本量）；网站JS检查通过。审计见 `audit/pension_2013_residual_review_2026-10-22.md`。


2026-10-22续审：2015 `fn064_w2_1_2_`/`fn064_w2_1_3_`按计划路线审查。受控本地表显示非空字段都对应转入状态与企业养老金来源；官方Codebook标题单位为年，但两个字段均以字符串发布，且一个字段有不可数值解析文本。继续保留文本并锁定数值分析，等待官方编码/特殊文本解释。审计见[`audit/pension_2015_transfer_year_string_storage_review_2026-10-22.md`](audit/pension_2015_transfer_year_string_storage_review_2026-10-22.md)。

2026-10-22内部生物标志物角色边界已补充至血检目录：字段页面提示16项化验为已审P角色；目录搜索中的自动E/P标签是待复核发现项，不等于已批准暴露链接。2011胱抑素C权重资格和跨波原始值可比性限制分别展示。详见`audit/internal_biomarker_role_review_2026-10-22.md`和`audit/blood_biomarker_definition_review_v1.md`。


2026-10-22补审：11个吸烟/饮酒开始或停止时间格式选择器已按波次官方标签转为C类元数据，排除于E/P关联矩阵；选择器相邻的年龄/年份回答组件仍保留。详见[`audit/behavior_age_year_selector_metadata_role_review_2026-10-22.md`](audit/behavior_age_year_selector_metadata_role_review_2026-10-22.md)。


2026-10-22数据准备脚本QA加固：2013官方权重文件缺少`crosssection`或`longitudinal`时现在会失败关闭，避免产生缺失官方样本资格标志的派生表；新增合成测试覆盖标志保留、冲突、相同重复行及标志缺失。测试不读取CHARLS个体数据。详见`audit/prepared_wave_design_field_audit_2026-10-22.md`。


本机受控数据状态复核（2026-10-22）：LocalAppData中存在五波已准备分析表，但对应五波原始CHARLS发行包当前不在本机受控数据根目录，桌面旧原始数据路径也不存在；因此本轮仅重跑汇总级样本设计审计，不重建任何个人表。`audit/survey_design_field_coverage_v1.csv`现有54条波次—设计字段汇总：五波均有communityID和权重字段，2015/2018/2020有crosssection/样本标记，当前2013派生表缺crosssection/longitudinal，2011/2013亦未检出相同样本标记；各波均未发现显式方差分层变量。不得从权重非缺失推断样本资格。原始包路径、权重来源版本与2013标记恢复仍是本机分析重建前置项。


2026-10-22续建2014 Life History独立回顾性候选目录：官方字段映射18概念组、471行（E 466 / P 5）；生命历程样本无权重且含特殊样本构成，不纳入常规波次配对/加权关联框架。页面和复现材料见 [`audit/life_history_exposure_mapping_review_2026-10-22.md`](audit/life_history_exposure_mapping_review_2026-10-22.md)。


2026-10-22生命历程字段差集补审：补入T004逐段城乡模式25个字段、T003c迁出原因13选项×25段居住履历的325个字段，以及A7/A10/A10_1父母离异及发生年龄；合计18概念组/471字段行（E 466、P 5）。循环/选项字段只按概念组归并，不当作数百个独立暴露；迁出多选的存储方式待获准原始数据核验。详见Life History映射审计。


2026-10-22候选概念链接审计：核实并分类全部3个未决多概念源字段链接，剩余32个共享字段均已有关系类型；修正父母教育记录分层解释，并将2018同题的两个工作规模候选ID显式合并为别名。概念总数和2018元数据共现已刷新。见 [`audit/concept_overlap_resolution_2026-10-22.md`](audit/concept_overlap_resolution_2026-10-22.md)。


行为暴露共享题关系补审：DA067（2020 DA051）过去一年饮酒原始频率三分类与“是否饮酒”二元概念现明确标为派生关系；1/2派生Yes、3派生No，未把它们当作独立暴露，也保留缺失/路由状态。复核细节见 `audit/concept_overlap_resolution_2026-10-22.md`。


体力活动共享字段审计：官方问卷将不同强度的发生题分别记录；`physical_activity_occurrence`是分组上位概念，没有独立的总体活动响应。现将10个共享链接标为`umbrella_group_not_independent_measure`，任何“至少一类活动”变量须按预设规则从符合资格的强度题派生；2011随机半数家庭施测限制保留。见`audit/concept_overlap_resolution_2026-10-22.md`。

2011、2013、2015、2018四波慢病治疗选项目录分别补入53、52、52、68个字段的官方Codebook类别文字。频数不进入网站；2011–2015字段的未选存储未核、暂不可分析，2018字段仍需验证发行版编码和适用分母。标签目录不代表这些字段已进入模型。详见[audit/chronic_disease_ancillary_label_ingestion_2026-10-22.md](audit/chronic_disease_ancillary_label_ingestion_2026-10-22.md)。

本轮2018慢病治疗标签更新已发布：`190837f`对应的GitHub Pages部署成功，线上目录已包含68个官方类别标签；频数不公开，路由和发行版编码/分母待核说明保留。网站仍是元数据原型，没有关联模型结果。发布核查见[`audit/github_pages_publication_review_2026-10-22.md`](audit/github_pages_publication_review_2026-10-22.md)。


### 网站方法说明更新（2026-10-23）

主页现逐波概述横截面/纵向样本标记、专用测量权重、2013准备表需恢复官方标记、2020代表性年龄边界，以及方差分层字段仍待核验等限制。页面将 `communityID` 标为 PSU 候选而非已完成的全设计复现，并链接至 [`audit/survey_design_weight_review_v1.md`](audit/survey_design_weight_review_v1.md)。没有发布个体数据或关联估计。


### 当前页面状态更新（2026-10-23）

逐波权重、样本标记和方差设计限制已显示在主页“数据与方法说明”卡片中；主导航中的“测量与设计元数据”会打开 C 类目录。候选配对页可按波次和概念查看来源字段、标签及边界，关联结果页目前明确显示尚无已审真实结果。详情见[`audit/github_pages_publication_review_2026-10-22.md`](audit/github_pages_publication_review_2026-10-22.md)。


2026-10-23网站加载优化：主页不请求目录JSON；专题目录、候选配对索引及E/P/C角色分片按需加载，主目录仅用于仓库构建/审计且不会进入Pages部署包。各静态JSON使用ETag重新验证缓存。测量结果、构建步骤和测试见[`audit/site_static_asset_cache_review_2026-10-23.md`](audit/site_static_asset_cache_review_2026-10-23.md)。

2026-10-23专题目录同步：饮食/环境专题35条、社交/家庭联系专题184条源字段现在会显示主目录中已审核的官方值标签及其出处/审核状态；仅唯一波次—字段码匹配时填入，已有文本和冲突项受保护。重建报告见[`site-prototype/dist/domain_label_sync_report.json`](site-prototype/dist/domain_label_sync_report.json)，方法与验证见[`audit/domain_catalog_label_sync_2026-10-23.md`](audit/domain_catalog_label_sync_2026-10-23.md)。正式关联模型仍为0。

2026-10-23核心配对可用性门控：私有QA脚本现在逐波读取并应用横截面标记；当前2013派生表缺少官方`crosssection`和`longitudinal`，因此99个核心概念组合的配对N全部留空。重新运行准备表验证器结果为2013 `CHECK`，其余四波`PASS`。2011未见独立标记，输出只标记为基线表可用性；2015/2018/2020按`crosssection=1`筛选。所有此类非缺失计数仍未处理权重、模块路由、特殊码或模型排除，不能当作分析样本量。细节见[`audit/core_availability_sample_frame_gate_2026-10-23.md`](audit/core_availability_sample_frame_gate_2026-10-23.md)。

2026-10-23目录来源展示复核：客观测量、住房编码和2020疫情家庭经济目录现在在表格说明列展示来源文档及审核/映射状态，方便追溯官方材料；不改变字段分类或分析资格。


2026-10-23住房产权份额续审：2018年5个当前住宅产权关系份额字段已标为连续百分比，网站明确保留关系槽位、不可直接相加、问卷路由和特殊值仍待授权发行版核验；不展示Codebook摘要极值或频数。E目录通用待核现为611；另8个面积、租金、住房估值和取得时间字段已补入单位与问卷路由边界；95项Python测试通过。审计记录：[`audit/housing_current_owner_share_2018_review_2026-10-23.md`](audit/housing_current_owner_share_2018_review_2026-10-23.md)及[`audit/housing_current_home_measurements_2018_review_2026-10-23.md`](audit/housing_current_home_measurements_2018_review_2026-10-23.md)。


2026-10-23住房计数续审：15个五波卧室、起居室和厕所计数字段已补入官方题意、计数单位、住宅对象及软性范围检查说明；E目录通用待核现为596。详见[audit/housing_room_count_measure_review_2026-10-23.md](audit/housing_room_count_measure_review_2026-10-23.md)。


2026-10-23更新：更正2018 HA004住房价值字段顺序。现在公开目录按官方问卷正确区分总价（7个槽位，10,000 Yuan）与单位面积价（5个槽位，1,000 Yuan/square metre），并将7个格式选择器列为C类元数据；全量重建与108项测试通过。详见[`audit/household_property_value_2018_slot_unit_review_2026-10-23.md`](audit/household_property_value_2018_slot_unit_review_2026-10-23.md)。


2026-10-23住房金额题组更新：补审2011/2013/2015共40条住房购建与市场价值金额字段，目录记录官方问卷单位及连续测量状态，不将Codebook摘要频数/极值用作数据或清洗范围。E住房类通用待核现为0；发行版存储倍率和特殊值仍待授权数据核验。详见[`audit/housing_numeric_value_metadata_review_2026-10-23.md`](audit/housing_numeric_value_metadata_review_2026-10-23.md)。


2026-10-23家庭房产出售所得用途复核：修正10月21日审计遗漏。2013/2015官方Codebook分别列出按用途和房产槽拆分的54个百分比数值字段，以及54个选项索引字段；另有4个“Specify Usage”自由文本字段。百分比字段作为独立E候选概念加入主目录与候选配对数据，但全部DO NOT ANALYZE，待获准发行版核对字段身份、选择器/类别对应、房产槽路由、特殊值和值域及有效分母。选择槽转C类、自由文本仅留C元数据且不公开文本。当前角色分片E/P/C为4,723/2,067/979行，锁定项89条；全量/收尾构建、锁定清单一致性和111项测试均已通过。审计见[`audit/household_sale_proceeds_allocation_mapping_review_2026-10-23.md`](audit/household_sale_proceeds_allocation_mapping_review_2026-10-23.md)。

2026-10-23父母探访类别标签更新：33个2011–2018波次字段加入官方逐字段有序类别，其中27个字段类别集完整、6个字段保留Codebook已列部分类别；Codebook频数不进入网站，未推断缺项或跨波类别。后续DA056选项边界和124个家户成员金额字段也已同步。当前E/P有3,315行非空官方/已审标签（3,238波次字段），E通用待核204行，C通用待核328行。118项测试及89条禁分析锁校验通过；当前审计队列见[`audit/current_value_label_review_queue_2026-10-23.md`](audit/current_value_label_review_queue_2026-10-23.md)。


DA056选项编码边界更新（2026-10-23）：41个2011/2013/2015活动与设备选项字段已同步官方Codebook选项身份及源文件，但未验证个人级存储和未选中状态，网站不填响应类别，并明确空缺不可解释为No。E目录通用待核204，C目录328；详见[`audit/social_code_value_review_v1.md`](audit/social_code_value_review_v1.md)。


家户成员金额字段更新（2026-10-23）：124个2011、2013、2015年度/月度工资及2011养老金等金额槽位已加入官方问卷确认的元/年或元/月单位，并保留家庭名册和波次题意，不把金额归属到主受访者或将槽位求和。剩余存储尺度、特殊值、路由和受访者链接须继续审核。审计见[`audit/household_member_income_amount_review_2011_2015_2026-10-23.md`](audit/household_member_income_amount_review_2011_2015_2026-10-23.md)。

家庭支出字段更新（2026-10-23）：53个2011–2020波次字段已按官方问卷补入家庭层级、周/月/年参考期和元单位；4个自产品指标采用Codebook明确的`1=Yes; 2=No`，金额字段不虚构类别。E通用待核降至151，P为0、C为328；E/P官方/已审非空值标签为3,212行、3,186个波次字段。完整范围及限制见[`audit/household_expenditure_metadata_review_2011_2020_2026-10-23.md`](audit/household_expenditure_metadata_review_2011_2020_2026-10-23.md)和[`audit/current_value_label_review_queue_2026-10-23.md`](audit/current_value_label_review_queue_2026-10-23.md)。121项测试和89条禁分析锁校验通过。

个人转移收入来源更新（2026-10-23）：50个五波次选项字段按官方问卷/Codebook审核。2011–2015只确认到选项身份，未推断未选中为No；2018/2020的20个字段显示明确的`0=No`及选项码`=Yes`，不复制频数。养老金区间端点更新：16个2011/2013/2015下界/上界字段说明为条件金额区间，不是点估计；2013字符串类型、2015代码本摘要和2011区间路由分别记录。当前E通用待核85、P为0、C为328；E/P非空官方/已审值标签3,232行、3,206个波次字段。128项测试、JS语法和89条禁分析锁检查通过。审核记录见[`audit/individual_transfer_income_source_review_2011_2020_2026-10-23.md`](audit/individual_transfer_income_source_review_2011_2020_2026-10-23.md)、[`audit/pension_interval_endpoint_review_2011_2015_2026-10-23.md`](audit/pension_interval_endpoint_review_2011_2015_2026-10-23.md)和[`audit/current_value_label_review_queue_2026-10-23.md`](audit/current_value_label_review_queue_2026-10-23.md)。


核心调整候选和逐波准备限制汇总见[`audit/core_covariate_readiness_2026-10-23.md`](audit/core_covariate_readiness_2026-10-23.md)。年龄、性别、教育、婚姻/伴侣、户籍、居住地和抽样设计分别核验；目录中的456条自动发现C波次字段线索（300个不同变量码）不等于固定调整变量，正式模型仍为0。
