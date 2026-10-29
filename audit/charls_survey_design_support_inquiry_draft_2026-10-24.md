# CHARLS 抽样设计与权重官方咨询稿（未发送）

> 历史版本：Wave 2 `Weights.dta` 及多波次部分设计文件现已入库并完成来源/表头审核；本稿中“仍缺 Wave 2 Weights.dta”等内容已过期。当前可用问题请见 [`current_charls_official_inquiry_draft_2026-10-30.md`](current_charls_official_inquiry_draft_2026-10-30.md)。本稿从未发送。

日期：2026-10-24  
状态：供项目负责人使用其本人获准的 CHARLS 账号或官方支持渠道发送；本项目未代发邮件、未提交数据访问申请，也未附带任何受访者数据。

2026-10-26 官方抽样页复核后补充：页面把县级单位按 NBS 地区、城乡县区类型和人均 GDP 排序/分层后系统 PPS 抽取，并说明每县抽 3 个村/社区、30 个大型社区有拆分。需一并确认该抽样过程在公开发布数据中的官方方差估计对应方式。CHARLS 联系页当前列出的地址为 `charls@whu.edu.cn`（页面标注日期为 2019-09-13）；发送者应先重新确认其仍有效。

## 咨询目的

本项目计划按 CHARLS 波次开展横断面暴露—表型关联分析。官方说明支持村/城市社区作为 PSU，并描述分层、多阶段抽样；但现有已审阅公开文件未确认本项目各波可直接用于 Taylor 线性化的方差分层标识或官方复制权重。对 2013 波，准备表还缺 Wave 2 `Weights.dta` 提供的 `crosssection` 和 `longitudinal` 样本资格标记。下列问题旨在取得官方字段/方法指导，不请求任何未公开个体记录。

## 中文邮件草稿

**主题：咨询 CHARLS 各波公开数据中的方差设计字段及 Wave 2 权重文件**

CHARLS 数据团队您好：

我们正在依据 CHARLS 官方用户手册、问卷、代码本和发布说明，准备一个按波次开展的横断面暴露—健康表型关联研究。研究者会使用本人获准账号取得的数据；目前只希望确认官方文件结构和调查方推荐的方差估计方法，不会向网站发布个人级记录。

烦请协助确认以下事项：

1. 对目前公开发布的 Wave 1（2011）、Wave 2（2013）、Wave 3（2015）、Wave 4（2018）和 Wave 5（2020），官方数据包中是否提供用于 Taylor 线性化方差估计的设计分层变量、复制权重，或其他等价设计信息？如有，请告知每波对应的文件名、字段名、数据版本和连接键。
2. 官方抽样页描述县级单位按 NBS 地区、城乡县区类型及人均 GDP 排序/分层后系统 PPS 抽取；每个县级单位再抽 3 个村/城市社区作为 PSU，且 30 个大型社区曾拆分。对于方差估计，官方是否建议把县级单位作为方差层、社区作为 PSU，或使用其他多阶段/Taylor 线性化设置？第一阶段县级系统 PPS 和后续社区抽样应如何纳入方差？30 个拆分社区在发布 PSU 文件中如何对应最终抽样单位？若发行文件未提供明确设计字段或复制权重，CHARLS 是否推荐正式或近似方差方法？是否允许依据排序或地理字段重建方差层？
3. Wave 2 官方页面列出的 2015-11-18 版 `Weights.dta`（网页 SHA1：`22c4fc89df2e55fa8faf051e88830eebe0e035c0`）是否仍是应使用的官方文件版本？该文件是否包含 `crosssection`、`longitudinal`、横截面权重（含/不含非应答调整）和 `Biomarker_weight`？各字段的官方定义、适用总体和推荐匹配键是什么？
4. Wave 1 与 Wave 3 的血液生物标志物、Wave 1–3 的体格/功能测量，以及 Wave 1 的 Cystatin C 年龄子样本，分别应使用哪些官方权重或样本资格标记？专用生物标志物权重是否校正对应模块无应答？如不同测量项目适用范围不同，是否有逐项目/逐模块的官方说明？
5. 对 Wave 5（2020 发布包）及其后单独开展的调查，能否确认各自的抽样目标人群、适用权重与设计字段版本，避免把后续调查文件或采集计划错误并入 2020 Wave 5？

