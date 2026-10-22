# 2018 房屋产权成员关系槽位值标签审查

审查日期：2026-10-22。共核对 215 个 `HA000_W4` 房屋/成员关系字段的 Codebook 标签区块；不复制或使用任何频数和百分比。

Codebook 对这些字段使用 `Do Not Own` 和 `Own` 两种回答标签。但生成的频数型 Codebook 摘录对部分字段只显示其出现过的标签，无法据此确认缺失类别的完整码本。逐字段审查后，15 个字段同时列出 `0=Do Not Own` 与 `1=Own`；其余 200 个仅暴露部分回答码，因此主目录不补猜缺失类别，也不把已出现标签当作完整标签集。对 200 个字段，目录记录“response-code set incomplete; do not infer omitted categories”并保留官方 Codebook 来源。

这类字段是“某家庭成员是否拥有该房屋产权”的离散关系项，按房屋、成员和路由重复；即使值标签齐全，也不能把槽位当作互相独立的家庭暴露。公开的字段目录只提供代码含义与审计状态，不公开频数。完整回答码表需要 CHARLS 官方提供不依赖观察频数的字段格式/值标签字典，或在获批原始发行文件中对格式元数据进行核验。

审查脚本为 `scripts/build_housing_owner_relation_labels.py`，从官方 Codebook 文本中仅提取 `0/1` 对应文本，明确跳过频数/百分比列；完整量逐字段匹配住房映射。此检查仅改善标签覆盖状态，不授予分析资格，也未使用个体记录。

## 官方发布材料与文件校验

CHARLS Wave 4 User's Guide 将 Codebook 定位为发布数据集变量的概要信息，并说明 Wave 4 数据文件为 Stata 14 格式。官方 2018 页面同时列出 User's Guide、Household Questionnaire、Codebook 与数据文件下载入口。项目本地三份 PDF 与官网页面展示的 SHA-1 完全匹配：Codebook `8F8017CEC22518E0251CF15EE3A700C9142A7A14`、User's Guide `18D92656677464D10096377E1864DB59BD4DAA51`、Household Questionnaire `6C547DDE4240EAE5F7FFFB22556D26109186B974`。因此本次“完整标签集不足”是当前 Codebook 摘录粒度的限制，不是本地文件与官网版本不一致。官网下载入口需要用户账户；未尝试匿名取得受控微观数据。

官方来源：[2018 Wave 4 数据与文档页面](https://charls.pku.edu.cn/en/Data/a2018_CHARLS_Wave_4.htm)；[Wave 4 User's Guide PDF](https://charls.pku.edu.cn/en/data/User2018.pdf)。
