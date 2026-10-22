# 慢病诊断概念—变量对照 v2

更新：2026-10-17

本表把跨波慢病诊断从源字段层映射到15个有名称的疾病概念。映射依据是各波官方问卷/代码本的疾病题顺序和项目变量元数据，不读取任何受访者值。它是定义审计，不是已完成的跨波状态派生或最终可建模结局。

## 核查到的波次差异

- 2011、2013、2015和2018的常规慢病列表为14项：高血压、血脂异常、糖尿病/高血糖、癌症、慢性肺病、肝病、心脏病、中风、肾病、胃/消化疾病、情绪/神经/精神问题、记忆相关疾病、关节炎/风湿病、哮喘。
- 2020官方问卷 `XChroDisType` 列出15项，在记忆相关疾病之后把帕金森病单列，随后为关节炎和哮喘。因此2020序号13/14/15分别对应帕金森/关节炎/哮喘；更早波次序号13/14是关节炎/哮喘。
- 2018官方问卷对第12项记忆相关疾病的说明写入“帕金森病”作为示例，因此2018不能提供独立的帕金森指标，也不能与2020单列帕金森字段当作同一量。
- 2013和2015有复访状态确认、区间新诊断分支。三类字段在变量对照中分开标记：`doctor_diagnosis_item`、`returner_prior_condition_confirmation`、`returner_interval_new_diagnosis`。不能只用常规基线题就把返访者编码为无病。
- 对照表不把“是否知道患病”、诊断时间、药物/治疗和当前病情等题目混作医生诊断结局；它们可在后续形成不同的概念或派生信息。

## 文件和字段

- `chronic_disease_concept_crosswalk_v2.csv`：15行概念词典，含2011–2018旧序号、2020序号、源字段模板和波次 caveat。
- `chronic_disease_concept_variable_mapping_v2.csv`：从 `raw_variable_catalog_v1.csv` 中匹配到的实有字段逐项表，含年份、字段名、原始标签、模块、变量角色和 Concept.ID。当前共231条源字段—波次角色映射：原有疾病诊断/复访字段、2013/2015 ZDA007前次访谈疾病状态28条，以及DA009时间格式标记56条。另含男性限定前列腺疾病（不含前列腺癌）概念20条波次字段映射。前者是历史预加载/返访上下文，后者的1=Year、2=Age是其伴随年份/年龄值的单位选择，不是独立结局。
- `chronic_disease_concepts_v2.json`：本地原型用的公开变量元数据子集。
- 可重建脚本：`../scripts/build_chronic_disease_concept_crosswalk.py`。

## 官方来源

- 2011 CHARLS 官方 codebook，Health Status and Functioning 中 DA007 疾病条目；项目存档提取文本：`CHARLS_2011_Codebook_extracted.txt`。
- 2013、2015 官方问卷，Health Status and Functioning 中 DA007 疾病序列及复访条件/previous wave 健康状态路由；存档：`背景资料/官方指南和问卷/CHARLS_2013_Questionnaire_extracted.txt`、`CHARLS_2015_Questionnaire_extracted.txt`。
- 2018 官方问卷，Health Status and Functioning 中 DA007_1–DA007_14；特别核对 DA007_12 的记忆相关疾病说明含 Parkinson’s disease；存档：`背景资料/官方指南和问卷/CHARLS_2018_Questionnaire_extracted.txt`。
- 2020 官方英文问卷中的 `XChroDisType` 疾病列表，以及 DA003_[i] 医生诊断题；存档：`背景资料/官方指南和问卷/CHARLS_2020_Questionnaire_English_extracted.txt`。变量名/波次实际存在性由 `raw_variable_catalog_v1.csv` 交叉验证。

## 还没有解决的派生问题

本表不决定疾病状态的跨波更新规则。下一步仍需按每波 respondent/interview type 和官方路由，将基线曾诊断、返访者上一波疾病状态、上一波核实结果、区间新诊断、拒答/不知道、结构性不适用区分开；再与现有 `chronic_disease_wave_definition_review_v1.md`、`chronic_disease_state_derivation_v1.md` 和聚合 QA 对照。已确认字段模板只证明该源变量属于该病种题项，不证明其在每位受访者中可直接解释为 0/1，也不证明 2011–2020完全可比。


### 2026-10-17：前列腺疾病补充

依据2011、2013、2015、2018官方问卷/代码本补入独立 `prostate_illness_diagnosis` 候选概念。20条字段映射覆盖新访者DA029、返访者DA029_W2_1既往知情、2018 DA029_W4区间新增诊断及DA030年/龄单位和数值组件。DA029明确排除前列腺癌；该题仅男性适用，必须按new/returner路由解释，不能向女性或2020波次外推。此处字段数不是独立指标数。
