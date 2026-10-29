# CHARLS Wave 2 权重与目标估计量来源复核

日期：2026-10-24  
来源范围：CHARLS 官方 2013 Wave 2 Release Note（VersionID 20151118）、官方 Harmonized CHARLS Codebook（Version D, June 2021）、Wave 2 资料页。只审阅发布文档，不读取个体数据。

**2026-10-30 状态更新：**下文第1点关于准备表缺少 `crosssection`/`longitudinal` 的状态已被后续官方入库与 Wave 2 重建取代。官方 Wave 2 Weights 包已通过发布来源/哈希与表头核验；两个样本标记和模块权重已进入独立受保护 Wave 2 准备表。权重适用性、模块资格、目标总体、年龄算法和 PSU/方差审查仍未闭环。其余对官方权重含义及禁止臆造方差层的说明继续适用。

## 官方文件能确认什么

Wave 2 Release Note 将 `Weights.dta` 和 `PSU.dta` 列为与调查模块配套发布的数据文件，并将 `Weights.dta` 说明为包含横截面/纵向权重及受访者家户成员 ID 的文件。发布说明明确列出 `crosssection` 和 `longitudinal` 两个资格标记，并提醒横截面样本与纵向样本可能不同；权重非缺失或为正不能替代样本资格判断。

该说明区分两套横截面权重（是否包含非应答调整）和纵向权重。纵向权重基于基线权重，并使用“基线受访者是否参加第二波”的逆概率调整；构造时将死亡视为响应。故同一波的横截面和纵向估计目标不能混为一谈，不能把横截面权重当面板权重。

Wave 2 另提供横截面生物标志物权重：以个体横截面权重乘以生物标志物响应概率的逆概率因子，并将该因子在第99百分位截尾。Release Note 明确没有提供纵向生物标志物权重。实验室表型分析因此需要单独确认目标总体、样本资格、适用的生物标志物权重和分析物发布覆盖；不能用普通横截面权重的存在推定其已调整生物标志物模块无应答。

官方说明将 `PSU.dta` 列为包含省、市和区域类型信息的文件；Harmonized CHARLS Codebook 说明抽样按城乡地区人均 GDP 分层并采用县/区—村/社区—家庭多阶段 PPS，社区/村为PSU。公开文档审阅仍未确认可直接用于方差软件的 Wave 2 方差层 ID 或复制权重。省、市和区域类型是地理/抽样背景字段，不能仅因其出现在 PSU 文件中就重建成官方方差层。

## 对当前项目的执行约束

1. **已完成的来源/字段准备：**官方 `crosssection` 与 `longitudinal` 标记已从经核对版本的 `Weights.dta` 恢复到独立 Wave 2 准备表。官方权重标记与具体分析变量的模块资格仍须分开核实。
2. 在官方文件来源、版本、校验值、变量标签及受访者链接键核验前，不运行 Wave 2 正式模型。成功合并样本标记也不代表权重已选对或方差设计已闭环。
3. 普通健康问卷、血检/生物标志物、随机半样本模块分别定义目标估计量和权重适用性；任何发布的权重/样本资格规则均保留来源与版本。
4. 当前没有经官方资料确认可用的 Wave 2 方差层标识。继续核验 PSU/Weights 文件的元数据和官方方差建议，不能用地区变量臆造 strata。

## 官方来源

- [CHARLS 2013 Wave 2 Release Note, VersionID 20151118](https://charls.pku.edu.cn/en/data/Release2013.pdf)，第1–2页。
- [CHARLS Wave 2 (2013) official release page](https://charls.pku.edu.cn/en/Data/a2013_CHARLS_Wave2.htm)，列出 Codebook、PSU、Weight 等文件及各自版本信息。
- [Harmonized CHARLS Codebook, Version D](https://charls.pku.edu.cn/en/team/Codebook.pdf)，第13–14页，调查设计和权重说明。

官方文件提供研究方法与数据结构说明；使用实际 CHARLS 微观数据仍须由每位分析者依当前注册/申请和数据使用协议取得许可。

## 2026-10-25官方入口复核

通过 CHARLS 官方 Wave 2 资料页再次核验：页面仍将 `Weights (updated on 18/11/2015)` 列为发行文件，SHA1仍为 `22c4fc89df2e55fa8faf051e88830eebe0e035c0`；页面同时显示 CHARLS 用户登录/注册入口。对应的官方 Release Note 仍标记 `VersionID: 20151118`，并确认样本旗标和三类不同权重口径（横截面含/不含非应答调整、纵向、横截面生物标志物）。这只是公开清单与文档的在线复核；本机仍未取得该二进制文件，不据此宣称完成数据下载或合并。

来源：[CHARLS 2013 Wave 2 official release page](https://charls.pku.edu.cn/en/Data/a2013_CHARLS_Wave2.htm)；[Wave 2 Release Note](https://charls.pku.edu.cn/en/data/Release2013.pdf)。

## 2026-10-29 intake update — official later-wave design files now available

The initial review noted that the Wave 2 archive was absent and that later-wave blood/sample inputs were not yet available locally. This is superseded by the current protected intake: Wave 2 Weights (official document 318), Wave 3 Weights/Sample_Infor/Blood (1152/1151/2088), Wave 4 Weights/Sample_Infor (2106/2107), and Wave 5 Weights/Sample_Infor (2210/2209) are available. Wave 3–5 additions were checked against the server's SHA-1-verified intake manifest and metadata-only header reviewed after local-copy SHA-256 matching. The detailed wave-specific status is recorded in `multwave_official_weights_blood_source_review_2026-10-29.md` and `multwave_weight_estimand_matrix_v1.md`. This update does not itself authorize modeling; wave-specific eligibility and survey design remain under review.
