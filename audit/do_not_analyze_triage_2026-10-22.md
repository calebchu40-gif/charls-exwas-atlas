# 当前 DO NOT ANALYZE 项分流清单（2026-10-22）

当前主目录有33条唯一波次—字段分析锁定项。下方字段清单含33条现行锁定；FM033仅在说明文字中用于记录其已解除锁定，不计入现行数。此清单不解除任何未关闭的限制；2011 FM019、FM032/FM035、FM039进行受控本地答案存储/路由QA，未导出个人记录或把代码本频数当分析样本量。FM033基于官方问卷、Codebook及受控QA拆出为带未观测选项说明的条件性分类候选。2015 `fn064_w2_1_2_`/`_1_3_`已受控核验路由及字符串存储，年份单位明确，但一个字段有不可数值解析文本，仍锁定。

## 分类与所需证据

| 记录数 | 当前阻断原因 | 关闭阻断所需证据 |
|---:|---|---|
| 8 | DO NOT ANALYZE as an amount; preserve threshold categories; controlled QA found FN064 route/selector gaps and FN070 selector gaps; payment form and response sequence remain unresolved | 受控QA已确认类别值与路径/选择器存在上述问题；详见[`pension_2011_fn064_fn070_storage_route_review_2026-10-22.md`](pension_2011_fn064_fn070_storage_route_review_2026-10-22.md)，等待官方发行说明或字段级解释。 |
| 6 | DO NOT ANALYZE as an amount; controlled QA confirms route but finds unpaired Min/Max endpoints; FN036/FN094 format selectors absent on bracket rows | 受控QA已完成，问题和限值见[`pension_2013_bracket_bounds_local_route_review_2026-10-22.md`](pension_2013_bracket_bounds_local_route_review_2026-10-22.md)；需解决上下界配对及未决格式后才能评估数值用法。 |
| 5 | DO NOT ANALYZE: selected-option storage is confirmed, but the eligible denominator and route discrepancy remain unresolved; do not infer unselected options as No | 受控本地QA已确认选中值的存储格式；详见[`pension_2011_fm019_checkbox_storage_review_2026-10-22.md`和`pension_2011_fm039_bracket_storage_review_2026-10-22.md`](pension_2011_fm019_checkbox_storage_review_2026-10-22.md)。等待官方解释/发行版路由核实后再解除。 |
| 4 | DO NOT ANALYZE: FM031 has no Codebook observations; FM032/FM035 paired bracket endpoints and special-value meaning remain unresolved | 授权发行文件或CHARLS官方澄清验证存储、路由、值域或字段身份；依专项审计保持锁定。 |
| 3 | DO NOT ANALYZE pending exact Wave 3 questionnaire-to-Codebook field mapping confirmation | 授权发行文件或CHARLS官方澄清验证存储、路由、值域或字段身份；依专项审计保持锁定。 |
| 2 | DO NOT ANALYZE: paired endpoints and Codebook extreme value are confirmed, but FM038 unit branch and special-value meaning remain unresolved | 授权发行文件或CHARLS官方澄清验证存储、路由、值域或字段身份；依专项审计保持锁定。 |
| 2 | DO NOT ANALYZE numerically; years unit and route verified, but official string encoding and special-text/missing rules remain unresolved | 受控QA确认路线且代码本字段标题给出“年”；其中一个计划字段含不可数值解析文本。保留原字符串，需官方发行版解释编码后再判断，见[`pension_2015_transfer_year_string_storage_review_2026-10-22.md`](pension_2015_transfer_year_string_storage_review_2026-10-22.md)。 |
| 1 | exclude from E/P association matrix; DO NOT ANALYZE until the official formula ambiguity is resolved | 授权发行文件或CHARLS官方澄清验证存储、路由、值域或字段身份；依专项审计保持锁定。 |
| 1 | DO NOT ANALYZE; do not parse or publish string contents as an amount until exact official field identity is confirmed | 授权发行文件或CHARLS官方澄清验证存储、路由、值域或字段身份；依专项审计保持锁定。 |
| 1 | DO NOT ANALYZE; retain only to document the questionnaire/Codebook discrepancy pending official release clarification | 授权发行文件或CHARLS官方澄清验证存储、路由、值域或字段身份；依专项审计保持锁定。 |

## 字段清单

### 8条：DO NOT ANALYZE as an amount; preserve the exact threshold/category and confirm payment period and sequence interpretation before any statistical use

