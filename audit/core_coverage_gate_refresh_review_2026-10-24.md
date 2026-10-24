# 受控核心概念覆盖复验（2026-10-24）

重新运行 `scripts/build_core_concept_coverage.py`，仅读取本机 `%LOCALAPPDATA%/CHARLS_ExWAS_Atlas/derived_wave_tables` 中已获授权的波次准备表。程序输出保留在同一非同步私有根目录的 `qa_outputs/`，包括概念可用性、字段非空配对诊断和构建元数据；刷新日志也留在该目录。未把受访者记录、ID、逐对人数、覆盖率或文件哈希复制到仓库或网站。

本轮确认的样本框门槛状态：

- 2011：准备表中没有独立基线样本标志；结果只能解释为基线框架内的字段可用性诊断。
- 2013：`crosssection` 和 `longitudinal` 两个官方标志仍缺失；脚本对该波关闭逐对人数输出，没有从权重是否非空推断样本资格。
- 2015、2018、2020：准备表含官方 `crosssection` 字段，诊断按 `crosssection=1` 筛选。此筛选仍未确认每个字段所属模块的问卷资格、特殊值、测量质控、专用子样本权重或方差设计。

因此这些文件只用于字段覆盖/缺失路径排查，不是正式分析样本流，也不是模型 N、加权代表性人数或 ExWAS 结果。活动模块的随机子样本标记代码含义仍未核实；测量子样本和血检权重需另按官方说明配置。2013 只有在获准门户取得并核验官方 Wave 2 `Weights.dta` 后，才能恢复样本标志并重建准备表。

输出文件名：`core_concept_coverage_v1.csv`、`core_concept_dictionary_v1.csv`、`core_pairwise_complete_n_v1.csv`、`core_wave_pair_summary_v1.csv`、`core_concept_status_summary_v1.csv`、`core_coverage_build_metadata_v1.json`。文件只存在受控本机 QA 目录，不属于可提交的项目材料。
