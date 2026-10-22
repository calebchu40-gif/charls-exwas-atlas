# 2011问卷来源身份更正及影响审计

更新：2026-10-21。根据 `sources_official/SOURCES.md`，文件 `CHARLS_2011_Baseline_Questionnaire_official.pdf` 和同名摘录实际是2013随访问卷，不能作为2011基线问卷。正确文件是 CHARLS 官方2011基线家户问卷：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc`，文本检索副本为相邻的 `_extracted.txt`。官方2011 Codebook位于 `sources_official/CHARLS_2011_Codebook_extracted.txt`。

## 已完成的修正

- 10个构建脚本中的错误2011问卷引用已指向正确基线摘录：慢病辅助项、慢病诊断时间、慢病管理、返家频率、家户资产、养老金、养老金补充项、退休史、工作暴露相关和值标签脚本。Codebook镜像路径统一指向 `sources_official/` 下的官方摘录。
- 对 `BA005` 做了题干级复核并撤回错误判断：2011基线题是“外出上学/工作时是否几乎每周回家”，与Codebook二元 Yes/No 一致；2013题才列三档频率。现在拆成两个Concept ID，映射脚本的强断言分别检查对应波次措辞。详见 `home_return_frequency_mapping_review_2026-10-17.md`。
- 对2011 `FC019–FC021`、`FD002`、`FH001`、`FH015`、`FG014`、`FC002`、`FC017`及退休史脚本使用的官方基线来源进行了本轮重点核查；工作领域详情见 `current_work_organization_field_review_2026-10-21.md`。
- 10个机器可读目录/交叉表及站点JSON中的旧路径已更正为正式2011基线问卷/Codebook文件路径；全量目录已重建，E/P概念、字段链接数和共现索引以当前快照为准。

## 尚待复核范围

18份专题Markdown审计文件曾引用错误问卷摘录；其中工作史审计现已用正确2011基线家户问卷逐项复核并更正 FB010 证据；FL020 16项问卷选项及其未确认的数据编码也已单独记录，见 `work_history_lifecourse_mapping_review_v1.md`。养老金专项复核也已完成：`pension_2011_fn015_fn016_source_identity_conflict_review_2026-10-22.md`和`pension_2011_fn036_questionnaire_codebook_identity_review_2026-10-21.md`均已按正确2011基线家户问卷更正，相关字段映射恢复。下列15份文件仍需逐项复核；跨波构念须分别依据对应官方波次材料判断，不可只凭相邻波次推定。

其余15份文件为：

- `assistive_device_phenotype_mapping_review_2026-10-17.md`
- `behavior_overlap_relationship_review_2026-10-20.md`
- `codebook_only_sleep_severity_2011_identity_review_2026-10-21.md`
- `last_nonfarm_job_hours_wage_2013_2018_review_2026-10-21.md`
- `pension_2011_codebook_questionnaire_discrepancy_review_2026-10-17.md`
- `pension_basic_plan_participation_dates_review_2026-10-21.md`
- `pension_land_requisition_and_fn094_amount_review_2026-10-21.md`
- `pension_subsidy_measurement_concepts_review_2026-10-17.md`
- `respondent_financial_assets_2011_2018_review_2026-10-21.md`
- `rotating_savings_private_lending_2011_2015_review_2026-10-21.md`
- `side_job_fields_2011_mapping_review_2026-10-21.md`
- `social_care_formal_helper_mapping_review_2026-10-17.md`
- `subjective_living_standard_2011_2013_review_2026-10-21.md`
- `unpaid_debt_balance_2011_2018_review_2026-10-21.md`
- `work_job_search_and_separation_benefits_review_2026-10-21.md`

当前站点仍是公开元数据候选目录，分析资格未建立。逐项使用获准微观数据前，须对受影响的2011字段重看正确基线问卷、Codebook、原始发布字段和值码/路由；遇到冲突或题目缺失应锁定、不凭相邻波次推断。


## 2026-10-21全目录来源路径复扫与映射增补

全量复扫发现并修正了残留的通用2011问卷路径：DB029S1–S7辅助器具、HD012访谈协助、DA029/DA030慢病诊断及FC019/FC020/FC021/FG014工作回答标签均改指向正确的2011基线家庭问卷；2020慢病辅助项路径改为实际存在的英文问卷摘录。新增`scripts/correct_2011_questionnaire_source_paths.py`并纳入`build_ep_atlas_metadata.py`。完整流水线重建后，所有audit CSV和站点JSON内错误通用2011路径残留为0。

同轮为工作目录补入两项候选：2011–2018当前工作地点相对居住地位置，以及2011–2018不在职受访者最近一份工作的雇主单位类别，各4条波次映射。对照源文件时发现2011 Codebook没有FL014记录；四波FL014选项因此按官方问卷菜单录入，标签不带频数。两个指标均保留波次原始类别和条件路由，不作为同一当前就业构念。分别见`workplace_location_2011_2018_mapping_review_2026-10-21.md`和`most_recent_job_employer_type_2011_2018_mapping_review_2026-10-21.md`。

**当前权威构建口径：**以完整入口`python scripts/build_ep_atlas_metadata.py`及`audit/ep_concept_mapping_coverage_v1.md`为准；E/P候选概念1,153（E890、P272、双角色9），E/P链接5,879，完整crosswalk5,984（C105，102匹配、3条目录外），目录7,806行（E/P7,246、C560）。当前不含微观数据分析，正式关联模型仍为0。
