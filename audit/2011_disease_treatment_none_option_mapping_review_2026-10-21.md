# 2011慢病治疗“以上皆无”字段映射补齐（2026-10-21）

## 结论

官方2011 Codebook列出8个带病种索引的`DA010`“None of the Above”字段。它们此前因字段标签不含treatment/medicine关键词而未进入机器生成的治疗crosswalk。现将其补入既有病种特异治疗方式概念；没有新增8个表型，也未把Codebook频数复制进值标签或当作分析数据。

| CHARLS字段 | 已有概念 | Codebook题项身份 |
|---|---|---|
| `da010_2_s4` | `reported_treatment_dyslipidemia` | 血脂异常，以上皆无（题项索引4） |
| `da010_5_s4` | `reported_treatment_chronic_lung_disease` | 慢性肺病，以上皆无（题项索引4） |
| `da010_6_s4` | `reported_treatment_liver_disease` | 肝病，以上皆无（题项索引4） |
| `da010_7_s4` | `reported_treatment_heart_disease` | 心脏病，以上皆无（题项索引4） |
| `da010_9_s4` | `reported_treatment_kidney_disease` | 肾病，以上皆无（题项索引4） |
| `da010_10_s4` | `reported_treatment_digestive_disease` | 胃/其他消化系统疾病，以上皆无（题项索引4） |
| `da010_12_s4` | `reported_treatment_memory_related_disease` | 记忆相关疾病，以上皆无（题项索引4） |
| `da010_13_s4` | `reported_treatment_arthritis_rheumatism` | 关节炎/风湿病，以上皆无（题项索引4） |

## 证据与分析边界

字段—病种身份及选项索引来自`sources_official/CHARLS_2011_Codebook_extracted.txt`。之后补入的`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`显示DA010是按DA007已报告病种询问的当前治疗多选题，并列出中医、西医、其他治疗和“以上皆无”。Codebook频数没有用作变量标签或分析N。

受保护的本地准备表中，8个病种组的DA010选项字段均有值与题项索引相符；但7组存在“以上皆无”与至少一个治疗选项同时非缺失的少量记录。此汇总 QA 只在本机执行，输出不含ID、逐人值或频数；具体结果留在本机 `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\chronic_treatment_storage_2011_aggregate_qa.csv`。由于该重叠与问卷选项结构不一致，且本地准备表的原始发布包身份、字段合并来源、缺失/跳题编码及DA007适用分母尚未完成逐项回溯，不能判断是原始记录、准备过程还是特殊存储导致，也不能解除`DO NOT ANALYZE`。不得把空白直接解释为No，不得把“以上皆无”解释为无疾病或未治疗。

映射修订脚本：`scripts/build_chronic_disease_ancillary_crosswalk.py`。本轮本地汇总审计脚本：`scripts/audit_2011_chronic_treatment_storage.py`；它只读取DA010的32个选项字段并写入私有汇总QA目录。生成位置：`audit/chronic_disease_ancillary_variable_mapping_v1.csv`及网站领域元数据；此批是8条映射、0个新概念，状态仍锁定。
