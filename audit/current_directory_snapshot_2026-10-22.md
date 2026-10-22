# CHARLS ExWAS Atlas 当前目录快照（2026-10-22）

## 当前目录

本快照统计公开字段元数据与人工审核映射；未拟合ExWAS关联模型。最新重建扩展2018 HCAP及跨波官方认知标签；将拒答原因、测验工具及施测条件共15字段列为C类，并保留连续认知原始值的有效范围限制；新增慢病辅助题审定标签并消除DA020S2注释文本冲突；工作类复选框及问卷菜单共81个新标签展示，保留未选中/路由/代码本遗漏限制；新增收入/借贷/养老类别标签、养老金参与/资格标签、4个C类金额/日期选择器以及2020家庭疫情经济13个待发行版核实标签；未将个人记录或标识符写入项目材料或交接包。

- 逐波字段目录：7,544行（E 4,566、P-only 1,903、C 911、E/P双角色164）。
- 去重候选概念：1,408个（E侧1,130、P侧287，双角色概念9个）。
- E/P概念—源字段映射：6,598条；全来源crosswalk 6,804条，其中6,792条匹配目录，12条是目录外C类元数据。
- 2011/2013/2015/2018/2020波次目录概念对共现：120,052 / 126,301 / 128,984 / 98,667 / 12,598。
- 当前未映射E/P字段均为0。11个吸烟/饮酒年龄/年份格式选择器已转为C类并排除于关联矩阵；相邻回答组件保留并须按波次选择器解释。C类字段保留测量、问卷路由、回答历史、来源身份等元数据，不进入E/P关联配对。
- E/P目录现有2,834行含非空值标签（2,808个波次—字段码）；2013 `fn056_w2_5`的问卷选项/CodeBook类别表覆盖差异已复核，精确标为`conflict`的字段码为0；2011 `FB010`问卷与Codebook编码差异另行确认并标记`DO NOT ANALYZE`；FL020 16个选项的问卷含义已列出，但选中/未选中/缺失码未证实，均保持锁定。慢病辅助crosswalk的84条非空标签已全部精确连接至主目录；工作复选框/菜单新增81个标签，收入/家庭借贷/养老新增7个，养老金参与/资格新增16个，2020家庭疫情经济新增13个标签。另在C类展示2018四个格式/日期选择器。依据见[`chronic_disease_ancillary_label_ingestion_2026-10-22.md`](chronic_disease_ancillary_label_ingestion_2026-10-22.md)、[`work_checkbox_value_label_ingestion_2026-10-22.md`](work_checkbox_value_label_ingestion_2026-10-22.md)、[`work_questionnaire_category_label_ingestion_2026-10-22.md`](work_questionnaire_category_label_ingestion_2026-10-22.md)、[`additional_income_debt_pension_label_ingestion_2026-10-22.md`](additional_income_debt_pension_label_ingestion_2026-10-22.md)、[`pension_and_format_selector_label_ingestion_2026-10-22.md`](pension_and_format_selector_label_ingestion_2026-10-22.md)和[`covid_economic_candidate_label_display_2026-10-22.md`](covid_economic_candidate_label_display_2026-10-22.md)。
- 正式关联模型数为0；未计算关联效应或个人级配对样本量。目录另有33条逐波字段带DO NOT ANALYZE锁定；2011 FM033已依据官方类别和受控存储核查移出旧的菜单冲突锁定，作为路线专属分类候选，并保留一个问卷选项无Codebook观测的警示。锁定字段仍可检索，但不得进入模型。逐字段和所需证据见[`do_not_analyze_triage_2026-10-22.md`](do_not_analyze_triage_2026-10-22.md)。

2026-10-22续核：2015 Wave 3官方发布页列出的Codebook及问卷版本与本地PDF校验值一致。发布页/发布说明没有给出`fn057_w3_4_1_`至`_3_`问卷—Codebook字段名冲突的勘误，故维持锁定；`ha065_1_18_`身份冲突也未获官方说明。详情见[`pension_2015_residual_review_2026-10-22.md`](pension_2015_residual_review_2026-10-22.md)和[`2015_inactive_income_housing_asset_fields_review_2026-10-22.md`](2015_inactive_income_housing_asset_fields_review_2026-10-22.md)。

## 方法和设计闸门

