# Wave 1 estimand、血检权重与方差设计准入审查

日期：2026-10-29  
状态：官方来源复核已完成；调查设计门仍未通过；未拟合暴露—结局关联模型。  
范围：CHARLS 2011 基线血液化验结局与家户/社区暴露的横断面分析。

## 1. 已确认的目标样本与年龄域

2011 基线在住户样本中选择 45 岁及以上的主要受访者；如果主要受访者有配偶，配偶不论年龄都会被访谈。官方血液用户手册将血检目标样本明确为全部基线主要受访者与其配偶。因此不能仅凭“CHARLS 面向45岁及以上人群”就把每位配偶都删掉，也不能把全部主访者/配偶不加说明地称为一般中国成年人。

**本项目的预设主 estimand 候选**：2011 基线目标总体中年龄 ≥45 岁的家庭居住人口，使用官方血检权重；年龄限制作为调查设计 domain/subpopulation 实现，完整样本和 PSU 结构仍保留在设计对象中。分析报告须明确 CHARLS 的主要受访者/配偶抽样结构及机构居住人群不在基线抽样框内。若方法审查认为配偶的个人权重与该年龄 domain 不足以支持所需总体解释，则降格为“基线符合资格的主要受访者/配偶样本中的加权关联”，不作更宽泛代表性声明。

## 2. 血液结局权重

官方 CHARLS Blood Sample Users' Guide 将 `bloodweight` 定义为同时校正家户/个人主问卷无应答及血液采集参与无应答的专用权重；其起点是个人样本权重，血检应答模型使用社区虚拟变量、年龄、性别及其交互、教育，并将逆应答概率限制在第99百分位。该权重适用于本项目的常规血液检测候选，不应未经论证以 `ind_weight_ad2` 或一般 biomarker 权重替代。

执行时须先按官方定义和已审源字段确认 `bloodweight` 的发行来源、ID连接、值标签/缺失状态与年龄 domain；不能用权重非缺失反推血检资格，也不能先删掉非域记录再建方差设计对象。

**胱抑素 C 单独阻断**：官方指南说明血样受访者中 ≥70 岁者全部检测，70 岁以下另抽随机子样本。现有指南未给出该二阶段检测的独立入样概率或专用二阶段权重。因此，在找到并审核相应抽样权重/方法前，胱抑素 C 不进入与其他血液指标相同的全体血检主检验族。

体格测量、血压、肺功能/体能等非血液表型需另按所属模块的资格和权重审核，不能沿用上述 `bloodweight` 决定全部表型的权重。

### 2026-10-29 受保护官方框架/权重核对

从官方 Wave 1 四件套重新构建的版本化受访者表已通过当前 source-manifest/hash gate。受保护聚合审计仅读取 ID、`communityID`、`ind_weight_ad2` 与 `bloodweight`，未读取问卷、暴露或结局取值。CHARLS National Baseline/Blood Users' Guides 报告的 interview/blood target 总数，与 Codebook 报告的 `ind_weight_ad2` 非缺失数一致；本地官方 Weight 文件对应的非缺失 ID 总数也与该公开目标数相符。与此同时，All Data 的 `Demographic_Background` spine 比目标分母少一小组记录，且 Weight 中有正调整权重的记录无法连接到该 spine；精确差异和键留在私有 QA，不能宣布逐人 ID 对账完成。

官方 Blood 文件中的全部 ID 均可连到重建 person spine，`bloodweight` 有效记录总数与 Blood Guide 报告的 complete sample 一致。由此，血液结局分析的官方目标分母/血液完成样本在**聚合层面**得到一致性支持，`bloodweight` 仍是血液结局的首选权重来源；该判断不等于估计设计完整，也不解决年龄域、暴露模块缺失、拆分子 PSU、县级分层或方差方法。目标框门应记为 `partially_reconciled`，而不是 fully passed。模型仍关闭。

## 3. PSU 与方差估计

CHARLS 官方抽样说明将村/城市社区列为通常的 PSU，并说明大于2,000户的一些大型社区可以将地理子区/原居委会作为 PSU；共30个社区以此方式拆分。官方指南还说明县级单位按地区、城乡类型和人均 GDP 排序后进行系统 PPS 抽样。

