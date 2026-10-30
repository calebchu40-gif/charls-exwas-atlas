# 2011/2015 血检字段清单与公开目录覆盖核对

日期：2026-10-24。范围仅限 CHARLS 官方公开的 2011 Blood Data User Guide、2015 Blood Data Release Note VersionID 20190620 与本项目字段 crosswalk；不读取受访者微观数据或代码本汇总频数。

## 核对结果

- 2015 Release Note 的 Table 1 列出 16 项实验室分析物：5 项 CBC（WBC、HGB、HCT、MCV、PLT）及 11 项生化/免疫检测（TG、肌酐、BUN、HDL、LDL、总胆固醇、葡萄糖、尿酸、胱抑素 C、CRP、HbA1c）。另列 `bl_fasting` 与 `bl_top_coding_tg` 两项采样/处理字段；`Blood_weight` 是横断面血检权重，不是分析物。字段目录 2015 条目与 Release Note 字段清单逐项相符。
- 2011 Blood Guide 同样覆盖 16 项分析物（CBC 5 项及血浆/全血检测 11 项）；crosswalk 按 Guide 和 Wave 1 字段目录分别保存 2011 与 2015 源码，16 个概念通过稳定概念 ID 配对，但这只表达概念候选对应，不证明方法/原始值可直接跨波比较。
- 2011 Guide 为 11 项化学分析物提供检测方法、CV 和指南报告范围；CBC 部分没有逐分析物的实验室方法/CV/范围。2015 Release Note 给出变量定义和单位，但没有这些逐项 assay 方法/CV/范围，因此 2015 字段保持空，不从 2011 继承。
- 2015 Blood Data 是独立发布文件；本地受控目录当前没有该文件。此次核对只验证公开文档与元数据映射的字段清单，不验证实际数据文件、ID 合并、值分布或覆盖率，不授权拟合关联模型。

自动回归测试以官方 Release Note 提及的字段为显式期望集合，并要求 2015 crosswalk 逐项匹配、官方文本中均可找到、且 16 个分析物仍与采样/处理字段分开。详情及测量限制见 [`blood_biomarker_definition_review_v1.md`](blood_biomarker_definition_review_v1.md)、[`blood_assay_method_metadata_2011_2015_2026-10-22.md`](blood_assay_method_metadata_2011_2015_2026-10-22.md)。

## 官方材料

- `sources_official/CHARLS_2011_Blood_User_Guide.pdf` 与提取文本，血检组成及检测方法表。
- `sources_official/CHARLS_2015_Blood_Release_Note.pdf` 与提取文本，Table 1 发布字段和单位。
- [CHARLS 2015 Wave 3 官方数据页](https://charls.pku.edu.cn/en/Data/a2015_CHARLS_Wave_3.htm)。
- [CHARLS 2015 Blood Data Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf)。

## 2026-10-30 受保护服务器入库更新

此前“本地受控目录没有 2015 血检文件”是 2026-10-24 的历史状态，不能代表后续状态。2026-10-30 在用户授权的服务器私有入库中，2015 官方 Blood ZIP 已通过项目的 SHA-1 校验及 metadata-only Stata 表头检查：表头为 13,420 行，预期的 20/20 个字段齐全。检查未读取个人记录值、ID、权重分布、合并覆盖或关联结果；原始包与 QA 均留在服务器 `private/`。

官方 Release Note 区分 13,420 名任何血样采集对象与 13,013 名横断面样本；因此 Stata 文件总行数不得直接当作横断面目标样本、模型 N 或逐对完整案例 N。Release Note 将 `Blood_weight` 定义为由个人横断面权重与血检应答概率校正构造的横断面血检权重，并说明其概率因子在第99百分位截顶。该权重与 2011 `bloodweight` 的 wave-specific 来源分别管理，不得直接跨波拼接或比较权重数值。[官方 Wave 3 数据页](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html)；[官方 2015 Blood Data Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf)。

该入库只使 2015 血检来源及字段存在性可进入下一轮逐波设计审查；不证明 2015 暴露/PSU/权重连接、目标框或模型已准入。Wave 3 仍须单独完成样本框、横断面/追踪估计目标、官方 PSU 与方差资料、字段编码、非应答权重适用性和独立方法审阅。跨波关联仍按波次分别估计；不因概念或单位相同就合并血检结果。
