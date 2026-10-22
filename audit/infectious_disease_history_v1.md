# CHARLS 2011 DA044 既往传染病史字段审计

更新时间：2026-10-17。此页依据 CHARLS 官方2011基线问卷、2011代码本和公开字段目录；未读取受访者微观记录。

2011基线问卷 DA044 问受访者是否曾被医生告知得过指定传染病。问卷列出结核病、乙型肝炎、疟疾、流感、狂犬病、血吸虫病、艾滋病/感染者、乙型脑炎、痢疾、麻疹、布氏杆菌病、淋病、梅毒、其他（要求说明）和“均无”。其中前14个类别字段（`da044s1`–`da044s14`）各自保留为单波既往病史候选概念；`da044s15`“均无”不是一种疾病，故不建立疾病Concept ID。开放文本`DA044_1`未被转成标准化病种。

官方代码本对各类别只列出已选类别代码，例如`da044s1`显示1=结核病；没有足够证据将未出现的代码或空值统一解释为“否”。网站值标签因此只写代码本证实的选中类别，并注明未选/缺失存储值待官方发布格式核对。不可把它们直接当作1=Yes、0/2=No的二元患病变量。

这些题是回顾性、医生告知的既往病史，不代表当前感染；只有2011基线字段，不能作为跨波重复表型。某些病种在公开代码本汇总中十分稀疏，字段进入正式统计前须核实缺失/多选存储规则、有效样本量和适用的数据披露要求，不应仅依据代码本频数开展估计。

## 字段对应

| CHARLS字段码 | 候选概念 | 问卷类别 | 显示的值语义 |
|---|---|---|---|
| `da044s1` | `infectious_history_tuberculosis` | 结核病 | 1=Tuberculosis（选中项） |
| `da044s2` | `infectious_history_hepatitis_b` | 乙型肝炎 | 2=Hepatitis B（选中项） |
| `da044s3` | `infectious_history_malaria` | 疟疾 | 3=Malaria（选中项） |
| `da044s4` | `infectious_history_influenza` | 流感 | 4=Influenza（选中项） |
| `da044s5` | `infectious_history_rabies` | 狂犬病 | 5=Rabies（选中项） |
| `da044s6` | `infectious_history_schistosomiasis` | 血吸虫病 | 6=Schistosomiasis（选中项） |
| `da044s7` | `infectious_history_hiv_aids` | 艾滋病/感染者 | 7=AIDS/infectious cases（选中项） |
| `da044s8` | `infectious_history_encephalitis_b` | 乙型脑炎 | 8=Encephalitis B（选中项） |
| `da044s9` | `infectious_history_dysentery` | 痢疾 | 9=Dysentery（选中项） |
| `da044s10` | `infectious_history_measles` | 麻疹 | 10=Measles（选中项） |
| `da044s11` | `infectious_history_brucellosis` | 布氏杆菌病 | 11=Brucellosis（选中项） |
| `da044s12` | `infectious_history_gonorrhea` | 淋病 | 12=Gonorrhea（选中项） |
| `da044s13` | `infectious_history_syphilis` | 梅毒 | 13=Syphilis（选中项） |
| `da044s14` | `infectious_history_other_infectious_disease` | 其他（未具体指明） | 14=Other（选中项） |

表中括号表示官方代码本列出的已选类别值，不意味着代码本证明其余存储值的含义。

## 来源

- 项目存档：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc`及对应`_extracted.txt`，Health Status and Functioning，DA044；`sources_official/CHARLS_2011_Codebook_extracted.txt`，DA044s1–DA044s15。
- 官方2011问卷来源与文件校验信息见`sources_official/SOURCES.md`。
- 可复现映射：`scripts/build_health_symptom_crosswalk.py`；输出`audit/health_symptom_variable_mapping_v1.csv`及`site-prototype/dist/health_symptoms_v1.json`。