目标仍是按波次构建CHARLS暴露—表型探索目录，后续分析需定义 estimand、分析单位、样本资格及变量的答案/缺失/跳题规则。不能以变量字段数追平NHANES，也不能把问卷组件、波次版本、答案历史标志或测量流程计为独立暴露/结局。

逐波横断面估计和纵向估计必须分开定义。本机受控派生表已含多个波次的权重、`crosssection`和`communityID`字段，但2013样本标志被准备脚本漏掉（已修正脚本，需从原始发行包重建），且派生表发行版本/校验值仍未登记。`communityID`是有官方依据的PSU候选；未确认实际发行文件的方差分层ID或获准替代方差方法前，不发布完整设计校正推断。不得从省份、城乡、社区ID推测抽样分层。生物标志物要按各波官方说明使用专门的响应权重。细节见[`prepared_wave_design_field_audit_2026-10-22.md`](prepared_wave_design_field_audit_2026-10-22.md)。

2020 `xmainjobdays`的Codebook字段标题和摘要统计无法解释问卷CAPI重复条件的来源变量，继续排除分析；详见[`capi_work_derived_variables_2020_review_2026-10-21.md`](capi_work_derived_variables_2020_review_2026-10-21.md)。

2026-10-22完整元数据重建后，目录、概念—源字段crosswalk、配对覆盖摘要和首页KPI已由同一构建入口刷新：目录7,544行、E/P概念1,408个、E/P链接6,598条、全来源crosswalk 6,804条；DO NOT ANALYZE字段33条，与分流清单一致。HCAP认知偏倚及最新官方类别/施测元数据复核分别见[`hcap_wave4_cognition_bias_guidance_review_2026-10-22.md`](hcap_wave4_cognition_bias_guidance_review_2026-10-22.md)和[`cognition_2018_codebook_categories_and_admin_metadata_review_2026-10-22.md`](cognition_2018_codebook_categories_and_admin_metadata_review_2026-10-22.md)。值标签扩展和连续数值边界见[`cognition_2018_codebook_label_expansion_review_2026-10-22.md`](cognition_2018_codebook_label_expansion_review_2026-10-22.md)。2011–2020逐波认知代码本差异及新增提示见[`cognition_2011_2020_wave_specific_codebook_review_2026-10-22.md`](cognition_2011_2020_wave_specific_codebook_review_2026-10-22.md)，标签导入规则修复和2020施测字段角色复核见[`cognition_label_ingestion_and_role_rebuild_2026-10-22.md`](cognition_label_ingestion_and_role_rebuild_2026-10-22.md)。中间快照`current_directory_snapshot_2026-10-22_route_audit.md`保留历史数字，不作为当前统计。

2026-10-22认知标签最终核验：认知类别字段的`not yet reviewed`由19降至0；E/P目录现有非空官方/审定标签2,678行、2,652个不同波次字段码。主目录与认知字段映射对311条非空标签连接后，现存标签冲突为0。具体修复与不推断规则见[`cognition_label_ingestion_and_role_rebuild_2026-10-22.md`](cognition_label_ingestion_and_role_rebuild_2026-10-22.md)。

2026-10-22慢病时间单位审校：112个DA009唯一波次字段按官方Codebook分为56个日历年和56个诊断年龄指标；目录C角色副本不计作新变量，并共显示168个角色行。复发中风最近事件时间增加6个P波次字段及2个同源C类角色副本，分别保留2013月份、其余波次年龄和跨波年份单位。2013第15个未列病种占位码不赋病种单位。详情见[`chronic_disease_diagnosis_time_unit_review_2026-10-22.md`](chronic_disease_diagnosis_time_unit_review_2026-10-22.md)和[`recurrent_stroke_timing_unit_review_2026-10-22.md`](recurrent_stroke_timing_unit_review_2026-10-22.md)。

详细依据见[`charls_wave_sampling_and_weight_status_2026-10-22.md`](charls_wave_sampling_and_weight_status_2026-10-22.md)及[`EXWAS_result_schema_v2.csv`](EXWAS_result_schema_v2.csv)。字段映射的原始边界与逐项审计见同目录专题审计和项目根目录`README.md`、`HANDOFF_合作者接手说明.md`。

## 下一阶段

