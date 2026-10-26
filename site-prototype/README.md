# CHARLS ExWAS Atlas 原型

这是一个本地静态查询原型，读取 `dist/` 中从CHARLS官方问卷、代码本及审计整理的字段级公开元数据。页面展示候选暴露（E）、候选表型（P）、字段角色、来源波次、答案标签、单位、路由及审校状态；不含受访者微观记录，也没有拟合或审查通过的关联结果。

当前目录覆盖2011、2013、2015、2018、2020五轮。最新全量重建见项目根目录 `README.md` 和 `audit/current_directory_snapshot_2026-10-22.md`。波次字段概念共现只表示目录元数据覆盖，不是实际人数、配对样本量或关联结果。

官方抽样权重核查记录在 `audit/charls_wave_sampling_and_weight_status_2026-10-22.md`。2018横截面权重有不同目标和非应答调整；2013提供独立横截面生物标志物权重；面板、体检/血样子样本须按各波官方说明处理。Wave 4权重和Sample_Info字段存在于本机受控准备表，但尚未核对其对应官方源文件的版本与哈希；现存历史聚合审计显示五波所有受访者的`communityID`均可匹配官方2013 PSU映射表；这仅验证社区ID键覆盖，原始文件版本及逐波适用性仍需重核，实际方差分层字段/估计方案尚未验证。2013准备脚本现要求保留官方`crosssection`与`longitudinal`标记，并在缺失时停止；由于原始发行包未在项目目录内，当前尚不能重建并拟合设计校正关联或发布实际pairwise N。Wave 5 年龄目标总体仍待官方样本信息与权重源文件校验，具体哈希和核对步骤见 `audit/wave5_sampling_file_source_verification_2026-10-22.md`。结果表规范使用 `audit/EXWAS_result_schema_v2.csv`。

启动：在项目根目录运行 `python -m http.server 8767 --bind 127.0.0.1 --directory site-prototype\dist`，然后访问 <http://127.0.0.1:8767/>。数据由 `scripts/build_ep_atlas_metadata.py` 生成。

只有在目标人群和资格、变量比较性、官方权重与方差设计、缺失处理、多重检验方案均落实，并获得相应数据许可后，才能接入通过披露审查的聚合关联结果。不得把代码本频数或字段共现数解释为个体分析结果。


2026-10-26更新：2014 Life History候选视图现有40个概念组、1,029条字段映射（E 1,001、P 28），包括饥荒序列、亲代/抚养人、兄弟姐妹家庭史、亲代历史社会背景和80岁以上受访者的历史家庭背景。抚养人不必然等于生物学父母；家庭层历史报告不是受访者临床表型。C8选项5及C1_g3选项8存在中英文问卷表述不一致，页面明示。官方发布说明明确该特殊调查无权重，因此仍单列，不计入常规波次E/P配对覆盖，不代表分析资格。字段映射行数不等于独立概念数、分析样本量或关联结果。审计见 `audit/life_history_famine_sequence_review_2026-10-26.md`、`audit/life_history_guardian_health_context_review_2026-10-26.md`、`audit/life_history_sibling_module_review_2026-10-26.md`、`audit/life_history_parent_module_review_2026-10-26.md`、`audit/life_history_historical_family_class_review_2026-10-26.md` 和 `audit/life_history_parent_social_context_review_2026-10-26.md`。提交 `d277385` 已上线；530项测试、公开包、92条分析锁和前端语法检查通过。

提交 `60360b1` 的 C1/C2 抚养人就业元数据复核已上线（app v141 / JSON v8）：覆盖8个结构化字段，细化了既有概念中的条件路由和缺失语义；自由文本职业详情排除。审计见 `audit/life_history_parent_employment_review_2026-10-26.md` 和 `audit/life_history_parent_employment_coverage_2014_v1.csv`。全套531项测试及公开包/分析锁检查已通过。

提交 `17d0c5c` 的 E7–E8/G1–G2敏感历史项目已上线（app v142 / JSON v9），使专题扩至42概念、1,033字段（E 1,005、P 28）。该批不包含参与者值或Codebook频数；警方拘留/指控仅标作敏感司法系统接触元数据，后续分析需要单独伦理、隐私和披露审查。审计见 `audit/life_history_sensitive_history_review_2026-10-26.md`。全量532项验证通过。

首页已调整为组会演示入口：先说明项目范围，再进入暴露/表型目录或关联状态；其余专题页收纳在更多专题目录。当前关联页明确显示0条已审查真实结果，目录字段数与潜在配对数均不是分析结果。