2011 `fn070_4`, 2011 `fn070_3`, 2011 `fn070_2`, 2011 `fn070_1`, 2011 `fn064_4`, 2011 `fn064_3`, 2011 `fn064_2`, 2011 `fn064_1`

### 6条：DO NOT ANALYZE as an amount; controlled QA confirms route but finds unpaired Min/Max endpoints; FN036/FN094 format selectors absent on bracket rows

2013 `fn094_w2_bracketbracket_min`, 2013 `fn094_w2_bracketbracket_max`, 2013 `fn036_w2_bracketbracket_min`, 2013 `fn036_w2_bracketbracket_max`, 2013 `fn077_w2_bracketbracket_min`, 2013 `fn077_w2_bracketbracket_max`

FN077's Yuan/month unit is explicit in the questionnaire, but its endpoints also fail to form consistent pairs; it remains locked as a numeric amount. See [`pension_2013_bracket_bounds_local_route_review_2026-10-22.md`](pension_2013_bracket_bounds_local_route_review_2026-10-22.md).

### 5条：DO NOT ANALYZE: selected-option storage is confirmed, but the eligible denominator and route discrepancy remain unresolved; do not infer unselected options as No

2011 `fm019s5`, 2011 `fm019s4`, 2011 `fm019s3`, 2011 `fm019s2`, 2011 `fm019s1`

### 4条：DO NOT ANALYZE: FM031 has no Codebook observations; FM032/FM035 paired bracket endpoints and special-value meaning remain unresolved

2011 `fm035_b`, 2011 `fm035_a`, 2011 `fm032_b`, 2011 `fm032_a`

2011 `fm033` has been removed from this lock group. It is retained as an FM011=3 categorical candidate with only documented observed codes and an explicit warning that the questionnaire's commercial-insurance option has no Codebook observations and must not be assigned an inferred code. See [`pension_2011_fm032_fm033_fm035_route_storage_review_2026-10-22.md`](pension_2011_fm032_fm033_fm035_route_storage_review_2026-10-22.md).

### 3条：DO NOT ANALYZE pending exact Wave 3 questionnaire-to-Codebook field mapping confirmation

2015 `fn057_w3_4_3_`, 2015 `fn057_w3_4_2_`, 2015 `fn057_w3_4_1_`

官方发布页所列2019-06-20版Codebook与本地核验SHA1一致；当前官方发布页/发布说明未提供该字段名冲突的勘误。故锁定仍有效，详见[`pension_2015_residual_review_2026-10-22.md`](pension_2015_residual_review_2026-10-22.md)。

### 2条：DO NOT ANALYZE: paired endpoints and Codebook extreme value are confirmed, but FM038 unit branch and special-value meaning remain unresolved

2011 `fm039_b`, 2011 `fm039_a`

### 2条：DO NOT ANALYZE numerically; years unit and route verified, but official string encoding and special-text/missing rules remain unresolved

2015 `fn064_w2_1_3_`, 2015 `fn064_w2_1_2_`

Unit is years by the official Codebook title and both plan routes match the local parent selectors; both remain strings, and one includes nonnumeric text. Do not coerce either field. See [`pension_2015_transfer_year_string_storage_review_2026-10-22.md`](pension_2015_transfer_year_string_storage_review_2026-10-22.md).

### 1条：exclude from E/P association matrix; DO NOT ANALYZE until the official formula ambiguity is resolved

2020 `xmainjobdays`

2020官方问卷的两个分支均判断`XEmployed=1`，分别写入`FC026*52`和`FD008*52`；Codebook标题及摘要统计未说明实际计算来源，不能据此解除锁定。详见[`capi_work_derived_variables_2020_review_2026-10-21.md`](capi_work_derived_variables_2020_review_2026-10-21.md)。

### 1条：DO NOT ANALYZE; do not parse or publish string contents as an amount until exact official field identity is confirmed

2015 `ha026_w2_11_25_`

### 1条：DO NOT ANALYZE; retain only to document the questionnaire/Codebook discrepancy pending official release clarification

2015 `ha065_1_18_`

## 执行规则

- DO NOT ANALYZE状态不会因字段已链接Concept而自动解除。
- 多选空值、区间端点、字符串答案、跳题缺失及家属名册槽位不得猜测性转换。
- 依赖授权发布数据字典或响应存储的事项保留锁定；公开问卷足以解决的事项依据专项审计更新。

目录映射齐全度与分析就绪度是两个检查。设计与模型门槛见`audit/charls_wave_sampling_and_weight_status_2026-10-22.md`和`audit/EXWAS_result_schema_v2.csv`。
