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

证据来自`sources_official/CHARLS_2011_Codebook_extracted.txt`中DA010按病种列出的字段标签与选项索引。Codebook频数没有用作变量标签或分析N。现有2011基线英文问卷可用文件不含与这些英文标签逐字对应的完整题页文本，因此此处只认定Codebook中的字段—病种身份和题项索引，不声称已复核全部中文问卷路由。

字段作为“以上皆无”选项保留在原病种的治疗方式概念内；缺失/跳题、选择该项与其他选项的互斥性、二元存储方向和真正适用分母，仍须依据官方发布字段说明并在有权限的数据环境按规则验证。因项目当前没有使用者级CHARLS数据且未读任何个人记录，这8条的映射状态为待验证，明确标记`DO NOT ANALYZE`，不能据此推断未治疗、无疾病或No。

修订脚本：`scripts/build_chronic_disease_ancillary_crosswalk.py`。生成位置：`audit/chronic_disease_ancillary_variable_mapping_v1.csv`及网站领域元数据；此批是8条映射、0个新概念。
