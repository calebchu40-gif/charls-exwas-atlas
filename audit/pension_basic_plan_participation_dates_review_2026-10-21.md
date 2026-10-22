# 2013/2015基本养老金参保起止时间字段复核（2026-10-22更新）

> **来源身份更正：**此前2013题干引用了`CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`；该文件实际内容虽为2013 Follow-up Questionnaire，但路径标错为2011。现在改用正式`sources_official/CHARLS_2013_Questionnaire_extracted.txt`核对。复核发现2013和2015问卷对FN028均写“开始参加”，而对应波次Codebook均称“停止参加”；两波都存在相同的题意冲突，不能只锁2015。

## 核验结果

2013与2015 Codebook均将`fn027_w2_1/_2`列为通过所选工作单位参加企业职工基本养老保险的开始年月，将`fn028_w2_1/_2`列为停止参加年月。两波问卷FN027均写开始参加；但两波问卷FN028也均写开始参加，与对应Codebook的“停止参加”标题冲突。问卷的FN028题干可能重复了开始时间措辞，但在没有CHARLS正式勘误或获准发行版字典证据前，不推断其意图。

## 目录处理

- `fn027_w2_1/_2`：2013/2015按参加开始年、月映射至`pension_basic_plan_participation_start_date`。保留年月组件，不直接推算参保年限；问卷月份0表示不记得。
- 2013/2015 `fn028_w2_1/_2`：统一保留为问卷/代码本题意冲突候选`pension_basic_plan_fn028_timing_questionnaire_codebook_conflicted`，四个波次字段均标记`DO NOT ANALYZE`。在冲突解除前不赋予开始/停止含义，不与FN027或跨波字段合并，不从年月派生时长。月份0仍按问卷文字记录为“不记得”，但不消解事件身份冲突。

所有字段均在基本养老金参与/工作单位历史题组中；正式分析分母须由问卷路由决定。微观数据的实际有效值、特殊缺失和跨波样本资格尚未核验。

## 官方依据

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`：FN027/FN028约第7322–7335行；两题均写“start to participate”，FN028月份0按问卷表示不记得。
- `sources_official/CHARLS_2013_Codebook_extracted.txt`：FN027为开始参加、FN028为停止参加。
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`：FN027/FN028约第6337–6348行；两题均写“start to participate”。
- `sources_official/CHARLS_2015_Codebook_extracted.txt`：FN027为开始、FN028为停止。
- 映射规则：`scripts/build_pension_exposure_crosswalk.py`。

本审计只使用公开问卷/代码本，没有读取受访者记录或估计关联。不得以代码本频数替代样本量，也不得把条件性缺失改作0或未参保。
