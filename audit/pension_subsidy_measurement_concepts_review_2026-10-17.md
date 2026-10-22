# 养老金补贴金额与比例的构念拆分（2026-10-17）

> **来源身份更正（2026-10-22）：**2011补贴部分已改用正确的`CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`；旧引用文件实际内容为2013随访问卷。现按正确2011基线问卷、2011 Codebook重新核对FN009–FN011路由和字段。

## 审计结论

旧版通用 `pension_subsidy_amount` 把年度补贴、一次性补贴和月补贴合为一个Concept ID；旧版 `pension_subsidy_ratio` 又把养老保险和医疗保险补贴比例合并。它们的报告时期、保险类型和单位不同，不能当作同一个测量指标。现已按问卷构念拆为：年度养老金补贴金额（元/年）、一次性养老金补贴金额（元）、养老保险补贴比例（0–100%）、养老保险月补贴金额（元/月）、医疗保险补贴比例（0–100%）、医疗保险月补贴金额（元/月）。年度和一次性金额保留计划类型、补贴来源及波次在字段层；2018年养老与医疗保险独立。

## 官方依据与适用边界

- 2011基线家户问卷摘录 `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` 第5499–5503行：FN009–FN014仅对FN002=3/4/5的农村/居民类养老金领取者提问；FN009=No跳至FN012，FN009=Yes后询问缴费起始时间和FN011金额。FN011题干分别列出年缴费、集体年度补贴、政府年度补贴，或一次性缴费、集体一次性补贴、政府一次性补贴，变量码为FN011_1至FN011_6。2011 Codebook第83786–83816行另将`fn011`定义为支付形式选择器（1=Annual、2=Lump Sum），并分别列出六个金额项。故年度项为`fn011_1/_2/_3`，一次性项为`fn011_4/_5/_6`；计划/领取者路由与形式选择器需保留，不能将跳题当作0。
- 2013官方问卷 `sources_official/CHARLS_2013_Questionnaire_extracted.txt` 第7596–7604行分别询问年度补贴和一次性补贴，并指出后续居民养老金题依参保计划提问。该组金额应保留波次和计划类型，不能把 payer/plan 字段当成相互可替代的个人总额。
- 2018官方问卷 `sources_official/CHARLS_2018_Questionnaire_extracted.txt` 第7797–7814行规定，FN104回答Yes后继续询问FN105开始领取年月及FN106/FN107补贴；回答No或Unknown跳至FN012。FN106是养老保险补贴，FN107是医疗保险补贴；每题记录比例或元/月金额，且题目允许用-1表示Unknown。FN105月份0表示受访者不记得月份。不得把条件性空值当成0，也不得合并两种保险或比例/金额答案。
- 2018官方代码本 `sources_official/CHARLS_2018_Codebook_extracted.txt` 第61952–62026行列有对应变量名；目录只保留题目允许的范围/单位及原始标签，不使用代码本频数、均值或标准差作为研究结果。

## 当前映射与限制

重建 `audit/pension_exposure_variable_mapping_v1.csv` 后，旧概念已不再用于上述字段：2011/2013/2015年度补贴字段指向 `pension_subsidy_annual_amount`；2011/2013一次性补贴指向 `pension_subsidy_lump_sum_amount`；2018 `fn106_w4_1/_2` 与 `fn107_w4_1/_2` 分别指向养老/医疗比例和月金额4个概念。2018这4个字段值标签均明确保留 `-1=Unknown`。现阶段均为候选暴露，不代表可跨波直接合并或已有合格模型。连续金额项不使用代码本频数作样本量。2011受访者微观值、特殊缺失码及FN011格式选择器与子项实际一致性仍须在获准数据中验证；已由问卷和Codebook确认的题意/路由不应再标为来源待审。

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


## 2011来源身份复核补充（2026-10-22）

已确认此审计的旧2011引用属于错标的2013问卷摘录；现更正为正式2011基线家户问卷。FN009=Yes是FN011回答资格，FN009=No跳至FN012；Codebook中的FN011形式变量区分年度与一次性回答。六个金额组件分别保留，2011 Codebook中的观测统计仅用于定位官方条目，不进入Atlas或研究结果。微观数据一致性、特殊缺失和实际分母仍未核验。
