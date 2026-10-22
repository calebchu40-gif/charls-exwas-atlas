# 慢病辅助题值标签导入复核（2026-10-22）

## 范围与结果

依据 `audit/chronic_disease_ancillary_variable_mapping_v1.csv` 中已完成逐波官方 Codebook/问卷语义复核的非空标签，将原先未进入主目录的慢病辅助题标签接入 `audit/charls_atlas_candidate_fields_v0.csv` 与站点目录。新增规则只接受两类明确状态：既往波次自知疾病/预加载题；以及Codebook明确类别的条件性选项。其余未审、答案存储未核实或状态不匹配的标签不因本次修改而导入。

新增显示的13个波次字段为：

- 9个自知疾病题 `ZDA008_1_`、`ZDA008_5_`、`ZDA008_11_`，覆盖2013、2015、2018。2013显示 `1=Yes; 2=No; 3=Don't know`，2015和2018只显示 Codebook 明列的 `1=Yes`，不推断其他编码。
- 2011 `DA011S3`（`3=None of the above`，仅标识被选中的选项，不能将未选中代码当作No）。
- 2013、2015、2018 `DA019_W2_1`（`1=Yes; 2=No`，保留既往中风受访者条件性重访路由；不得与全样本中风患病状态合并）。

同轮将2011 `DA020S2` 两份官方映射中的文字统一为 `2=Taking antidepressants (selected option; unselected storage code not inferred)`，消除了选项说明详略不同造成的标签冲突。这个字段仍是条件性、多选治疗方式信息，不代表诊断；未选中或空白不推断为No。

## 验证

- 84条慢病辅助映射中所有84条非空标签都与主目录逐波字段精确相同；慢病辅助子集标签冲突为0。
- 对既往波次自知疾病/预加载项与仅表示选中项的字段，网页在标签旁展示路由/未选中解释提示。
- E/P目录标签行数为2,691；该次目录重建时唯一未决标签冲突是2013 `fn056_w2_5`，按既有分析锁定保留。
- 33项 `DO NOT ANALYZE` 锁定与逐项分流清单精确一致；全量元数据流水线成功。
- 未读取受访者回答、未使用 Codebook 频数估计样本量、未拟合关联模型。标签存在不代表字段分析资格已经确认；条件路由、未选中值存储、特殊缺失码和合法数据发行版本仍须在有授权的数据文件中核实。

## 可复现入口

标签接受规则位于 `scripts/build_charls_atlas_catalog.py`；2011 DA020标签语义由 `scripts/build_2011_psych_treatment_crosswalk.py` 生成。执行 `python scripts/build_ep_atlas_metadata.py` 可重建目录及网站元数据。
