# 2011年预期主要养老依靠来源映射复核

2011年全国问卷 FN080 问：如果将来年老、不能工作，受访者认为主要依靠什么养老。按官方问卷与 CodeBook 的选项标签新增1个E候选概念、1条字段映射：

| Concept ID | 字段 | 官方分类 |
|---|---|---|
| `anticipated_primary_old_age_support_source` | `fn080` | 1=子女；2=储蓄；3=养老金或退休工资；4=商业养老保险；5=其他 |

该题测量主观预期的主要养老支持来源，而非已获得的家庭支持、当前养老金参保或实际领取的待遇。保留五类名义变量，不对类别排序，也不跨波合并。它与同期 `fn076` 新农保缴费由谁承担、以及实际养老金领取字段含义不同。

代码本选项频数未记录或引用；没有读取受访者记录。正式分析前应评估此单波主观预期构念的目标估计量、缺失机制和可能与年龄/退休状态的关系。

- 构建脚本：`scripts/build_old_age_support_expectation_crosswalk.py`
- 映射表：`audit/old_age_support_expectation_crosswalk_v1.csv`
- 官方依据：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`、`sources_official/CHARLS_2011_Codebook_extracted.txt`
