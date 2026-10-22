# 2013人寿保险缴费频率：问卷选项与CodeBook类别覆盖复核（2026-10-22）

## 裁定

2013 `FN056_W2_5`保留为候选分类暴露。值标签按该波官方问卷展示四类：1=Monthly、2=Quarterly、3=Half a year、4=Annually；网站在值标签旁直接显示CodeBook类别表未列季度选项及获准发行版核验提醒，完整来源与路由说明保留在概念悬浮提示中。原先把它判为“问卷与CodeBook标签冲突”并整题禁用，现修正为“问卷定义明确，CodeBook类别表未覆盖该选项”。

## 官方证据

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`，印刷页207–208附近，FN056_W2题组：FN056_W2_5列出月、季度、半年和年度缴费选项；相邻FN056_W2_6分别以月、季度、半年、年度为金额周期。
- `sources_official/CHARLS_2013_Codebook_extracted.txt`，Work, Retirement and Pension部分，FN056_W2_5的响应类别表列出月、半年、年度，未列季度选项；相邻FN056_W2_6_2季度缴费金额字段明确标注“No Observations”。本审计不抄录或传播CodeBook频数。
- 2015问卷和CodeBook均包含季度类别，说明不能用2015类别反推2013；2013问卷本身已足以给选项2定义语义。

## 目录处理及边界

`audit/life_insurance_exposure_crosswalk_v1.csv`保留问卷定义的四类，并在`mapping_status`与`caveat`中注明CodeBook类别覆盖差异。`audit/pension_label_conflict_adjudication_v1.csv`将机器裁定状态改为`resolved_questionnaire_authority_codebook_category_table_partial`，由目录构建器以该波问卷标签为准。主目录值标签不再空白，标签状态不再为`conflict`，也不再因这个类别表覆盖差异单独标记`DO NOT ANALYZE`。

这项裁定只解决选项含义和目录标签；没有读取个体回答，也没有确认任何具体发行文件是否含代码2。后续在获准版本做分析前仍应核对发行版值域、特殊缺失和适用路由；如果出现代码2，按本波问卷解释为Quarterly。变量仍为候选暴露，需结合完整的人寿保险参与路由和分析分母审核，不能当作现成的跨波统一变量。

