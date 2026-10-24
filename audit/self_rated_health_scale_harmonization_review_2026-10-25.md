# CHARLS 自评总体健康量表分尺度映射复核（2026-10-25）

## 结论

2011、2013、2015年问卷中有两种不同的自评总体健康五级量表：`Excellent → Poor` 与 `Very good → Very poor`。原目录把开头的 `DA001`（前一种）映入以后一种量表为主体的概念，只把末尾的 `DA080` 归入前一种，导致相同量表被拆开、两个量表又在概念层面部分混并。本次改为按响应尺度建立两个候选概念，并保留波次字段、原代码、问卷来源和特殊路由待核验提示。

| 候选概念 | 2011–2015源字段 | 值标签 | 后续波次 |
| --- | --- | --- | --- |
| `self_rated_health_excellent_poor` | `DA001`, `DA080` | 1 Excellent; 2 Very good; 3 Good; 4 Fair; 5 Poor | 当前目录未确认2018/2020同尺度字段 |
| `self_rated_health_very_good_very_poor` | `DA002`, `DA079` | 1 Very good; 2 Good; 3 Fair; 4 Poor; 5 Very poor | 2018 `DA002`; 2020 `DA001` |

问卷在2011、2013、2015年都说明受访者在健康模块开头和结尾各评价一次，且题目顺序随机。基线问卷的随机顺序字段标为 `SEC_DA_LIST`；2013/2015问卷分别指向 `DA001b`、`DA002b`，而发布 Codebook 的实际字段名使用 `DA001`、`DA002`。问卷末尾出现 `DA079` 和 `DA080`。本复核只据此将字段归到题型，不从公开 Codebook 的频数、数据值或题目出现顺序推断哪个字段对每位受访者实际提问、哪类缺失表示跳题，也不把重复测量字段当作两个独立结局。

基线问卷末尾明确注明 `DA079`/`DA080` 不允许代理回答；DA079问卷题干及选项为 `Very good` 到 `Very poor`，而2011 Codebook 标题写作 “Self Comment of Your Health By Comparing With Others”。保留源标签冲突，以问卷题干和选项作为题型证据，并将 Codebook 标签冲突继续标注。实际分析前仍须用获批发布数据的变量字典确认这些字段的身份、缺失码、跳题和受访者覆盖；本目录不构造量表转换或合并后的分数。

## 构建实现

- `scripts/build_health_symptom_crosswalk.py` 将自评健康分为两个量表特定概念；每个字段仍独立保存在 source crosswalk。
- `scripts/enrich_outcome_value_labels.py` 给两组字段附上各自官方题目选项，不再把 DA001 的五档选项标在 Very-good/Very-poor 概念下。
- `tests/test_self_rated_health_scale_mapping.py` 防止早期波次及后续波次尺度错配。
- `scripts/apply_cognition_self_rated_memory_review.py` 的自评记忆专题复核只更新按波次拆分的源目录。网站压缩目录按变量名合并跨波字段，缺少波次键；例如 2020 `dc004` 是“Checking Day”，早期 `dc004` 是“Self Rated Memory”，因此不能把波次专属复核复制到合并行。

## 可复核官方来源

- `sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`：第2883–2893行说明双量表、前后两次、随机顺序和 `SEC_DA_LIST` 路由；第2901–2918行记录开头 DA001/DA002 的两个响应尺度；第3988–4004行记录末尾 DA079/DA080、代理人限制及对应选项。
- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`：第2362–2373行说明随机顺序及 `DA001b`/`DA002b`；第2376–2393行记录开头响应尺度；第3319–3337行记录末尾字段及选项。
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`：第1864–1875行说明随机顺序及开头字段；第1878–1895行记录开头响应尺度；第2716–2734行记录末尾字段、代理人限制及选项。
- 对应官方发布变量描述：`sources_official/CHARLS_2011_Codebook_extracted.txt`、`CHARLS_2013_Codebook_extracted.txt`、`CHARLS_2015_Codebook_extracted.txt`、`CHARLS_2018_Codebook_extracted.txt`、`CHARLS_2020_Codebook_extracted.txt`。本复核不复制变量频数或样本计数。

## 边界

这些是代码本/问卷驱动的候选字段映射，不是可分析样本、效应估计或已验证的跨波测量等价性结论。暂不生成关联结果或样本量；个体级数据未被读取。
