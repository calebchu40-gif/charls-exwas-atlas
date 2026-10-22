# 2013/2015基本养老金参保起止时间字段复核（2026-10-21）

> **来源身份更正（2026-10-21）：**本文旧版本引用的 `CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` 实际内容是2013随访问卷。本文涉及的2011题干或路由判断须对照正确的官方2011基线问卷复核；在复核完成前，不能把该旧摘录当作2011题意证据。处理范围及当前状态见 [`2011_questionnaire_source_identity_correction_2026-10-21.md`](2011_questionnaire_source_identity_correction_2026-10-21.md)。

## 核验结果

CHARLS 2013与2015代码本均列出`fn027_w2_1/_2`（通过该工作单位参加企业职工基本养老保险的开始年份/月份）及`fn028_w2_1/_2`（停止参加的年份/月份）。官方2013追访问卷对两组题意与代码本一致。官方2015问卷对FN027仍写开始参加，但对FN028却再次写成开始参加；2015代码本仍将FN028列为停止参加。FN028的2015语义冲突没有得到官方澄清，不能按代码本或题干任一方自行重编码。

## 目录处理

- `fn027_w2_1/_2`：2013/2015按参加开始年、月映射至`pension_basic_plan_participation_start_date`。只保留年月组件，不直接推算参保年限；月份0按问卷表示不记得。
- 2013 `fn028_w2_1/_2`：问卷和代码本一致，映射为停止参保年月`pension_basic_plan_participation_stop_date`。年份与月份分开，月份0表示不记得。
- 2015 `fn028_w2_1/_2`：保留为独立波次冲突审计项`pension_basic_plan_fn028_timing_2015_conflicted`，明确`DO NOT ANALYZE`。不与开始日期或2013停止日期合并，不从年月派生时长。

所有字段均在前述基本养老金参与/工作单位历史题组中，分析分母须由问卷路由决定。微观数据的实际有效值、特殊缺失、跨波样本资格尚未核验。

## 官方依据

- `sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`（文件首页注明2013 Followup Questionnaire）：第204–205页附近FN027、FN028起止时间题及月份0说明。
- `sources_official/CHARLS_2013_Codebook_extracted.txt`：FN027为开始参加、FN028为停止参加。
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`：第198页FN027和FN028题干；两项都写“start to participate”。
- `sources_official/CHARLS_2015_Codebook_extracted.txt`：FN027为开始、FN028为停止，和2015 FN028题干冲突。
- 映射规则：`scripts/build_pension_exposure_crosswalk.py`。

本轮只用公开问卷/代码本，没有读取受访者记录或估计关联。不得以代码本频数替代样本量，也不得把条件性缺失改作0或未参保。
