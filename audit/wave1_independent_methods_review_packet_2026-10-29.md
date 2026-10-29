# Wave 1 设计与105项试点：独立方法审阅材料

**状态：待独立调查抽样/生物统计审阅；未获模型运行或结果发布批准。**

本材料汇总当前可核实的方法信息及尚需决定的事项，供具备复杂抽样调查经验的审阅人评估。材料不含 CHARLS 参与者记录、样本计数、逐对结果或本地哈希。

## 当前可核实的证据

- 用户确认 Wave 1 All Data、PSU、Weight、Blood 来自其获准 CHARLS 账号，对应官方数据项 123、117、118、201。服务器只读来源检查和准备表 provenance/hash 检查通过；该检查核对来源文件清单、Stata 表头和文件哈希，不读取受访者答案。
- 受保护发行包中15个 All Data 模块的字段名已经逐一检查。`sub_commuID` 只见于社区模块；其余14个模块均没有此字段。社区模块同时含 `communityID`。
- 独立 PSU 文件的表头提供 `communityID`、省/市、NBS城乡、地区类型和版本字段；未见子 PSU 映射键、显式方差层或复制权重。社区字段存在不等于能确定个人所在子 PSU。
- Weight 文件含家庭/个人键及多类权重；Blood 文件含 `bloodweight`、空腹标记和15个常规血液分析物字段，另有 cystatin C。官方手册支持常规血液结局优先评估血检专用权重；cystatin C 因有年龄分层随机检测而暂不并入普通血检分析族。
- 受保护只读 `require_verified_wave1_frame` 检查通过；`require_wave1_analysis_readiness` 因没有绑定当前来源和方案的审阅记录而阻断模型执行。
- 两个 Wave 1 试点入口都在读取分析输入前调用上述来源与分析就绪门；当前没有审核记录时会 fail closed，不会进入拟合步骤。

## 105项方案的当前定义

- 一个固定的105系数家族：运行水源 Yes vs No 15项，加上烹饪燃料6个非电力类别各自 vs 电力的90项；配对15个非 cystatin C 血液分析物。燃料类别保留官方分类，不合并成“清洁/污染”组。
- M1 为主探索模型：暴露 + 中心化年龄 + 年龄平方 + 性别；M2 加 NBS 城乡及分组教育，作为敏感性模型。M0 仅作描述。M1与M2分别在各自完整105项中调整 BY-FDR 和 Bonferroni；不可估计项仍保留。该扩展在先前水源试点后提出，须标记为探索性，不能称为预注册确认性发现。
- 分析目标暂定为基线年龄≥45域，完整血检目标框中建立设计后再用 domain 表达年龄资格；配偶可低于45岁。年龄协变量目前来自 Harmonized CHARLS D-derived candidate，不是 Wave 1 官方原始年龄字段，需审阅其构造和目标日期。
- 当前脚本使用 `communityID` 为 PSU、无分层、有放回 Taylor 线性化近似；此为历史探索实现，不是完整 CHARLS 方差设计，也没有本次运行准入。

## 新发现的测量条件问题：空腹状态

Wave 1 官方 Blood User Guide 说明采血前要求过夜空腹，但未空腹者仍采血并记录状态；指南指出非空腹样本约占少数，且非空腹血糖可能高于空腹测量。官方 Blood 文件含 `qc1_va003` 空腹字段。该字段在 Stata 文件中没有 value-label set；所取得的 Wave 1 Codebook 和 Blood User Guide 说明了字段用途/测量背景，但没有给出该变量的具体数值编码。官方2015 CodeBook的相近 `bl_fasting` 字段为1=Yes、2=No，但不据此推断Wave 1编码；第三方变量索引提示同一映射，也不据此解码或放行。现有105项扩展脚本没有将空腹状态放入模型或相应的结局 domain；项目变量语义记录则要求血糖、甘油三酯保留空腹信息。具体复核记录见 [`wave1_fasting_code_source_review_2026-10-29.md`](wave1_fasting_code_source_review_2026-10-29.md)。

因此，在任何真实模型运行前，先以发布文件文档核实 `qc1_va003` 数值编码，再明确并预先固定血糖及甘油三酯的处理：主估计是否对空腹状态调整、是否另做空腹样本敏感性分析，以及缺失/非空腹标记如何处理。不可查看结果后再决定筛选方式，也不得按未经核实的编码划分 fasting/not fasting。此决定也会影响结局标准化参考域和每一项的估计目标。

## 请审阅人决定的问题

1. 官方抽样说明提及30个大型社区以子社区作为 PSU；当个人/家庭文件没有 `sub_commuID`，PSU 文件也没有该字段时，是否有可接受且可追溯的方式将最终 PSU 映射到受访者？如果没有，现有公开数据可以支持哪种推断范围？
2. 若仅能使用 `communityID`，以父社区为 cluster、无显式 strata 的 with-replacement Taylor 近似，是否可用于清楚标记的内部探索估计？其标准误、自由度和代表性限制应怎样表述？审阅人可要求停止模型拟合或改为仅作描述。
3. 血检专用 `bloodweight` 与年龄≥45 domain 的目标总体解释是否成立？如何界定包括较年轻配偶的完整设计框和45+目标域？
4. 对血糖/甘油三酯，官方发布文档中应以何种代码解释 `qc1_va003`？在此基础上建议采用何种预先声明的空腹状态调整和敏感性方案？
5. 105项主族的具体有效值、量纲/变换、协变量、可估性标准、单 PSU/domain-singleton 处理、多重校正与结果复核是否足够完整？

## 当前决策

在上述问题获得独立方法审阅并写入受保护审核记录、冻结的105项配置绑定到当前来源与代码之前，不拟合真实关联模型。近似估计若被接受，也必须明确标成近似设计，不能表述为完整复现 CHARLS 分层多阶段设计或无条件全国代表性结果。没有任何结果可进入公开网站。

## 官方来源

- [CHARLS 官方抽样设计说明](https://charls.pku.edu.cn/en/About/Sample.htm)
- [CHARLS 2011–2012 National Baseline Users' Guide](https://charls.pku.edu.cn/wenjian/jixiandiaochashujuyonghushiyongshouce2013-04-07.pdf)
- [CHARLS Blood Sample Users' Guide](https://charls.pku.edu.cn/wenjian/xuejianshujuyonghushiyongshouce.pdf)，尤其是过夜空腹、非空腹样本仍采集以及血糖差异的说明。
- 项目内的 [试点方案与门禁](pilot_2011_water_biomarker_plan_and_gates_2026-10-26.md) 与 [生物标志物有效值/尺度门禁](wave1_biomarker_outcome_validity_and_scale_gate_2026-10-27.md)。