已核对的公开发布字段包含社区/PSU键及地理/城乡背景字段，但没有可识别的正式方差 `stratum ID` 或复制权重字段。个人/PSU发行结构中也没有明确的 respondent-to-sub-neighborhood PSU crosswalk。故：

- `communityID` 是官方设计中村/社区层 PSU 的可用候选键，但不足以证明30个拆分社区内的最终子 PSU 已被正确识别。
- `province`、`city`、`urban_nbs`、`areatype` 是地理/抽样背景字段；不得将它们拼成伪分层变量。
- 血检非应答模型中的社区虚拟变量属于权重构造，不等于方差分层ID。
- 仅按 `communityID` 聚类且不纳入显式方差层，最多是标记清楚的近似方差方案，不能宣称完整复现 CHARLS 分层、多阶段 PPS 设计。
- 在子 PSU 映射和最终方差方案未得到文件证据或独立方法审查之前，不运行正式关联模型，不报告设计校正 p 值/置信区间。

## 4. 决策与下一步

1. 将主分析目标锁定为45岁及以上域估计；把配偶年龄不限的抽样事实写进分母定义，并以调查 domain 方式处理年龄范围。
2. 血液结局用 `bloodweight`；非血液结局按模块另行判定权重和资格；胱抑素 C 暂不进入同一主族。
3. 继续检索已取得的 Wave 1 官方材料和源包中是否有受访者到子 PSU 的正式映射、方差层或方差估计建议；只接受可追溯的官方字段/定义，不从ID结构或地理变量反推。
4. 若公开资料和发行包仍不能关闭拆分 PSU/方差层问题，形成一个明确标为近似的候选方案（社区 PSU 聚类、无伪造层），并在拟合前作独立方法审查。若近似不获接受，需由研究者经本人获准的 CHARLS 支持渠道询问正式建议；本项目不会代发联系信息。
5. 设计门关闭之后，再冻结完整105项试点的权重、估计总体、实验室有效值、协变量DAG、诊断和多重检验家族，然后复核与运行。

## 5. 获准发行包的表头复核（2026-10-29）

### 2026-10-29 元数据核查结果

对受保护服务器中 All Data 压缩包的15个 Stata 模块逐一检查表头元数据，未读取观测值。`community.dta` 是唯一包含 `sub_commuID` 的模块，且同时有 `communityID`；其余14个模块没有 `sub_commuID`。其中 `health_care_and_insurance.dta` 无法由 pyreadstat/ReadStat 读取元数据，随后使用 pandas Stata reader 的 header-only 路径取得表头（Stata 113，480个变量）；未读取参与者记录。

官方 `PSU.dta` 表头包含 `communityID`、省/市、NBS城乡、地区类型和版本标识；没有子 PSU、方差层或复制权重字段。`Weight.dta` 表头有社区、家庭、个人键及多种访谈/生物标志物权重；Blood 文件有 `bloodweight`。字段名与标签不证明年龄域或方差设计已适用。

受保护目录的只读准入检查确认来源身份及准备表 provenance/hash 门通过；随后 `require_wave1_analysis_readiness` 因缺少与当前来源和分析计划绑定的审阅记录而拒绝模型执行。来源核验已通过，但样本框、年龄域、PSU/方差和真实模型门仍未通过。

## 6. 官方依据

- [CHARLS 官方抽样介绍](https://charls.pku.edu.cn/en/About/Sample.htm)：基线抽样框、社区 PSU、超大型社区子区拆分及样本形成。
- [CHARLS 2011–2012 National Baseline Users' Guide](https://charls.pku.edu.cn/wenjian/jixiandiaochashujuyonghushiyongshouce2013-04-07.pdf)：主要受访者年龄筛选、配偶纳入、抽样权重构造。
- [CHARLS Blood Sample Users' Guide](https://charls.pku.edu.cn/wenjian/xuejianshujuyonghushouce.pdf)：血检目标样本、`bloodweight` 构造和胱抑素 C 子样本测量。
- 项目已有源材料：`sources_official/CHARLS_2011_National_Baseline_Users_Guide_extracted.txt`、`sources_official/CHARLS_2011_Blood_User_Guide_extracted.txt`、`sources_official/CHARLS_2011_Codebook_extracted.txt`。

本审查没有纳入参与者记录、个人级统计、匹配率、样本计数或分析结果。与重建文件有关的结构性核验明细留在服务器受保护 QA 区。
