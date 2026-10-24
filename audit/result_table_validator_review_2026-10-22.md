# 结果表结构与发布状态校验器（2026-10-22）

按`audit/CHARLS_ExWAS分析规约_v0.1.md`中“结果层”和“下一步可执行项”的要求，新增标准库结果表校验器`scripts/validate_exwas_result_table.py`。它只读取结果CSV和公开结果schema，不读取CHARLS个体记录，也不拟合模型。

校验器检查schema必需列、必填值、数值/概率范围、重复`analysis_id`、逐对样本流的单调关系、置信区间顺序、权重/PSU/分层字段与其验证状态是否一致；若`fit_status`不是`success`，所有效应估计和检验字段必须留空。标为`success`的 CHARLS 行必须有估计、标准误、区间、p值和模型样本量；权重选择须为核实后使用官方权重或核实后未加权，PSU须核实且实际用于方差估计，分层码须核实，或在官方未发布时明确标出近似方差方法和局限。数据发布SHA-256、产生结果的Git提交，以及逐对可估计性审查状态和受控审查编号，都是成功状态的硬性来源追溯/方法门槛。具体规则见[`result_table_design_success_gate_review_2026-10-24.md`](result_table_design_success_gate_review_2026-10-24.md)和[`estimability_release_gate_review_2026-10-24.md`](estimability_release_gate_review_2026-10-24.md)；填写内容的空白模板见[`estimability_review_record_template_v1.md`](estimability_review_record_template_v1.md)。

运行：

```powershell
python scripts/validate_exwas_result_table.py path\to\results.csv
python -m unittest discover -s tests -v
```

2026-10-24状态：校验规则由合成夹具测试；结果校验器专属测试现为14项，全项目269项测试通过。新增 near-separation 回归用例确保有限迭代系数和`NaN`不确定性不能以`inestimable`状态通过；成功行还必须由受控的逐对审查给出`reviewed_pass`和审查编号，且不可估计结果不能同时标记审查通过。分层码未发布时，机器校验要求`variance_design`用`approximate method:`与`limitation:`，或中文的`近似方法：`与`局限：`作明确标签。合成成功行仅是软件测试夹具，不是CHARLS分析结果。该检查器不能替代数据许可、统计方法复核、披露审查或字段级估计资格判断。正式模型仍被逐波样本资格、模块权重覆盖和方差设计核验门槛阻断。