1. 找回或重新申请原始官方发行包，修复后重建个人分析表并记录压缩包/权重/样本/PSU文件版本与哈希；尤其恢复2013 `crosssection`/`longitudinal`标志。若不做推断分析，网站保持可搜索的变量元数据图谱。
2. 从候选E/P概念中按研究问题定义分析单位和目标人群，审核跳题、特殊码、量纲、适用波次及可比性；候选映射不能直接当作模型输入。
3. 只有在设计字段和资格规则核实后，才生成逐波配对样本流程、预先规定协变量与多重检验方案，计算效应与样本量，并将经过审查的汇总结果导入网站。

## 当前网站原型

`site-prototype/dist/`提供可本地运行的检索型目录。C类结果逐字段显示角色判定、处理边界、审核状态和来源提示。网页当前没有关联结果，页面明确说明这一状态。

## 2026-10-22血液指标跨波方法学补充

CHARLS 2015血检论文提示Wave 1与Wave 3采集/运输/检测程序不同；即使指标同名同单位，也不能把原始数值直接当作纵向可比。总胆固醇、HDL-C、hsCRP和HbA1c涉及HRS家族跨实验室校准工作，但这不证明公开CHARLS字段自动含有2011/2015校正值。网站血检页现展示逐字段可比性警告。2011胱抑素C为70岁及以上全测、70岁以下随机抽样；`bloodweight`是否涵盖分析物子样本选择尚无证据，需在指标级分析前关闭此权重/抽样资格问题。详见[`audit/blood_biomarker_definition_review_v1.md`](blood_biomarker_definition_review_v1.md)。

2026-10-22内部生物标志物角色口径：宽目录的自动E/P双角色是候选搜索标签；20个相关概念在经审查crosswalk中均只有P映射（13个2011血液指标、7个2011–2015客观测量），2015独立血检模块未触发同样自动分类。专题页现解释内部生物标志物与环境污染物暴露的差异；将其作为E须说明估计目标和时间/生物学依据，不能自动作为暴露链接。见[`internal_biomarker_role_review_2026-10-22.md`](internal_biomarker_role_review_2026-10-22.md)。

2026-10-22构建复核：在字段目录、目录范围JSON和逐项锁定清单之间再次核对，最终计数仍为7,455字段、1,399候选概念、6,532条E/P源映射、6,712条全来源crosswalk、33条锁定；网站28个JSON全部生成，前端脚本语法检查通过。完整重建过程记录见[../logs/metadata_rebuild_2026-10-22.log](../logs/metadata_rebuild_2026-10-22.log)。

2026-10-22后续审计：2011社区环境crosswalk现为100个候选概念/187条字段映射，其中59条有明确离散/序数类别标签，128条为CodeBook已定位的数值/计数回答且无离散标签；早期8/38为初版子集。养老金标签冲突已从15条逐波字段降至1条，仅2013 `fn056_w2_5`季度回答的CodeBook/问卷差异仍待获批字典或官方解释。E/P目录中有标签文本2,478行、覆盖2,452个波次字段码；该标签覆盖不代表分析资格，自动报告见`audit/charls_ep_catalog_value_label_coverage_v1.md`。定点复查的本机原始数据输入目录均不存在，暂不能从源档案重建或拟合模型；CHARLS官方数据需登记签署协议后申请，详见`audit/DATA_ACCESS_AND_REPRODUCTION.md`。

2026-10-22受控派生表设计字段审计新增：更正Wave 2样本旗标在准备脚本中被遗漏的问题，待原始包恢复后重建；记录本机已有权重/样本字段与communityID、方差分层仍未确认的边界。见[prepared_wave_design_field_audit_2026-10-22.md](prepared_wave_design_field_audit_2026-10-22.md)。

2026-10-22网站值标签补漏：已将2011 da005按官方问卷/Codebook显示1=Yes; 2=No；2013同名字段保留三档回家频率标签，跨波含义不合并。最终全量重建日志见[../logs/metadata_rebuild_2026-10-22.log](../logs/metadata_rebuild_2026-10-22.log)。



2026-10-22医疗费用目录扩展：官方问卷/Codebook字段级检索新建11个医疗费用候选表型概念、93条2011/2013/2015/2018字段映射，均匹配主目录并统一归P侧；未作为环境暴露。年度保费、门诊/住院总额、自付额、药费、非医疗相关交通食宿分项展示。区间端点不当作精确金额，官方Codebook频数不作样本量。候选角色及字段路由仍需授权发布数据QA；详见`healthcare_cost_candidate_inventory_2026-10-22.md`。该段末尾数字为医疗费用专题构建时点的历史快照；专题字段均匹配目录，但它早于后续字段/Concept别名规范化，不作为当前目录统计，当前值以上方快照摘要和后续概念链接复核记录为准。

