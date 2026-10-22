# 结果表结构与发布状态校验器（2026-10-22）

按`audit/CHARLS_ExWAS分析规约_v0.1.md`中“结果层”和“下一步可执行项”的要求，新增标准库结果表校验器`scripts/validate_exwas_result_table.py`。它只读取结果CSV和公开结果schema，不读取CHARLS个体记录，也不拟合模型。

校验器检查schema必需列、必填值、数值/概率范围、重复`analysis_id`、逐对样本流的单调关系、置信区间顺序、权重/PSU/分层字段与其验证状态是否一致；若`fit_status`不是`success`，所有效应估计和检验字段必须留空。标为`success`的行必须有估计、标准误、区间、p值和模型样本量，且不能把未决或缺档的设计字段宣称为成功结果。

运行：

```powershell
python scripts/validate_exwas_result_table.py path\to\results.csv
python -m unittest discover -s tests -v
```

目前仅用合成字典做了4项规则测试（阻塞结果不含效应、阻塞结果不可带估计、样本流/概率边界、设计已验证的成功样例）。成功样例是软件测试夹具，不是CHARLS分析结果。该检查器不能替代数据许可、统计方法复核、披露审查或字段级估计资格判断。
