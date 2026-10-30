# Wave 1 空腹变量编码来源复核

**日期：2026-10-29**  
**状态：官方来源说明变量存在，但本次检索未找到官方数值代码映射；分析门继续关闭。**

## 复核问题

Blood 数据中的 `qc1_va003` 表示采血时是否空腹。拟定的105项试点包含血糖和甘油三酯；在冻结其分析domain、调整或敏感性方案前，需要把数值代码对应到“是/否”，并确认缺失码如何处理。

## 官方来源证据

- CHARLS《Blood Sample Users' Guide》说明受访者被要求过夜空腹；即使未空腹仍采血，并在数据中记录状态。指南同时指出非空腹样本的血糖可能偏高。见官方指南第8页（PDF第9页）及第16页（PDF第17页）。
- 官方 Wave 1 Blood 文件表头含 `qc1_va003`，但字段未带 value-label set。
- CHARLS 官方 2013 CodeBook 不含 `qc1_va003`；其内容是2013随访问卷模块，不能替代2011血液数据值标签。
- 复查 CHARLS 官方 Wave 1 下载页后，页面列出的相关文档是通用 Wave 1 Codebook 与 Blood Data Users' Guide，没有另列 2011 Blood 专用 Codebook 或 Blood Release Note。现已在服务器私有入库核验平台列出的通用 Codebook RAR，但该文件不含 Blood fasting 字段映射。官方 Blood ZIP 归档仅包含 Stata 数据文件，没有随包数据字典/README。见[官方 Wave 1 数据文档清单](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)。
- 2026-10-29 再次打开 CHARLS 当前官方 Wave 1 页面核对文档清单：仍列通用 Codebook 与 Blood data users' guide，没有新增 `qc1_va003` 专用代码本；该页面将 Blood 数据发布日期列为 2014-04-29。此为在线文档清单核对，不构成字段代码的数值映射。
- **官方归档核验（2026-10-30）：**服务器受保护入库中的 `2011_120_CHARLS_codebook.rar` MD5 为 `293eb9789ee559fe0d7099086a2aaf40`，与北大开放研究数据平台 CHARLS 2011 baseline v1.1 的 `CHARLS_codebook.rar`（文件136）登记值一致。归档在服务器 private/ 内提取；提取 PDF SHA-256 为 `fa1cb4fe315c95a290ff1b5b7431d32c2707055364a5a3f6749c13ebc25ca722`，检索文本 SHA-256 为 `21bd1638f1a968d70d3b634b713d90c8f5942037f65ab5036bfe558564b76c35`。仅对文档做字段名检索，未发现 `qc1_va003`、`va003`、`newglu`、`newtg`、fasting 或“空腹”编码定义。该来源核验补齐了通用 Wave 1 Codebook 的身份链，但仍未提供 Blood 文件 `qc1_va003` 的数字映射；分析阻断继续有效。归档及提取件始终留在服务器 private/，未复制到 GitHub、OneDrive 或公开网站。
- **服务器私有血液文件元数据复核（2026-10-30）：**在用户授权的受控目录，对 Wave 1 Blood `.dta` 仅调用 `pyreadstat.read_dta(..., metadataonly=True)`；未载入/检查受访者记录。文件元数据报告 11,847 行、19列，`qc1_va003` 的变量标签为 `Fasting`；该变量没有 `variable_to_label` 对应值标签集，整个文件也没有 value-label tables。其余13个候选结局的变量标签与单位标记可用于字段对应，但不提供有限特殊码说明。**没有值标签不等于证明个体字段不存在有限数值型特殊码**，更不能据此猜测 `qc1_va003` 的1/2含义；14项阻断保持不变。
- 本轮补查官方 Wave 1 [Physical Examination Questionnaire](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)（本地归档提取文本）及 Blood Guide 的全文文本层；体检问卷未出现 `qc1_va003`/空腹项目或其数字选项，Blood Guide 只说明记录空腹状态及非空腹风险，未定义字段代码。该协议文件不能替代数据字典或 released value labels。
- CHARLS 官方 2015 CodeBook 对相近的 `bl_fasting` 字段列出 `1=Yes, 2=No`；这是Wave 3字段，不能单独证明2011 `qc1_va003` 的编码跨波一致。
- 当前已查的官方 2011 文档/发行物没有给出 `qc1_va003` 的具体数值代码/特殊缺失码映射；它不是“编码已确认”，而是“官方公开材料仍未解决”。这不排除 CHARLS 账号内或其他正式更正文件存在额外说明。

## 非官方检索线索（不作为准入依据）

检索到第三方 CHARLS 变量索引把该变量标为 `1=Yes, 2=No`。该页面不是CHARLS官方发布文件；只能作为后续查找官方原始codebook/发布值标签的线索，不能据此解码个体记录、冻结模型配置或放行分析。未从原始文件读取任何受访者值以验证此映射。

### 2026-10-30 在线官方来源复核

