# 通用 ExWAS CLI 真实数据准入加固（2026-10-28）

## 发现

静态审阅 `scripts/run_exwas_scan.py` 时发现：CLI 对输出路径执行了私有目录检查，也要求显式权重和 PSU，但真实模式此前没有调用 Wave 1 官方来源身份、准备表哈希及分析就绪审核。也就是说，使用者即使绕开 Wave 1 专用执行器，仍可能仅凭一个任意 registry/design 文件运行通用引擎。这与项目的“来源/设计门未过不得拟合”总规则不一致。

## 修正

- 真实模式现只接受 Wave 1，并且必须指定注册的 `--analysis-plan`。
- 读取完整帧前，先调用 `require_verified_wave1_frame` 和 `require_wave1_analysis_readiness`；缺少官方四源文件、匹配的准备表来源哈希或任一所需方法门时停止。
- 新增受保护的 `analysis_review/generic_exwas_scan_authorization.json` 额外审核记录，绑定波次、分析计划、来源 manifest、准备表 SHA-256、registry SHA-256、design SHA-256、审阅人/日期，并明确无公开发布批准。registry/design 任一字节改变后原授权即失效。
- 新增空白模板 `templates/generic_exwas_scan_authorization.template.json`。模板的 `not_approved` 状态不能通过门禁；不得将模板复制后直接当作批准。

该记录与既有计划审核是两个独立检查：前者审核此具体 registry/design 与帧的精确绑定；后者核验源文件、样本框、年龄域、权重、PSU/方差及冻结分析计划。通用工具暂不放行 Wave 2–5，直到各波有自己的来源、设计和计划准入函数；不能将 Wave 1 门禁移用到其他波次。

## 状态与验证

本轮只做代码静态编译和 whitespace diff 检查；当前工作环境未安装 `polars`，因此 CLI `--help` 无法启动。没有运行测试套件，没有读取 CHARLS 个体记录或拟合模型。受保护入库仍缺 Wave 1 All Data/PSU/Weight/Blood，故正式关联模型仍为 0。完成后需在锁定分析环境运行仓库验证工作流，并核查该执行器的合成路径仍可用。
