# 2011问卷来源身份更正及影响审计

更新：2026-10-21。根据 `sources_official/SOURCES.md`，文件 `CHARLS_2011_Baseline_Questionnaire_official.pdf` 和同名摘录实际是2013随访问卷，不能作为2011基线问卷。正确文件是 CHARLS 官方2011基线家户问卷：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc`，文本检索副本为相邻的 `_extracted.txt`。官方2011 Codebook位于 `sources_official/CHARLS_2011_Codebook_extracted.txt`。

## 已完成的修正

- 10个构建脚本中的错误2011问卷引用已指向正确基线摘录：慢病辅助项、慢病诊断时间、慢病管理、返家频率、家户资产、养老金、养老金补充项、退休史、工作暴露相关和值标签脚本。Codebook镜像路径统一指向 `sources_official/` 下的官方摘录。
- 对 `BA005` 做了题干级复核并撤回错误判断：2011基线题是“外出上学/工作时是否几乎每周回家”，与Codebook二元 Yes/No 一致；2013题才列三档频率。现在拆成两个Concept ID，映射脚本的强断言分别检查对应波次措辞。详见 `home_return_frequency_mapping_review_2026-10-17.md`。
- 对2011 `FC019–FC021`、`FD002`、`FH001`、`FH015`、`FG014`、`FC002`、`FC017`及退休史脚本使用的官方基线来源进行了本轮重点核查；工作领域详情见 `current_work_organization_field_review_2026-10-21.md`。
- 10个机器可读目录/交叉表及站点JSON中的旧路径已更正为正式2011基线问卷/Codebook文件路径；全量目录已重建，E/P概念、字段链接数和共现索引以当前快照为准。

## 尚待复核范围

18份专题Markdown审计文件曾引用错误问卷摘录；截至2026-10-22，18份逐项来源复核均已完成。工作史与睡眠情景题复核确认FB010编码冲突继续锁定，DE010–DE012为虚构人物锚定情景并转C类；FL020 16项选项含义已补录，但发行版存储码仍未验证，保持锁定，详见`work_history_lifecourse_mapping_review_v1.md`。养老金、金融资产、轮转储蓄、未偿债务、求职/离职补偿、side-job、主观生活水平和社会照护审计也均已按对应波次官方资料更正。来源身份复核队列已清空；仍未解决的值码、分母、稀疏度或个体记录QA按各专题审计保留，不因来源复核完成而视作分析就绪。

当前站点仍是公开元数据候选目录，分析资格未建立。逐项使用获准微观数据前，须对受影响的2011字段重看正确基线问卷、Codebook、原始发布字段和值码/路由；遇到冲突或题目缺失应锁定、不凭相邻波次推断。


## 2026-10-21全目录来源路径复扫与映射增补

全量复扫发现并修正了残留的通用2011问卷路径：DB029S1–S7辅助器具、HD012访谈协助、DA029/DA030慢病诊断及FC019/FC020/FC021/FG014工作回答标签均改指向正确的2011基线家庭问卷；2020慢病辅助项路径改为实际存在的英文问卷摘录。新增`scripts/correct_2011_questionnaire_source_paths.py`并纳入`build_ep_atlas_metadata.py`。完整流水线重建后，所有audit CSV和站点JSON内错误通用2011路径残留为0。

同轮为工作目录补入两项候选：2011–2018当前工作地点相对居住地位置，以及2011–2018不在职受访者最近一份工作的雇主单位类别，各4条波次映射。对照源文件时发现2011 Codebook没有FL014记录；四波FL014选项因此按官方问卷菜单录入，标签不带频数。两个指标均保留波次原始类别和条件路由，不作为同一当前就业构念。分别见`workplace_location_2011_2018_mapping_review_2026-10-21.md`和`most_recent_job_employer_type_2011_2018_mapping_review_2026-10-21.md`。

**当前权威构建口径：**以完整入口`python scripts/build_ep_atlas_metadata.py`及`audit/ep_concept_mapping_coverage_v1.md`为准；E/P候选概念1,153（E890、P272、双角色9），E/P链接5,879，完整crosswalk5,984（C105，102匹配、3条目录外），目录7,806行（E/P7,246、C560）。当前不含微观数据分析，正式关联模型仍为0。
