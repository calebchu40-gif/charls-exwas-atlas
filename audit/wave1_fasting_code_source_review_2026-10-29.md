# Wave 1 空腹变量编码来源复核

**日期：2026-10-29**  
**状态：官方来源说明变量存在，但本次检索未找到官方数值代码映射；分析门继续关闭。**

## 复核问题

Blood 数据中的 `qc1_va003` 表示采血时是否空腹。拟定的105项试点包含血糖和甘油三酯；在冻结其分析domain、调整或敏感性方案前，需要把数值代码对应到“是/否”，并确认缺失码如何处理。

## 官方来源证据

- CHARLS《Blood Sample Users' Guide》说明受访者被要求过夜空腹；即使未空腹仍采血，并在数据中记录状态。指南同时指出非空腹样本的血糖可能偏高。见官方指南第8页（PDF第9页）及第16页（PDF第17页）。
- 官方 Wave 1 Blood 文件表头含 `qc1_va003`，但字段未带 value-label set。
- CHARLS 官方 2013 CodeBook 不含 `qc1_va003`；其内容是2013随访问卷模块，不能替代2011血液数据值标签。
- 复查 CHARLS 官方 Wave 1 下载页后，页面列出的相关文档是通用 Wave 1 Codebook 与 Blood Data Users' Guide，没有另列 2011 Blood 专用 Codebook 或 Blood Release Note。官方 Blood ZIP 归档仅包含 Stata 数据文件，没有随包数据字典/README。见[官方 Wave 1 数据文档清单](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html)。
- 2026-10-29 再次打开 CHARLS 当前官方 Wave 1 页面核对文档清单：仍列通用 Codebook 与 Blood data users' guide，没有新增 `qc1_va003` 专用代码本；该页面将 Blood 数据发布日期列为 2014-04-29。此为在线文档清单核对，不构成字段代码的数值映射。
- **官方归档核验（2026-10-30）：**在暂存的官方资料中找到 `2011_120_CHARLS_codebook.rar`，压缩包 MD5 为 `293eb9789ee559fe0d7099086a2aaf40`，与北京大学开放研究数据平台 CHARLS 2011 baseline dataset v1.1 的 `CHARLS_codebook.rar` 条目一致。归档成员清单只有 `CHARLS_codebook.pdf`；其 SHA-256 与项目已存档的官方 Wave 1 Codebook PDF 相同。对该官方 Codebook 可检索文本定向查找 `qc1_va003`、`va003`、`fasting` 和“空腹”，未找到对应字段或代码标签。因此，归档取得补全了来源身份链，但没有提供 `qc1_va003` 的数值映射，空腹编码门仍未通过。归档和文档只保存在本机受控参考目录，未复制到 GitHub、OneDrive、服务器或网站。
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
- 官方 [PKU Open Research Data Platform 2011 baseline dataset, version 1.1](https://opendata.pku.edu.cn/dataset.xhtml?persistentId=doi%3A10.18170%2FDVN%2FIZU8OF&version=1.1)：列有 `CHARLS_codebook.rar`，但须经账号授权获取；文件内容目前未审阅。
- CHARLS 官方2015 CodeBook（本地官方来源归档）中的 `bl_fasting` 值标签，作为相邻波次比较；不可直接外推到2011。
- 第三方线索：[CHARLS 常规血液检测变量索引](https://www.dbcodebook.cn/nodes/post/56/)（非官方，仅检索线索）

