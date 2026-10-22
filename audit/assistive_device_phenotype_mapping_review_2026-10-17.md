# DB021/DB029 辅助工具使用字段复核（2026-10-17）

> **来源身份更正（2026-10-22）：**已用正式2011基线家户问卷复核DB021与DB029的题干和路由。DB021仅在DB010–DB020有任一项需要帮助时询问；无帮助需求者跳至DB029。DB022选“无人帮助”及DB026未付费的路径也跳至DB029，因此DB029与DB021不是相同适用人群或同一测量轮次。DB021为5选项，DB029为7选项，分别保留并按各自路径确定分母。正确问卷见`sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc`及相邻摘录。

## 结论

将 CHARLS 2011、2013、2015 的 DB029 多选辅助工具题列为一个 P 类候选构念 `adl_assistive_device_use`，按七个原始选项字段逐轮登记，共 26 个波次—字段映射：DB029 21条，另有2011 DB021的5个选项字段。构念表示功能受限背景下的辅助工具使用，属于功能状态标记，不是外部环境暴露，也不是26个独立结局。未将 2020 退出访谈的 `exdb029*` 误并入主访谈，也未推定 2018/2020 可比版本。

## 官方代码和答案语义

三个波次的官方问卷都将 DB029 标为“Do you use the following auxiliary? (Code all that apply)”。原始选项为：1 拐杖、2 代步器、3 手动轮椅、4 电动轮椅、5 导尿管/尿袋、6 座便辅助器、7 以上都没有。逐波代码本的 `db029s1` 至 `db029s7` 分别记录该选项；代码本频数只用于确认代码本标签，不代表本研究样本量或总体使用率。2011问卷另在IADL帮助者循环之后出现DB021（1–4为拐杖、代步器、手动/电动轮椅，5为无辅助工具）；`db021s1`–`db021s5`作为独立问卷源家族追加映射，不能假设与DB029同一路由或同一批受访者。目录保留原始选项码与选项标签，不改写成独立二元指标。

## 分析限制

2011问卷明示DB021的前置条件是DB010–DB020任一项需要帮助；没有帮助需求者跳至DB029。DB022选择无人帮助或DB026未支付帮助费用时也跳至DB029。不要把这些跳转后的空值当作未使用辅助器具；DB021与DB029分别采用各自符合路由的分母。

题目位于功能帮助问卷段，但DB021和DB029的具体适用路由不同，必须分别按逐波问卷重建分母。DB021的“无辅助工具”为选项5，DB029为选项7。未选项的空值不能自动视为“No”；正式分析前必须在获批数据中检查：每个题组的适用路径、该字段的缺失/跳题/多选存储方式、DB021选项5或DB029选项7与其他选项能否同时出现，以及个人受访/代理回答资格。当前仅将其纳入可搜索元数据候选目录，不计算使用率、不构建综合分数，也不进入关联模型。

## 来源

- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`：DB021原题、五个选项及功能困难帮助路由；DB029原题、七个选项，以及无帮助需求/无人帮助/未付费帮助等跳转上下文。
- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`、`sources_official/CHARLS_2015_Questionnaire_extracted.txt`：对应轮次 DB029 原题与选择项。
- `sources_official/CHARLS_2011_Codebook_extracted.txt`、`sources_official/CHARLS_2013_Codebook_extracted.txt`、`sources_official/CHARLS_2015_Codebook_extracted.txt`：`db029s1`–`db029s7`逐项编码标签；2011代码本也列出`db021s1`–`db021s5`。
- 映射表：`audit/assistive_device_phenotype_crosswalk_v1.csv`；总构建：`scripts/build_ep_atlas_metadata.py`。


### 2011年 DB021 与 DB029 的处理

DB021位于IADL帮助者循环后的核心访谈段，DB029位于之后的帮助成本/辅助工具题组。两组都问辅助工具，但问卷位置和路由不同，且DB021只有五个选项、DB029七个。目录将`db021s1`–`db021s5`额外保留为2011波次源字段，归入同一宽泛的辅助工具使用候选构念；分析时必须先判定估计目标和适用分母，不能合并重叠信息或把未选字段的空值转成No。