再次直接检索并打开 CHARLS 官方 Wave 1 数据目录和 Blood Sample Users' Guide：目录目前仍列通用 Wave 1 Codebook 与 Blood Guide；Guide确认空腹状态被记录、约8%的血样来自非空腹受访者，但未列 `qc1_va003` 的变量代码表。搜索结果中出现的 `1=Yes, 2=No` 来自第三方变量索引（其页面还展示合并数据的分布），不属于官方释义；没有将其升级为准入依据，也没有读取或计算本项目个体值分布。该搜索没有解除血糖/甘油三酯的空腹路由门。在线来源：[CHARLS Wave 1 data directory](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)、[2011 Blood Sample Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)、[非官方索引（仅线索）](https://www.dbcodebook.cn/nodes/post/56/)。

## 当前决定与下一步

1. 保持105项正式拟合门关闭。
2. 已复查官方 Wave 1 Codebook PDF、Blood Guide、Physical Examination Questionnaire、Blood 发行包成员及 Stata value-label 元数据；均未给出数值代码映射。官方 Codebook 归档现已按平台 MD5 核验并确认与已存档 PDF 相同，归档中未发现该字段。只有新的、正式且字段适用的 CHARLS 释义或数据更正材料，才能解除此门；不得用 2015 字段或受访者值推断。
3. 如果当前官方公开发行没有该代码映射，后续只通过用户本人获准的 CHARLS 渠道核实并记录回复；项目不会代发联系。编码来源确认后，再冻结缺失处理、血糖/甘油三酯的主估计目标、空腹状态调整及空腹样本敏感性域；不得看关联结果后选择。
4. 其他不受空腹状态直接影响的分析物仍受共同的 PSU/方差设计准入与独立方法审查阻断，不能因此提前开跑。

## 来源

- CHARLS 官方 [Blood Sample Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)
- CHARLS 官方 [2013 CodeBook](https://charls.pku.edu.cn/en/doc/Codebook2013.pdf)（本次核实不含 `qc1_va003`）
- 官方 [PKU Open Research Data Platform 2011 baseline dataset, version 1.1](https://opendata.pku.edu.cn/dataset.xhtml?persistentId=doi%3A10.18170%2FDVN%2FIZU8OF&version=1.1)：列有受限文件 `CHARLS_codebook.rar`（文件136）。已在用户授权的服务器私有入库核对平台 MD5，并检索文档内容；未发现 `qc1_va003` 的编码释义。
- CHARLS 官方2015 CodeBook（本地官方来源归档）中的 `bl_fasting` 值标签，作为相邻波次比较；不可直接外推到2011。
- 第三方线索：[CHARLS 常规血液检测变量索引](https://www.dbcodebook.cn/nodes/post/56/)（非官方，仅检索线索）

### 2026-10-30 official physical-examination questionnaire clarification

The official CHARLS Wave 1 page links a separate `Physical examination questionnaire` (`https://charls.charlsdata.com/Public/ashelf/public/uploads/document/public_documents/application/Biomarker-manual-2011.doc`; listed on the [official Wave 1 data page](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)). I retrieved and reviewed that source. It contains item `LI875`, asking whether the respondent smoked, exercised, consumed alcohol, or ate food within 30 minutes before the **blood-pressure test** (documented options 1=Yes, 5=No, 8=Don't Know). This is a pre-measurement behavior item for blood pressure, not the blood-collection fasting-status variable `qc1_va003`; its codes must not be transferred or used as a proxy for fasting status. The questionnaire contains no `qc1_va003` mapping. The source DOC is archived at `sources_official/CHARLS_2011_Physical_Examination_Questionnaire.doc` (SHA-256: `5D269E24409F0C2BCC1910BBC483498440FDDA26069AF03BFF2C5379181C71D2`). This adds an explicit guard against conflating short-term measurement context with blood fasting status and does not unlock any models.

### Official Dataverse inventory follow-up (2026-10-30)

The CHARLS 2011 baseline Dataverse separately lists `Medical-questionnaire-2011.doc` as file 138 (platform MD5 `d1f9351dff8bdadb0d1f692ff58b75c6`), distinct from the CHARLS-page-linked `Biomarker-manual-2011.doc`/Physical Examination Questionnaire reviewed above. The Dataverse record indicates sign-in/access is required; the file itself is not present in the project's protected intake or public source bundle and has not been inspected. Do not infer that it contains the fasting mapping. If obtained through the user's already authorized CHARLS account, check its platform MD5 and archive it only in the private official-document intake before reviewing. Until then, `qc1_va003` remains unresolved and the 14 fasting-sensitive hypotheses remain blocked.

### Official Dataverse access-state recheck (2026-10-30)

The current [file 138 record](https://opendata.pku.edu.cn/file.xhtml?datasetVersionId=97&fileId=138) confirms the title, 2011 baseline association, “体检问卷” description, 747.5 KB size, and platform MD5 above. The record displays CHARLS academic-use terms, prohibits publishing raw microdata or transferring it to others, and exposes a sign-in/request-access flow; a metadata-only fetch of the file API was unavailable from this environment. The document is still absent from the protected intake and its contents remain unknown. Do not work around the access control or assume it resolves `qc1_va003`; an already-authorized user may place their obtained copy in the private intake for checksum verification. No model gate changed.