## 年龄/日历年选择器修正

2026-10-22复核将11条吸烟/饮酒时间格式选择器转列C；波次编码顺序不同，不能将选择器当有序暴露或把相邻年龄与日历年混为同一单位。见[`behavior_age_year_selector_metadata_role_review_2026-10-22.md`](behavior_age_year_selector_metadata_role_review_2026-10-22.md)。

## 本机受控数据与准备脚本状态（2026-10-22续审）

本机LocalAppData保留五波个人级准备表；该目录不属于本快照或协作者包。五波原始官方发布压缩包未在当前受控根目录，故没有据此重建。安全汇总审计读取仅限权重、样本标记、communityID及地理上下文字段，生成54条波次—字段记录；各波都有权重与communityID，2015/2018/2020具样本标记，当前2013派生表无crosssection/longitudinal，2011/2013亦未见同样的样本标记，五波均未找到显式方差分层变量。2013准备脚本现要求两项官方标记齐全，否则停止；4项合成数据测试覆盖保留、冲突、重复与缺失保护。包含全部验证步骤的设计字段审计见[`prepared_wave_design_field_audit_2026-10-22.md`](prepared_wave_design_field_audit_2026-10-22.md)。


PSU标识符证据边界补充：既存`charls_psu_mapping_aggregate_v1.csv`记录五波所有非缺失communityID均匹配官方2013 PSU映射表，逐波未匹配数均为0。该历史聚合结果证明键覆盖，不证明当前源档案哈希、跨波抽样框完全等价或复杂抽样方差方案。因官方原始ZIP/RAR目前不在受控数据根目录，须取得原件后复核。


## 2014 Life History（独立特殊调查目录）

单列回顾性候选目录：18个概念组、471条字段映射（E 466、P 5）。官方2014发布说明指出该样本无权重、包含特殊刷新/补访样本且可能有45岁以下受访者，数据为需解释循环索引的宽表。该页不计入上述五个常规波次目录统计，不进入常规波次的概念共现或加权模型；也不表示已经核验个体级字段覆盖或分析资格。映射审计见[`life_history_exposure_mapping_review_2026-10-22.md`](life_history_exposure_mapping_review_2026-10-22.md)。


T003c/T004生命历程续补：新增迁出原因与逐段居住城乡模式；T003c多选/存储解释保持待验证。跨波主要目录、KPI和常规波次共现矩阵未纳入2014 Life History字段。


2026-10-22概念链接重叠复核：3个未分类多概念链接均以官方题意/记录结构复核后解决。2013/2015 Parent模块`ca009`按parentID筛选父亲/母亲，保留两个独立构念；2018 `fl012_w4`两个候选Concept ID实际对应同一FL012_W4题，已在显式别名表规范为一个概念。全量概念—源字段映射从6,805降至6,804；去重E/P候选概念从1,409降至1,408；未分类重叠为0。概念重叠仍有32项，其中均有已说明关系；路由/分母及派生规则在分析前仍须预先定义。详见[`audit/concept_overlap_resolution_2026-10-22.md`](concept_overlap_resolution_2026-10-22.md)。


2026-10-22 Wave 2人寿保险标签复核：官方问卷明确FN056_W2_5四个缴费频率选项，CodeBook响应类别表未列季度选项且季度金额子字段标为“No Observations”。将其作为类别覆盖差异而非标签定义冲突，网站显示完整问卷菜单和来源提示；不传播频数、不推断获准发行数据的实际值，拟分析前仍需审核发行版路由和值域。16项自动测试全部通过。详见[`life_insurance_frequency_wave2_category_coverage_review_2026-10-22.md`](life_insurance_frequency_wave2_category_coverage_review_2026-10-22.md)。


2011 FN064/FN070逐阈值Codebook类别已恢复到E/P值标签目录，共8个字段；不展示频数、不补齐未列类别，仍保留金额/路由分析锁定。网站E/P表现在对所有带`DO NOT ANALYZE`的字段显示醒目警示。详见[`pension_2011_fn064_fn070_storage_route_review_2026-10-22.md`](pension_2011_fn064_fn070_storage_route_review_2026-10-22.md)。
