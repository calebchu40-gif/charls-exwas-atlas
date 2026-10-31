# 引擎与 K=150/K=90 执行器：设计语义一致性（2026-10-31）

项目里有两条执行路径：

1. **通用引擎** `scripts/exwas_engine.py`（本轮工作引入）：注册表驱动、逐对扫描、可跨波复用；
2. **专用执行器** `scripts/run_2011_household_environment_scaleup.py`：K=150 家庭环境主块 + K=90 供暖子域。

两者必须对"什么算一个可报告的设计"给出同一答案，否则同一批数据会产出两种口径。本文件记录对齐结果与仍有意的差异。

本轮未读取参与者数据、未拟合模型。

---

## 1. 字段对照

| 执行器冻结配置（`design.*`） | 通用引擎 `DesignSpec` | 状态 |
|---|---|---|
| `weight_field` | `weight` | ✅ 一致，均必填 |
| `psu_field` | `psu` | ✅ 一致，均必填 |
| `stratum_fields: []` | `strata: str \| None` | ✅ 单列实现；执行器允许多列，引擎当前只支持单列（见 §3 差距 G1） |
| `replicate_weight_fields: []` | 无对应字段 | ✅ **有意的差异**：引擎永不接受复制权重，只能 Taylor；执行器要求显式写空列表 |
| `with_replacement` | 固定 `wr=True` | ✅ 一致（引擎不提供无放回选项） |
| `variance_method` | 由 `note()` 生成 | ✅ 引擎在无 strata 时自动写明"unstratified with-replacement Taylor approximation" |
| `variance_limitations` | 新增 `variance_limitations` 字段 | ✅ 本轮对齐；无 strata 时**强制**在结果说明中出现 `limitation:` 标签 |
| `singleton_psu_method`、`domain_singleton_method`、`on_domain_singletons` | 无对应字段 | ⚠️ 仅执行器承担（见 §3 差距 G2） |

## 2. 引擎本轮新增的硬约束

- `DesignSpec.note()`：当未提供 `strata` 时，说明文本必须包含
  `unstratified with-replacement Taylor approximation`、`not full design variance` 与 `limitation:`；
  未自定义限制文本时使用固定默认句（官方未发布方差分层/复制权重、县内系统 PPS 隐式分层未复现）。
- 提供了 `strata` 时，说明文本改为 `official stratum <列名>; Taylor linearisation`，不再挂 `limitation:`。
- `variance_limitations` 可从设计 JSON 读入（`load_design`），因此**每个波次可以写自己的限制措辞**。
- 引擎仍拒绝任何复制权重路径；若将来需要，必须新增显式字段并同时更新本备忘，不得隐式接入。

## 3. 仍然存在的差距（提交方法审阅）

| 编号 | 差距 | 影响 | 处理建议 |
|---|---|---|---|
| G1 | 执行器允许 `stratum_fields` 为多列，引擎只支持单列 | 若将来采用多列分层，通用引擎无法表达 | 在冻结前决定：要么执行器同样限制为单列，要么给引擎扩展多列（改动小，但需重跑全部测试） |
| G2 | 引擎未暴露 singleton 处理策略（整样本 singleton PSU、domain singleton） | 两种执行路径可能用不同的默认值，导致 SE 不可比 | 由执行器冻结配置显式声明；通用引擎的真实扫描必须**复用同一策略**，或在结果中记录"svy 默认"并声明为限制 |
| G3 | 执行器的 outcome/exposure 字段映射（`i016`–`i022`、15 项结局变换）在引擎侧由注册表承担 | 两套配置可能漂移 | 注册表从同一冻结文件生成；执行器与引擎共用同一份 `wave1_outcome_rules_v1.json` |
| G4 | 执行器绑定 plan 哈希、source manifest、prepared 表哈希；引擎只绑定设计 JSON | 引擎路径的来源可追溯性弱于执行器 | 扫描前由 `engine_to_schema_v3` 的 provenance 承担来源绑定（已实现，见该模块） |

## 4. 测试覆盖

`tests/test_engine_executor_consistency.py`（8 项）：

- 执行器模板仍含 weight/PSU/strata/replicate/WR/variance_method/variance_limitations 七个键；
- 模板默认 `status=not_frozen`、`replicate_weight_fields=[]`、`with_replacement=null`；
- 执行器要求的每个设计字段在引擎中有对应物；复制权重在引擎中**故意不存在**；
- 无分层说明必须含 `limitation:`；自定义限制文本原样出现；有分层时点名层列且不挂 `limitation:`；
- 设计 JSON 可往返 `variance_limitations`；
- 扫描产出的每一行 `design_note` 都带 `limitation:`。

## 5. 边界

- 一致 ≠ 已批准。方差方案仍待独立方法审阅；
- 本文件只做静态语义核对，不含任何数据或估计；
- 正式关联模型数仍为 0。
