# 等待期基础设施（2026-10-27）

**状态：代码与合成验证完成；未读取任何 CHARLS 个体记录，未拟合任何真实模型，未发布任何结果。**

本轮在数据申请审核期（9 项申请已提交、等待 CHARLS 审核）完成三件与分析数据无关、但数据到位后立即需要的基础设施：

1. 服务器上的正式分析环境；
2. 通用 ExWAS 扫描引擎（合成数据验证）；
3. 网站结果层（热图 / 详情 / 下载）与本地 staging 夹具。

---

## 1. 服务器环境

| 项目 | 内容 |
|---|---|
| 工作根目录 | 服务器项目根目录（私有 700；具体主机与路径不入库） |
| 代码 | `code/`（`git clone` 自 GitHub，只含代码与公开文档） |
| 环境 | `env/venv`（Python 3.12.3），按 `requirements-survey-audit.txt` 精确锁定 |
| 依赖实测 | `svy 0.35.0`、`pandas 2.3.3`、`pyreadstat 1.3.1`、`numpy`、`scipy`、`polars`、`pyarrow` |
| 私有目录 | `private/`（700），内含 `derived_wave_tables/`、`qa_outputs/`、`analysis_review/`、`intake_raw/` |
| 环境变量 | `env/charls_env.sh`（600）导出 `CHARLS_EXWAS_PRIVATE_ROOT` / `CHARLS_EXWAS_DATA_DIR` / `CHARLS_EXWAS_QA_DIR` |
| 资源 | 多核、内存与磁盘均充足（具体规格不入库） |

`project_paths.py` 已支持上述环境变量，因此不需要改动任何硬编码路径。

---

## 2. 通用 ExWAS 扫描引擎

新增两个脚本：

- `scripts/exwas_engine.py`：引擎本体（注册表加载与校验、设计规格加载、逐对枚举、svy 加权 GLM、长表输出、族内 BY/Bonferroni 校正）。
- `scripts/run_exwas_scan.py`：CLI（`--synthetic` 合成模式；真实模式读受控准备表）。

### 设计要点

| 关注点 | 实现 |
|---|---|
| 变量来源 | 外部 **变量注册表 CSV**（concept_id / role / wave / variable / kind / unit / transform / valid_min / valid_max / levels / reference / family），不硬编码任何 2011 水源或燃料 |
| 设计 | 外部 **设计规格 JSON**：必须显式给出 `weight` 与 `psu`，否则拒绝启动；`strata` 缺省时明确写“无分层近似” |
| 定义域 | `weight > 0` + 年龄下限 + 暴露/结局/协变量完整，全部在**完整设计框架**上用 `where` 表达，不预先删除子总体成员 |
| 结局 | 连续结局按分析域内加权均值/SD 标准化；二分类结局返回 OR（对数尺度系数指数化） |
| 暴露 | 连续（可 `transform=z` 加权标准化）、二分类、多分类（按 `levels`/`reference` 生成哑变量，逐水平出结果） |
| 自配对 | 同一 concept_id 的 E×P 直接跳过 |
| 失败关闭 | 缺列、无正权重、定义域为空、结局方差为 0、二元结局非 0/1、引擎漏掉暴露项 —— 全部写成 `fit_status` 行，不静默丢弃 |
| 多重检验 | 按 `wave × model` 冻结族，**包含不可估计假设**，统一重算 BY-FDR 与 Bonferroni |
| 结果列 | 29 列固定长表（analysis_id、族、暴露/表型概念与变量、对照、效应尺度、估计/SE/CI/P、设计自由度、n、PSU 数、Kish 有效 n、结局均值/SD、暴露尺度、拟合状态、引擎告警、设计说明、q、Bonferroni） |
| 输出位置 | 只允许私有工作区；`--out` 不在 `CHARLS_EXWAS_PRIVATE_ROOT` 下直接报错 |

### 合成验证

`tests/test_exwas_engine.py`：14 项测试，全部通过。

- 注册表：缺字段、非法角色、分类参照不在 levels、正常往返；
- 设计：缺 weight/psu、帧缺列；
- 效应回收：连续暴露真值 0.60 → 估计 0.60±0.10；二分类暴露真值 1.20 → 1.20±0.18；二分类结局真值 OR≈1.65 → 落在 1.2–2.3；
- 分类暴露：3 水平生成 2 行；
- 族：K 与实际行数一致、q/Bonferroni 齐全、自身不配对；
- 失败关闭：定义域为空全部标记 `no_eligible_records` 且不输出估计；z 变换记录 `weighted_z`。

同一套测试与同一合成扫描已在服务器复跑通过：

```
14 tests OK（服务器 env/venv）  →  16 行合成结果，两个模型族各 8 行
输出：private/qa_outputs/synthetic_scan_v1.csv
```

> 合成结果只验证软件行为，不是 CHARLS 分析结果。

---

## 3. 网站结果层

在 `site-prototype/dist/index.html` 与 `app.js` 中新增**暴露 × 表型热图**，与既有结果表共用同一份 `association_results_v1.json`：

- 每个 `(wave, model)` 一张矩阵；行=表型概念，列=暴露概念×对照（分类暴露自动展开为多列）；
- 三种着色：效应量（OR 按 log 尺度）、−log10 P、BY q 值；颜色深浅表示强度；
- 点格子 → 详情面板（暴露/表型/波次/模型/对照/效应尺度/估计与 SE/95%CI/P/q/Bonferroni/n/方差方法/可比性/拟合与披露状态/目标人群）；
- “下载当前筛选 CSV”（客户端生成，只含当前已审查的聚合行）；
- 不引入任何新的数据来源：行仍只来自经披露审查的 `association_results_v1.json`；空家族时不渲染热图。

### 本地 staging 夹具（不公开、不进仓库）

- 生成器：`%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\staging\build_staging_payload.py`
- 数据源：私有 pilot 的 2011 M1 家族（105 条 = 7 个燃料/水源对照 × 15 项血液表型）
- 流程：映射到公开行契约 → **用生产校验器** `validate_public_site_payload` 校验 → 复制一份 dist 到私有 staging 目录并写入 payload
- 断言结果：105 行 / 1 个完整族 / 校验 0 错误；热图渲染 15 行 × 7 列共 105 个格子
- 截图：`%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\staging\shot.png`

**staging 夹具中的“披露批准”是伪造的，仅用于界面开发；不得发布。**

---

## 4. 下一步（数据到位后）

1. 用真实发行版字段填 `audit/templates/exwas_variable_registry.template.csv` 与 `exwas_design.template.json`，冻结后才允许扫描；
2. 引擎输出 → `EXWAS_result_schema_v3.csv` 映射器（补齐 source identity / stratum status / estimability review 等字段）；
3. 结果表校验 → 披露审查 → `build_public_association_release.py --publish` → 热图自动显示真实结果；
4. 服务器上跑真实扫描前，仍需通过 Wave 1 来源/样本框/权重/PSU 方差四道门。