我们已从公开说明确认 Wave 2 `Weights.dta` 含横截面和纵向样本标记，并确认公开页面将 PSU 与 Weights 列为独立文件。若需要进一步核验，我们可以通过获准账号重新下载相应官方文件，并按要求提供文件版本或校验值；不会通过非官方途径取得文件。

感谢帮助。若以上问题应分别咨询数据发布与抽样方法团队，也烦请告知适当的官方渠道。

此致  
敬礼

（研究者姓名 / 单位 / 获准 CHARLS 账号信息由发送者填写）

## English email draft

**Subject: Clarification on released variance-design variables and the Wave 2 weights file**

Dear CHARLS Data Team,

We are preparing wave-specific cross-sectional analyses of associations between candidate exposures and health phenotypes, using CHARLS data obtained by each researcher through their own authorized account. We have reviewed the official user guides, questionnaires, codebooks, and release notes. We are seeking clarification about released file structure and recommended variance estimation only; we are not requesting unpublished respondent records and will not publish respondent-level data.

Could you please clarify the following?

1. For the publicly released Wave 1 (2011), Wave 2 (2013), Wave 3 (2015), Wave 4 (2018), and Wave 5 (2020) files, are stratum identifiers, replicate weights, or equivalent design information available for Taylor-linearized or other design-based variance estimation? If so, please identify the file, variable, release version, and join key for each wave.
2. The official sample page describes systematic PPS selection of county-level units after sorting/stratification by NBS region, urban-district/rural-county type, and GDP per capita; three village/urban-community PSUs are then sampled within each county-level unit, and 30 large communities were split. For variance estimation, does CHARLS recommend county-level variance strata with community PSUs, or another multistage/Taylor-linearization specification? How should first-stage county selection and subsequent community selection enter the variance? How do the 30 split communities map to final PSUs in released files? If no explicit design variables or replicate weights are released, what official or approximate method is recommended? May researchers reconstruct variance strata from the sorting order or geographic fields?
3. Is the Wave 2 `Weights.dta` package listed on the official page as updated 2015-11-18 (SHA1 `22c4fc89df2e55fa8faf051e88830eebe0e035c0`) still the correct official release? Does it contain `crosssection`, `longitudinal`, cross-sectional weights with and without nonresponse adjustment, and `Biomarker_weight`? Please advise the official definitions, target populations, and recommended merge key.
4. Which official weights and eligibility flags apply to blood biomarkers in Waves 1 and 3, physical/functional measurements in Waves 1–3, and the age-restricted Cystatin C subsample in Wave 1? Do the dedicated biomarker weights adjust for nonresponse in the relevant module? Is there item- or module-specific guidance where eligibility differs across measurements?
5. For the 2020 Wave 5 release and any later separately conducted survey, could you confirm the target population, applicable weights, and design-variable release versions so that later survey files or planned measurements are not incorrectly merged into Wave 5?

The public Wave 2 release note states that `Weights.dta` includes cross-sectional and longitudinal sample flags, and the public page lists PSU and Weights as separate files. If necessary, we can redownload the files through an authorized account and provide the release version or checksum for clarification. We will not obtain files through unofficial routes.

Thank you for your guidance. If these questions should be directed to separate data-release and sampling-method contacts, please let us know the appropriate official channels.

Sincerely,  
(Researcher name / affiliation / authorized CHARLS account details to be completed by the sender)

## 官方依据与当前项目链接

- [CHARLS 2013 Wave 2 官方数据页](https://charls.pku.edu.cn/en/Data/a2013_CHARLS_Wave2.htm)：列出 2013 `Weights`、`PSU` 文件及公开校验值。
- [CHARLS Wave 2 Release Note（2015-11-18）](https://charls.pku.edu.cn/en/data/Release2013.pdf)：说明横截面/纵向样本标记、两套横截面权重和生物标志物权重。
- [CHARLS 官方联系页](https://charls.pku.edu.cn/en/Contactus/Contactus.htm)：页面当前列出 `charls@whu.edu.cn`，标注日期为2019-09-13；发送前由研究者确认当前地址及适用支持渠道。
- 项目对官方字段与目标总体的核查：[`survey_design_weight_review_v1.md`](survey_design_weight_review_v1.md)、[`prepared_wave_design_field_audit_2026-10-22.md`](prepared_wave_design_field_audit_2026-10-22.md)。
- Wave 2 文件安全接收与核验步骤：[`wave2_official_weight_intake_2026-10-23.md`](wave2_official_weight_intake_2026-10-23.md)。
