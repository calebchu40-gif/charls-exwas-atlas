# CHARLS已到位文件的批量入库检查入口（2026-10-25）

为减少分别查找和启动 Wave 2 权重、Wave 3 Blood Data 检查脚本的操作，新增 `scripts/run_available_charls_intake_gates.py`。它只在受控目录检查固定文件名：`incoming_2013_weights/Weights.dta`，以及 `incoming_2015_blood/Blood_Data_2015_download` 和 `Blood_Data_2015.dta`。若仅有2015血检下载项或仅有DTA，会报告输入不完整并跳过；只有完整文件组到位才调用现有官方SHA1和Stata表头闸门。

从项目根目录运行：

```powershell
python scripts/run_available_charls_intake_gates.py
```

脚本不下载或解压文件、不读取个人答案或ID、不合并记录、不计算频数或样本量。完整摘要写入 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\qa_outputs\charls_available_intake_gates.json`，不写入项目树。所有输入和输出继续经过 `require_private_path` 检查，拒绝OneDrive等同步目录。任何输入文件若存在但哈希/表头不通过，会中止并报告错误，而不会接受替代文件。

新增三个合成单元测试覆盖缺文件、血检输入不完整和云同步路径拒绝。其余检查由各波既有脚本负责：[`wave2_weights_metadata_intake_gate_2026-10-25.md`](wave2_weights_metadata_intake_gate_2026-10-25.md)、[`blood_2015_intake_gate_2026-10-25.md`](blood_2015_intake_gate_2026-10-25.md)。
