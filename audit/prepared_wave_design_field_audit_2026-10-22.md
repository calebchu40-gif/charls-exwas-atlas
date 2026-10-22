# 本机受控CHARLS派生表的抽样设计字段审计

日期：2026-10-22。只在本机授权派生表上读取数据文件元数据和受控聚合质量信息；输出不含受访者ID、个人行、权重数值或小单元格。逐波权重、样本标记与PSU候选字段见[`survey_design_field_coverage_v1.csv`](survey_design_field_coverage_v1.csv)，可复现脚本为[`../scripts/audit_survey_design_fields.py`](../scripts/audit_survey_design_fields.py)。该脚本不读取受访者ID，并将少于10人的类别格抑制。

## 本机派生表已含字段

五个波次准备表均包含 `communityID`。2011、2013包含个人权重及其专用生物标志物权重；2015包含个人权重及`Biomarker_weight`；2018、2020包含`INDV_weight`和`INDV_weight_ad2`。2015、2018、2020表内也有`crosssection`样本标志。故此前“权重和Sample_Info尚未在本机授权资料中取得”的说法不准确：权重和样本文件字段已进入当前派生分析表。

这些表没有字段名中明确写作`PSU`或`stratum`的列；不能据此断言没有可用PSU。CHARLS 2011官方用户指南把村/居委会定义为PSU，Wave 2发布说明列出独立`PSU.dta`，并说明社区ID跨Wave 1/2不变；Wave 4/5指南称PSU信息与此前波次相同。现存历史聚合审计`charls_psu_mapping_aggregate_v1.csv`显示五波全部受访者的非缺失`communityID`均可在官方2013 PSU映射表中找到（每波未匹配ID为0）。这验证了社区ID键覆盖，不验证映射文件发行版本、跨波抽样框的完全等价性或方差设计。当前个人派生表的来源档案不在机，故需取得原始文件后复核PSU映射与版本哈希；聚合表中的446–450个社区数也不代表设计自由度。

目前未发现独立发布的显式方差分层ID或复制权重。设计材料说明抽样有分层和隐式排序，但没有授权我们由省份、城乡类型、县市代码或`communityID`推算实际分层。未核实真实发行文件的stratum定义前，不声称完整的CHARLS设计校正方差估计已就绪。

## 重要准备脚本问题

Wave 2（2013）的官方`Weights.dta`同时包含横断面/纵向样本标志和权重；准备脚本的`split_weights()`此前只保留名称含weight的列，因而当前2013派生表没有`crosssection`或`longitudinal`标志。此时不能通过权重是否非缺失来倒推样本类别。现已修正`prepare_charls_wave_tables.py`：下次从原始发行文件重建时，个人权重表会把官方样本标志一并按`ID`合入；若2013权重文件缺少任一官方标志则立即报错，不继续生成可能被误用的派生表。测试覆盖标记保留、标记冲突阻止个人权重表、完全相同重复行的去重以及缺失官方标记时失败关闭。2015–2020的`crosssection`来自`Sample_Info`，当前表已保留。

原始发行压缩包目前不在已记录的数据目录中，故没有在本轮重建五个含个人记录的派生表。更正的脚本与现有准备表不一致时，仍必须从用户获准的原始发行包完整重建并重新校验ID唯一性、模块合并和来源版本。不得用非缺失权重代替官方样本标志，也不得在未确认目标总体前直接将所有权重视为等价。

## 当前可做与不可做

- 可在定义清楚的2015/2018/2020横断面目标人群中，依据官方`crosssection`及合适的个人权重制定分析预案；仍需核验权重发行版本、权重字段的适用范围和协变量/结局模块资格。
- 2011基线和2013目前不能直接套用同一套横断面筛选：2011按基线用户指南界定目标样本；2013先重建并恢复官方cross-section/panel标志。
- 历史聚合审计支持`communityID`与官方2013 PSU映射表键覆盖匹配；仍需用原始包重核来源版本、逐波适用性及权重适用性。
- 在方差分层/适用方差估计方案未证实前，不运行或发布宣称完整设计校正的ExWAS p值、置信区间或关联结果。暂时保留正式模型数为0。

## 2026-10-22 本地受控准备表复验

对本机 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\derived_wave_tables` 中已获准使用的准备表重跑了结构校验和核心概念可用性汇总。五波表均可读，`ID` 缺失/重复检查及波次一致性检查通过；复验清单、文件哈希和模块合并QA只写入同一受控根目录的 `qa_outputs`，未进入仓库。另为31个核心候选概念重建了逐波字段非缺失与配对可用性表。该表仅用于检查字段覆盖和识别缺项，不包含样本资格、权重筛选、测量质控、多重插补或模型排除，不能称作分析样本量或关联结果。

模块合并QA原字段名`match_pct_of_base_nonmissing`的数值实际是0–1比例，易误读为0–100百分数。准备脚本现改用`match_rate_0_to_1`；本机复验器兼容读取旧字段并以新名称输出。该修正只消除尺度歧义，不改变合并记录。模块匹配率低也不能单独判作合并错误，需结合模块路由和样本资格判断。

这次复验没有改变关键闸门：2013当前派生表仍缺官方 `crosssection` / `longitudinal` 样本标志，2011/2013样本资格也不能用非缺失权重代替；2013/2015活动模块有子样本设计，客观体检/血检还要用专用资格与权重。原始官方发行ZIP/RAR和来源校验值仍未在受控数据根目录，因此已修正的2013合并逻辑尚未从源档案重建验证。所有派生表与逐对精确可用人数仅保留在本机受控目录，禁止推送到GitHub或放进协作者交接包。

## 官方资料

- [`CHARLS 2011 National Baseline User Guide`](../sources_official/CHARLS_2011_National_Baseline_Users_Guide_extracted.txt)：村/居委会作为PSU及抽样排序说明。
- [`CHARLS 2013 Wave 2 Release Note`](../sources_official/CHARLS_2013_Wave2_Release_Note_extracted.txt)：横断面与纵向权重、`crosssection`/`longitudinal`旗标、PSU文件及社区ID说明。
- [`CHARLS 2018 User Guide`](../sources_official/CHARLS_2018_Users_Guide_extracted.txt)：Wave 4权重、Sample_Info、PSU信息与跨轮样本定义。
- [`CHARLS 2020 User Guide`](../sources_official/CHARLS_2020_User_Guide_English_extracted.txt)：Wave 5权重、Sample_Info及PSU延续说明。
- 原始数据许可、输入路径及重建方式见[`DATA_ACCESS_AND_REPRODUCTION.md`](DATA_ACCESS_AND_REPRODUCTION.md)。
