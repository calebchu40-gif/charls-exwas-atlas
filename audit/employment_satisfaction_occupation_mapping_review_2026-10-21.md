# 就业满意度、预期停止年龄与职业编码补充映射（2026-10-21）

## 本轮审查结论

根据本地CHARLS公开版字段目录、各轮问卷及代码本，将此前未归属的就业字段中7个候选构念、13条波次—字段映射加入工作暴露crosswalk：

| 候选构念 | 来源字段 | 波次 | 处理边界 |
|---|---|---|---|
| 非农工作满意度 | `fk000_w3_1` | 2015、2018 | 五级有序自报；不等同于客观工作质量或农业工作满意度 |
| 一般预期停止工作年龄 | `fk003` | 2011、2013、2015 | 仅映射一般FK003；是主观预期，不是实际退休年龄 |
| 非农工作预期停止年龄 | `fk000_w3_2` | 2015、2018 | 与一般FK003和2020 FF004年龄/年份组件分开；2018锁定待核 |
| 自雇职业编码 | `fh005_gb`, `fh005_isco` | 2011 | GB与ISCO编码分列，需对应分类手册，不擅自转换 |
| 自雇行业编码 | `fh007_indc` | 2011 | 与雇员当前行业、职业分类分开 |
| 最近工作职业编码 | `fl017_gb`, `fl017_isco` | 2011 | GB与ISCO编码分列，与当前/自雇职业路径分开 |
| 最近工作行业编码 | `fl006_indc` | 2011 | 回溯最近工作行业，与最近工作职业分开 |

## 官方来源与编码风险

- 2015与2018官方代码本分别列出`fk000_w3_1`五个满意度类别：1=Completely satisfied、2=Very satisfied、3=Somewhat satisfied、4=Not very satisfied、5=Not at all satisfied。保留原序，不将代码本频数复制到站点。
- 2015代码本列出`fk000_w3_2`“Expected Age Stop Working”，观测最大值95；2018代码本同一字段族题签为“Expected Age When to Stop Working”，但摘要统计的最大值为2026。年龄题出现可能的年份值，不能自行推断某种转换；2018字段状态为`candidate; age-versus-calendar-year values unresolved; DO NOT ANALYZE until coding is clarified`。
- 2011/2013/2015代码本列出`fk003`“Age You Plan to Stop Working”。仅按一般预期停止工作构念保留FK003；`fc018`在多个波次存在不同题意，因此不并入。
- 2011官方Codebook字段目录确认`fh005_gb`, `fh005_isco`, `fh007_indc`, `fl006_indc`, `fl017_gb`, `fl017_isco`的变量代码/短标签。GB、ISCO与INDC字段分别保留。代码体系的详细值含义、版本/对应分类手册须在后续找到官方分类文档后再审核；不得把稀有职业代码未经披露审查放到公开结果中。

## 生成与验证

字段映射由`scripts/build_work_exposure_crosswalk.py`生成，值标签及站点JSON由`scripts/build_work_exposure_value_labels.py`生成，最终目录须通过完整入口`python scripts/build_ep_atlas_metadata.py`重建。该次完整构建后全局候选概念、映射数见`audit/current_directory_snapshot_2026-10-21.md`及`audit/ep_concept_mapping_coverage_v1.md`。不读取个体记录，不声称任何职业字段已获分析资格。

## 本地可追溯文件

- `sources_official/CHARLS_2011_Codebook_extracted.txt`：上述2011字段短标签与FK003条目。
- `sources_official/CHARLS_2015_Codebook_extracted.txt`：FK003、FK000_W3_1类别、FK000_W3_2摘要。
- `sources_official/CHARLS_2018_Codebook_extracted.txt`：FK000_W3_1类别、FK000_W3_2最大值2026冲突。
- `audit/raw_variable_catalog_v1.csv`：按波次核对字段是否存在。


