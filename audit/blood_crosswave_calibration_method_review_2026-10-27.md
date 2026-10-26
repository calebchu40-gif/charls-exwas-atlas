# CHARLS 2011/2015血液指标跨波校准方法复核（2026-10-27）

## 结论

2011与2015有同概念、部分同单位的血液指标，但不足以直接比较变化或跨波合并。已发表研究中至少存在两种不同的“校准”含义，不能混为一谈：

1. **采样/检测协议桥接或实验室校准：** 用桥接样本、跨实验室复测、明确转换函数或可追溯的官方处理变量，估计测定过程差异。
2. **把波次分布强制对齐：** 假设总体层面没有真实变化，调整某一波的值使其边际分布匹配基线。这会按构造消除总体均值/分布变化，不等同于由实验室对照样本识别出的测定偏差校正。

## 已核对的证据

- CHARLS 2015血检设计论文记载2011和2015均有静脉血检测，并说明Wave 3改进采血、运输及温控流程。论文提到TC、HDL-C、hsCRP与HbA1c正在与HRS家族研究做跨实验室比较和流程影响调整；这不证明CHARLS公开原始字段已包含完成校准后的变量。来源：Chen et al., *American Journal of Epidemiology* 2019，[PMCID PMC6825825](https://pmc.ncbi.nlm.nih.gov/articles/PMC6825825/)；CHARLS [2015 Blood Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf)。
- Wu et al. 2024在HRS/CHARLS心代谢风险与认知研究中，将CHARLS 2015的CRP、TC、HDL-C和HbA1c调整至2011基线分布；作者明确说明此操作使总体层面无2011–2015变化，但个体层面仍可变化。研究还将CHARLS样本限制为50岁及以上以匹配HRS。来源：[The Association Between Cardiometabolic Risk and Cognitive Function Among Older Americans and Chinese](https://doi.org/10.1093/gerona/glae116), *The Journals of Gerontology: Series A* 2024;79(7):glae116，样本定义及“Individual cardiometabolic biomarkers”方法段。

## 对本项目的分析决定

- 不能因为其他文章使用过分布匹配，就把它默认成ExWAS所有血液指标的校准方法；尤其不能未经验证地用于横断面暴露—表型回归。
- 对2011/2015同名血液分析物，先保留波次特异估计和原始测量尺度；跨波关联汇总须等待实验室桥接/校准证据、变量版本、目标样本和波次权重设计审定。
- 若未来问题明确为个体内纵向变化，任何基线分布对齐只能作为带有明确识别假设的敏感性分析候选；需核对转换公式、目标人群、完整配对样本选择、权重及其对暴露—结局协方差的影响，并与未对齐分析并列。不能称为“官方校准值”，也不能替代波次特异结果。
- 当前缺少官方Wave 1 All Data/PSU/Weight/Blood和2015独立血检入库；没有检查CHARLS个体测量，没有运行校准、拟合关联或生成结果。本文件是文献方法复核，不批准模型。

## 复核边界

2024主文说明了分布对齐的目标和指标，但本次未能获取其DOCX补充材料，具体转换公式尚未核验，不能声称已复现算法。未来借鉴前必须取得并逐项核对补充材料与代码。字段级实验室限制另见 `blood_biomarker_definition_review_v1.md` 和 `blood_biomarker_crosswalk_v1.csv`。
