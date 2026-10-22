# 2011 养老金模块剩余字段复核（2026-10-22）

## 范围与限制

本轮复核只使用CHARLS官方正确波次问卷、Codebook及公开变量目录，没有读取受访者微观数据。Codebook频数仅帮助确认响应类别或是否有观测，不作为分析样本量。当前站点展示的概念仍是研究候选，待完成官方数据授权、设计/权重规则和分析方案核查后才能开展关联分析。

## 恢复的字段映射

- `fn015`：2011 FN015询问正在领取居民养老金者（FN002=4）是否由其他养老金转入（1=Yes、2=No），使用专属概念 `pension_resident_transfer_status_current_recipient`；FN016仅在Yes后询问。
- `fn016`：2011 FN016是当前领取者的条件性转入来源（农村养老保险、企业基本养老保险、其他），使用 `resident_pension_transfer_source_current_recipient`；“其他”自由文本不纳入公开目录值。FN065/FN066才是已参保路线，并与2013 FN063_W2/FN064_W2对应；2015拆分计划字段暂不自动合并。
- `fn036_1`：工作单位养老金预期待遇金额（元/月）；`fn036_2`：预期待遇占退休前工资百分比。2011正确基线问卷与Codebook字段名和单位一致；分别建立概念，适用于FN034=Yes或FN035=1路由。比例不转换为金额。
- `fn048`父字段是回答格式选择器，转为C类元数据（1=比例、2=金额）；`fn048_1/2`：沿用既有跨波概念 `pension_early_exit_reduction_amount_or_ratio`，来源级分别保留百分比和人民币减少额。它们是按FN047指定年龄提前离开当前工作时的情景估计。
- `fn051_1/2`：商业养老保险开始缴费年、月，拆分为两个时间组件，月份0为不记得。
- `fn060_1/2`：所选农村/城乡居民类养老计划开始缴费年、月，拆分组件并保留FN039计划上下文；不自动跨计划/波次合并。

构建规则在 `scripts/build_pension_exposure_crosswalk.py`。先前fn015/fn016和fn036的错误身份冲突审计均已依据正确2011问卷更正，分别见 `audit/pension_2011_fn015_fn016_source_identity_conflict_review_2026-10-22.md` 和 `audit/pension_2011_fn036_questionnaire_codebook_identity_review_2026-10-21.md`。

## 转为排除关联的元数据

- `fn028_1/2/3` 和 `fn031`：正确2011问卷与Codebook将其定义为工作单位省/市/县等地理详情。属于条件性敏感地理信息，不作独立暴露，不公开个人位置或逐人地理编码。
- `fn046_1/2/3`：问卷内容是缴费确定型计划账户余额及最近查看时间，但官方Codebook对子字段均明确标注 `No Observations`；转为停用C元数据，不推断为零。

角色更正记录在 `audit/catalog_role_override_review_v1.csv`，通过 `scripts/apply_catalog_role_overrides.py` 执行。

## 仍待核实的展开区间字段

`fn064_1..4`（FN063预期待遇回答的展开追问）和`fn070_1..4`（FN069对应追问）现各自映射到独立的“展开区间回答序列”候选概念。Codebook给出了250、500、1000、2000元各阈值的类别标签，但各字段是序列组件，且公开资料未明确数值待遇的周期/支付形式及释放数据中的完整序列逻辑。因此保留官方类别标签和阈值，网站标记DO NOT ANALYZE as numeric benefit；不合并、不取中点、不年化，也不把跳题当零。

## 官方证据位置

- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`：FN015–FN016、FN028、FN031、FN034–FN070。
- `sources_official/CHARLS_2011_Codebook_extracted.txt`：上述字段标签、响应类别与No Observations状态。
- 2013对应题：`sources_official/CHARLS_2013_Questionnaire_extracted.txt` 的FN063_W2/FN064_W2，以及 `CHARLS_2013_Codebook_extracted.txt` 的 `fn063_w2_2_`/`fn064_w2_2_`。

## 验收要点

全量构建需确认fn015、fn016、fn065、fn066、fn036_1/2、fn051_1/2、fn060_1/2以及fn064/070展开追问组件均有对应Concept链接，FN015/016当前领取者路线与FN065/066已参保路线严格区分；fn048父选择器为C、子字段保留E；工作单位地理字段与fn046子项不进入E/P；fn064/fn070不被错误当作连续金额。


2026-10-22后续更正：Codebook明确`fm031`为No Observations，目录已将其转C类inactive legacy metadata并从E/P概念crosswalk移除；FM032展开区间端点仍单独锁定待发行版存储/特殊码核验。详见`audit/pension_2011_fm031_no_observations_review_2026-10-22.md`。


## FM019 checkbox response storage follow-up (2026-10-22)

Local authorized-table validation confirms `fm019s1`–`fm019s5` store the selected slot as a string option code and use empty strings otherwise. This verifies storage format only. Empty strings conflate unselected and not-asked states, and a route consistency check finds selections outside the apparent questionnaire paths; the eligible denominator remains unresolved. Keep all five fields under DO NOT ANALYZE. Details: `audit/pension_2011_fm019_checkbox_storage_review_2026-10-22.md`.


## FM039 bracket storage follow-up (2026-10-22)

Local authorized-table QA confirmed paired string endpoints and the Codebook extreme upper value, but FM038 answer-format selectors are empty on the bracket records. Corrected the prior “amount branch only” description; the interval unit and special-value meaning remain unresolved, so both endpoints stay locked. See `audit/pension_2011_fm039_bracket_storage_review_2026-10-22.md`.
