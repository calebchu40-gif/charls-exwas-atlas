# 2011养老金 FN024 变量身份与旧冲突更正（2026-10-22）

此前审计误将内容实际为2013随访的`CHARLS_2011_Baseline_Questionnaire_official`材料当作2011证据，因此错误地把2013 `FN022_W2`既往参保追问题干与2011 Codebook `fn024`作比较。使用CHARLS官方2011基线家户问卷后，这一“2011问卷/代码本码值冲突”不成立，已撤销相应锁定。

正确的2011基线问卷在`FN024`询问政府/事业单位或企业基本养老保险当前参保情况，且仅在`FB011=2`（尚未办理退休手续）时询问。答案为1=参加政府和事业单位养老保险、2=参加企业基本养老保险、3=均未参加。2011 Codebook的Wave 1字段`fn024`同样列出1/2/3这三个类别，含义逐项一致；Harmonized CHARLS D也将Wave 1 `FN024`列为参保变量。该项应视为未办理退休者的当前参保类型候选，不是未参保者既往参保史。

2013 `FN022_W2`是另一道题：仅在当前未参加相关基本养老金的路由中，询问过去是否曾参保；其四类包括政府/事业单位、企业、两者、均无。保留其既往参保概念，不与2011 `fn024`合并。2011/2013字段的题目身份与分母不同，跨波分析需要单独确定目标构念。

Codebook `fn035`“What do You Plan to Do”则与正确2011基线问卷`FN035`的缴费年限不足时养老金安排计划一致，答案为一次补缴、一次性补偿或不能领取养老金。该处旧先前差异同样来自误用2013问卷，并非2011证据冲突；现有字段映射保留为缴费年限不足条件下的计划候选。

## 目录处理

- 将2011 `fn024`从`pension_past_basic_plan_participation_when_not_currently_enrolled`拆出，映射为`pension_current_basic_plan_enrollment_among_nonretired_2011`，用波次特异构念标签和正确来源记录。
- 保留Codebook已核实的1/2/3类别，不再标记问卷/代码本冲突或`DO NOT ANALYZE`。该字段仍是候选变量；实际分析前仍需在批准的数据发行版核对路由、缺失、样本资格、权重和复杂抽样设计。
- 2013 `fn022_w2`继续属于既往参保追问，题意、选项和路线独立记录。
- 2011 `fn035`继续映射为缴费年限不足时的退休养老金安排计划；不与“预期待遇金额”或“预计领取时间”字段混淆。

## 来源

- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`：第4352行附近`FB011`退休手续题；第5554–5570行附近`FN024`当前参保项与后续工作单位题；第5598–5607行附近`FN034`与`FN035`安排计划。
- `sources_official/CHARLS_2011_Codebook_extracted.txt`：第84142行附近`fn024`标签；第84741行附近`fn035`标签。
- [Harmonized CHARLS D, Section J](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/harmonized_charls/application/Harmonized_CHARLS_D.pdf)：Wave 1变量列表和路由摘要。

未读取个体记录、未将Codebook频数作为样本量、未拟合关联模型。
