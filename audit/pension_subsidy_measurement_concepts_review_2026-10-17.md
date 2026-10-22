# 养老金补贴金额与比例的构念拆分（2026-10-17）

> **来源身份更正（2026-10-21）：**本文旧版本引用的 `CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` 实际内容是2013随访问卷。本文涉及的2011题干或路由判断须对照正确的官方2011基线问卷复核；在复核完成前，不能把该旧摘录当作2011题意证据。处理范围及当前状态见 [`2011_questionnaire_source_identity_correction_2026-10-21.md`](2011_questionnaire_source_identity_correction_2026-10-21.md)。

## 审计结论

旧版通用 `pension_subsidy_amount` 把年度补贴、一次性补贴和月补贴合为一个Concept ID；旧版 `pension_subsidy_ratio` 又把养老保险和医疗保险补贴比例合并。它们的报告时期、保险类型和单位不同，不能当作同一个测量指标。现已按问卷构念拆为：年度养老金补贴金额（元/年）、一次性养老金补贴金额（元）、养老保险补贴比例（0–100%）、养老保险月补贴金额（元/月）、医疗保险补贴比例（0–100%）、医疗保险月补贴金额（元/月）。年度和一次性金额保留计划类型、补贴来源及波次在字段层；2018年养老与医疗保险独立。

## 官方依据与适用边界

- 2011基线个人问卷摘录文件 `sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` 第8788–8794行将年度补贴（集体、政府）与总额/一次性补贴（集体、政府）分开列示。现映射 `fn011_2/_3` 为年度金额、`fn011_5/_6` 为一次性金额。
- 2013官方问卷 `sources_official/CHARLS_2013_Questionnaire_extracted.txt` 第7596–7604行分别询问年度补贴和一次性补贴，并指出后续居民养老金题依参保计划提问。该组金额应保留波次和计划类型，不能把 payer/plan 字段当成相互可替代的个人总额。
- 2018官方问卷 `sources_official/CHARLS_2018_Questionnaire_extracted.txt` 第7797–7814行规定，FN104回答Yes后继续询问FN105开始领取年月及FN106/FN107补贴；回答No或Unknown跳至FN012。FN106是养老保险补贴，FN107是医疗保险补贴；每题记录比例或元/月金额，且题目允许用-1表示Unknown。FN105月份0表示受访者不记得月份。不得把条件性空值当成0，也不得合并两种保险或比例/金额答案。
- 2018官方代码本 `sources_official/CHARLS_2018_Codebook_extracted.txt` 第61952–62026行列有对应变量名；目录只保留题目允许的范围/单位及原始标签，不使用代码本频数、均值或标准差作为研究结果。

## 当前映射与限制

重建 `audit/pension_exposure_variable_mapping_v1.csv` 后，旧概念已不再用于上述字段：2011/2013/2015年度补贴字段指向 `pension_subsidy_annual_amount`；2011/2013一次性补贴指向 `pension_subsidy_lump_sum_amount`；2018 `fn106_w4_1/_2` 与 `fn107_w4_1/_2` 分别指向养老/医疗比例和月金额4个概念。2018这4个字段值标签均明确保留 `-1=Unknown`。现阶段均为候选暴露，不代表可跨波直接合并或已有合格模型。代码本未提供答案类别的连续金额项仍标注为连续值/标签待审；分析时须结合官方缺失码、实际发布数据和路由重新核验。

## 重建后目录状态

- 候选E/P Concept ID：834；E角色560，P角色283；二者交集9个（角色源文件可能以单独E/P行表达其中部分交集）。
- 概念—源字段crosswalk：5,249条E/P映射，全部匹配主字段目录；另有11条C类映射，3条未匹配项均是C类权重资格元数据，不属于E/P分析变量。
- 目录：7,614行（E/P 7,148，C类466）。网站JSON已由目录构建器重写。E-only未映射序列900、P-only 73、双角色2；这些是原始变量序列，不是遗漏的独立指标数。
- 正式关联模型数仍为0；共现计数只是元数据可用性，不是样本量或显著性结果。

## 可复现步骤

在项目根目录依序运行：

```powershell
python scripts/build_pension_exposure_crosswalk.py
python scripts/build_pension_supplementary_crosswalk.py
python scripts/build_pension_codebook_value_labels.py
python scripts/build_charls_atlas_catalog.py
python scripts/build_ep_concept_source_crosswalk.py
python scripts/summarize_directory_scope.py
python scripts/summarize_ep_pair_wave_coverage.py
python scripts/summarize_catalog_concept_categories.py
```

特别注意：养老金主crosswalk生成器会覆盖补充养老金映射；所以必须紧接着运行补充crosswalk生成器。
