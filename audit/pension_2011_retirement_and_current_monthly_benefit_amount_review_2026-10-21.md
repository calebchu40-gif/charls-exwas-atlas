# 2011 FM020/FM022养老金待遇金额双时间点映射审计（2026-10-21）

核对来源为 `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` 与 `sources_official/CHARLS_2011_Codebook_extracted.txt`。2011原始字段目录识别出 `fm020`、`fm021_a`、`fm021_b`、`fm022`、`fm023_a`、`fm023_b` 六个字段；本审计只使用公开问卷、Codebook和字段元数据。

- `FM020`询问“退休时”的养老金（包括补贴）金额，问卷单位为元/月；`FM021`是仅在拒答或不记得时询问的区间展开（500、1,000、2,000、3,500、5,000元），字段目录用`fm021_a/b`存最小/最大区间端点。它们归为候选概念`pension_benefit_amount_at_retirement`。
- `FM022`询问“当前”每月养老金（包括补贴），单位元；它设有低值软提示（示例小于200元/月）。`FM023`为其拒答/不记得时的相同区间展开，字段为`fm023_a/b`。这些归为不同概念`current_pension_monthly_amount`。
- 不将退休时待遇与当前待遇混成一个时间点，不把区间上下界当作精确点估计，也不重复计算展开区间字段。FM020/021/022/023位于FM011=1正常退休或2提前退休的分支；FM019选择来源题也位于该分支。其前置模块仅对符合退休/退职历史路径者开放。对当前金额的题目及分母需按原始路由处理。
- 概念映射不证明回答值、特殊码、展开缺失或存储在获批发布文件中有效。正式分析前需在获批数据版本核实区间回答与金额字段之间的逻辑关系、金额的有效范围和跳题编码；不以Codebook频数代替个体记录。目录仍是候选项，未读取个人数据、未计算关联。

实施：`scripts/build_retirement_history_exposure_crosswalk.py`，映射输出`audit/work_exposure_crosswalk_v1.csv`。下一步须检查站点JSON/字段目录中单位、时间点、分支与区间端点是否逐字段保留。

