# Wave 1 空腹变量编码来源复核

**日期：2026-10-29**  
**状态：官方来源说明变量存在，但本次检索未找到官方数值代码映射；分析门继续关闭。**

## 复核问题

Blood 数据中的 `qc1_va003` 表示采血时是否空腹。拟定的105项试点包含血糖和甘油三酯；在冻结其分析domain、调整或敏感性方案前，需要把数值代码对应到“是/否”，并确认缺失码如何处理。

## 官方来源证据

- CHARLS《Blood Sample Users' Guide》说明受访者被要求过夜空腹；即使未空腹仍采血，并在数据中记录状态。指南同时指出非空腹样本的血糖可能偏高。见官方指南第8页（PDF第9页）及第16页（PDF第17页）。
- 官方 Wave 1 Blood 文件表头含 `qc1_va003`，但字段未带 value-label set。
- CHARLS 官方 2013 CodeBook 不含 `qc1_va003`；其内容是2013随访问卷模块，不能替代2011血液数据值标签。
- CHARLS 官方 2015 CodeBook 对相近的 `bl_fasting` 字段列出 `1=Yes, 2=No`；这是Wave 3字段，不能单独证明2011 `qc1_va003` 的编码跨波一致。
- 截至本次复核，没有找到CHARLS官方材料给出 `qc1_va003` 的具体数值代码/缺失码映射。

## 非官方检索线索（不作为准入依据）

检索到第三方 CHARLS 变量索引把该变量标为 `1=Yes, 2=No`。该页面不是CHARLS官方发布文件；只能作为后续查找官方原始codebook/发布值标签的线索，不能据此解码个体记录、冻结模型配置或放行分析。未从原始文件读取任何受访者值以验证此映射。

## 当前决定与下一步

1. 保持105项正式拟合门关闭。
2. 继续查找CHARLS官方 Wave 1 Blood codebook、数据字典或随发布包提供的值标签文件；若在本地官方发行包中补到，只读取文档/字段元数据并记录版本与来源。
3. 编码来源确认后，再冻结缺失处理、血糖/甘油三酯的主估计目标、空腹状态调整及空腹样本敏感性域；不得看关联结果后选择。
4. 其他不受空腹状态直接影响的分析物仍受共同的 PSU/方差设计准入与独立方法审查阻断，不能因此提前开跑。

## 来源

- CHARLS 官方 [Blood Sample Users' Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)
- CHARLS 官方 [2013 CodeBook](https://charls.pku.edu.cn/en/doc/Codebook2013.pdf)（本次核实不含 `qc1_va003`）
- CHARLS 官方2015 CodeBook（本地官方来源归档）中的 `bl_fasting` 值标签，作为相邻波次比较；不可直接外推到2011。
- 第三方线索：[CHARLS 常规血液检测变量索引](https://www.dbcodebook.cn/nodes/post/56/)（非官方，仅检索线索）

