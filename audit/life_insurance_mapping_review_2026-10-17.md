# CHARLS 人寿保险候选暴露映射复核

更新：2026-10-17。依据 CHARLS 2013、2015、2018 官方个人问卷与对应 CodeBook，按题目语义、适用路由、金额单位和逐波差异建立候选映射。仅使用公开字段标签和问卷编码；未读取受访者观测值，也未复制 CodeBook 的频数、比例或统计分布。

## 新增范围

整理出11个候选概念、38条波次—源字段映射，链接至主目录既有 E 角色。题组覆盖保险参加/领取状态、保单类型、开始参保年月、保费承担者、缴费频率及按周期记录的保费金额、已获赔付/报销状态及金额、预期待遇（月金额或一次性金额）。同名概念仅表示同一题目家族，题目目标和路由不必然跨波等价。

|候选 Concept ID|题目构念|映射数|波次—源字段|
|---|---|---:|---|
|`life_insurance_participation`|是否参加人寿保险（自报）|2|2013 `fn056_w2_1`; 2015 `fn056_w2_1`|
|`life_insurance_purchase_timing`|人寿保险开始参加时间|4|2013 `fn056_w2_2_1`; 2013 `fn056_w2_2_2`; 2015 `fn056_w2_2_1`; 2015 `fn056_w2_2_2`|
|`life_insurance_policy_type`|人寿保险类型（自报）|3|2013 `fn056_w2_3`; 2015 `fn056_w2_3`; 2018 `fn056_w2_3`|
|`life_insurance_claim_or_reimbursement_status`|是否曾从人寿保险获得赔付/报销|3|2013 `fn056_w2_7`; 2015 `fn056_w2_7`; 2018 `fn056_w2_7`|
|`life_insurance_expected_benefit_monthly`|人寿保险预期月领取金额|3|2013 `fn056_w2_9_1`; 2015 `fn056_w2_9_1`; 2018 `fn056_w2_9_1`|
|`life_insurance_expected_benefit_lump_sum`|人寿保险预期一次性领取金额|3|2013 `fn056_w2_9_2`; 2015 `fn056_w2_9_2`; 2018 `fn056_w2_9_2`|
|`life_insurance_premium_payer`|人寿保险缴费承担者|2|2013 `fn056_w2_4`; 2015 `fn056_w2_4`|
|`life_insurance_premium_payment_frequency`|人寿保险缴费频率|3|2013 `fn056_w2_5`; 2015 `fn056_w2_5`; 2018 `fn056_w2_5`|
|`life_insurance_premium_amount`|人寿保险缴费金额（按缴费周期）|12|2013 `fn056_w2_6_1`; 2013 `fn056_w2_6_2`; 2013 `fn056_w2_6_3`; 2013 `fn056_w2_6_4`; 2015 `fn056_w2_6_1`; 2015 `fn056_w2_6_2`; 2015 `fn056_w2_6_3`; 2015 `fn056_w2_6_4`; 2018 `fn056_w2_6_1`; 2018 `fn056_w2_6_2`; 2018 `fn056_w2_6_3`; 2018 `fn056_w2_6_4`|
|`life_insurance_claim_amount`|人寿保险已获赔付/报销金额|2|2013 `fn056_w2_8`; 2015 `fn056_w2_8`|
|`life_insurance_current_receive_expect_or_contribute`|人寿保险当前领取、预期领取或缴费（合并题）|1|2018 `fn073_w4`|

## 需要在目录中保留的区分

- 2013/2015 `fn056_w2_1`问是否参加人寿保险；2018 `fn073_w4`把当前参加、领取或预期领取合并提问，已独立登记，不与前两波二元参加题合并。
- 2013/2015 `fn056_w2_2_1/_2`记录开始参加的年/月，单独保留年月组件；月份为0或缺失时不推定具体日期。
- 2013/2015险种代码3为“Survivorship insurance”；2018问卷列“Pure endowment insurance”。目录保留逐波原始答案标签，不凭译名将代码3强制视为等价类别。2018问卷指示多份保单时记录最重要的一份；“其他”开放文本不是标准化类别。
- 保费缴费承担者只在2013/2015字段中出现。保费频率和金额分开；金额字段单位包括元/月、元/季度、元/半年、元/年。未来若计算年化保费，须从频率和金额分开生成派生字段，保存原始答案并核查特殊缺失。
- 赔付/报销问题在2013/2015问是否报销，2018问是否曾获赔付，作为候选同族记录但保留问法差异。赔付金额只有2013/2015问卷明确询问。
- 预期待遇的月领取金额和一次性金额分成两个概念，避免量纲混用；题目只向满足问卷相应保险/期待领取路径者询问。

## 官方编码冲突：2013缴费频率 `fn056_w2_5`

2013官方问卷（打印页207）列出 1=Monthly、2=Quarterly、3=Half a year、4=Annually；2013 CodeBook 的该字段答案标签只列代码1、3、4，没有代码2。代码本没有出现代码2不能证明问卷选项无效，但两份官方材料不一致且当前无法确认实际发布编码，故目录保存冲突说明并标记 **DO NOT ANALYZE**。不可据此自动补码、重编码或将该字段用于模型。2015/2018对应字段分别对照各自官方问卷与CodeBook，不把2013冲突外推至其他波次。

## 来源和可复现构建

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt` 第207–208打印页；`sources_official/CHARLS_2013_Codebook_extracted.txt` 人寿保险字段条目。
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt` 第183–184打印页；`sources_official/CHARLS_2015_Codebook_extracted.txt` 人寿保险字段条目。
- `sources_official/CHARLS_2018_Questionnaire_extracted.txt` 第233–234打印页；`sources_official/CHARLS_2018_Codebook_extracted.txt` 人寿保险字段条目。
- 可复现映射：`scripts/build_life_insurance_crosswalk.py` 生成 `audit/life_insurance_exposure_crosswalk_v1.csv`；全目录通过 `python scripts/build_ep_atlas_metadata.py` 重建。

**状态：**目录候选可按源字段码、波次、答案标签和 Concept ID 检索；不等于获准数据上的分析指标或结果。结构性缺失、多选/条件路由、可比性、权重和最低样本门槛均未在本映射中解决。


## 后续目录规则复核

全量目录检查发现通用养老金生成器曾把 `fn056_w2_*` 人寿保险题误映射到养老金缴费频率、缴费承担者及待遇状态等概念，并把2018周期保费金额误标为缴费频率。已在 `scripts/build_pension_exposure_crosswalk.py` 排除该人寿保险题族（保留有独立养老金含义的区间/上限字段），并重新构建；上述38条人寿保险映射只由本专题crosswalk提供。被移除的错误链接对应仍然存在的官方问卷字段，现归入待分流的E-only序列，不得计作新增概念。
