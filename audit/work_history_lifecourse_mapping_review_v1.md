# 职业生涯工作史暴露映射复核（2011/2013）

> **来源身份更正（2026-10-21）：**本文旧版本引用的 `CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` 实际内容是2013随访问卷。本文涉及的2011题干或路由判断须对照正确的官方2011基线问卷复核；在复核完成前，不能把该旧摘录当作2011题意证据。处理范围及当前状态见 [`2011_questionnaire_source_identity_correction_2026-10-21.md`](2011_questionnaire_source_identity_correction_2026-10-21.md)。

更新：2026-10-17。此次把未归属的终身工作史变量逐项与官方问卷和同波代码本核对。问卷原文位于`CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`（Section F，印刷页143–145/PDF页149–151）及`CHARLS_2013_Questionnaire_extracted.txt`（Section F，FB001–FB010）；编码标签取自相应官方代码本。范围仅为2011和2013的回溯工作史题，不读取个人回答。

## 新增候选概念与编码

| 概念ID | 变量码（2011；2013） | 测量对象与边界 |
|---|---|---|
| `first_work_start_timing` | `fb001_1`,`fb001_2`；同 | 首次工作/务农年龄或日历年二选一；年龄、年份分开保留，未经出生年份校验不得合成。 |
| `first_job_work_unit_type` | `fb002`；同 | 第一份工作的单位类型，是回溯第一份工作而非当前职业。 |
| `first_job_firm_ownership_type` | `fb003`；同 | 仅当第一份工作单位类型为企业（FB002=4）时询问；未进入该支路不是“无所有制”。 |
| `career_state_collective_employment` | `fb005`；同 | 职业生涯中是否曾在国有/国控/集体企业工作。若第一份工作已确认是相应所有制企业，问卷跳过FB005；估计总体指标时须用FB002/FB003识别该支路。 |
| `career_state_collective_enterprise_type` | `fb006`；同 | 在确认曾有此类经历后询问具体所有制类型，分母为条件性子组。 |
| `career_long_work_interruption` | `fb007`；同 | 是否曾有一次超过1年的工作中断；按问卷排除服役、灵活就业、退休后不工作及当前未就业等情形。 |
| `career_total_interruption_duration` | `fb008_1`,`fb008_2`；同 | 所有中断的合计年数/月数；仅对报告中断者提问，二字段为单位组件，缺失不可当作0。 |
| `career_longest_interruption_interval` | `fb009_2`,`fb009_3`,`fb009_5`,`fb009_6`；`fb009_1`–`fb009_4` | 最长中断起止年月。2011公开字段后缀与2013不同，按该波代码本字段标签映射；月份0可能代表记不清，端点不完整时不可派生精确时长。 |
| `career_interruption_reason` | `fb010`；同 | 中断原因，条件于FB007=是。2013问卷和代码本均为1=家庭、2=健康、3=上学、4=失业/下岗、5=其他。 |

以上共新增9个Concept ID和28条波次字段映射。工作暴露目录现在为46个Concept ID、137条字段映射；不是137种独立指标。2015、2018、2020的FB前缀复用为其他问题（例如2020 FB001问农活地点、FB002问农活类型），未跨波复用本次生活史定义。

## 明确的代码冲突

2011 `FB010`问卷列出的选项为1–5（家庭、健康、上学、失业/下岗、其他），但2011代码本标签显示1=家庭、2=健康、4=上学、5=失业/下岗、6=其他。没有证据能安全确定两者如何对应，因此目录仅保留官方代码本标签供追溯，并将映射状态标为“问卷/代码本编码冲突，未解决前不可分析”。该冲突不外推到2013；2013两份官方来源一致。

值标签脚本只保留代码和类别文本，移除代码本频数与百分比。连续年龄/年份/时长字段保留数值属性和单位，不将其拆成响应类别。

## 构建与审查文件

主字段级映射：`work_exposure_crosswalk_v1.csv`；逐字段官方回答标签：`work_exposure_value_labels_v1.csv`；网站JSON：`site-prototype/dist/work_exposures_v1.json`。构建入口为`python scripts/build_work_exposure_crosswalk.py`与`python scripts/build_work_exposure_value_labels.py`，全量同步由`python scripts/build_ep_atlas_metadata.py`执行。正式分析前仍须冻结目标人群、路由分母、缺失处理和跨波定义。


2026-10-21补充：2011/2013 `FB001`父项明确选择年龄或日历年，现列为C类单位选择器；`FB001_1`和`FB001_2`仍分别保留首次工作年龄/年份字段映射，暂不自动换算。详见`audit/lifecourse_timing_selector_review_2026-10-21.md`。2020同名`FB001`题意不同，未纳入。
