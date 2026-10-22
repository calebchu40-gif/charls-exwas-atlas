# 2011 FM019 养老金来源多选槽位审计（2026-10-21）

## 官方来源与题目范围

依据 `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` 的2011基线家庭问卷和 `sources_official/CHARLS_2011_Codebook_extracted.txt`。FM019题干为“Are you receiving pension benefits from the government, a previous work unit, or a social insurance agency? (Choose all that apply)”，并列商业保险公司、其他；FM011=1（正常退休）或2（提前退休）时询问FM014–FM024；FM019因此还限于该退休类型分支。需在FM010当前领取养老金路径中，FM010=No跳至FM042。它不是全样本参保情况。

| 字段 | 问卷选项槽含义 |
|---|---|
| `fm019s1` | 政府 |
| `fm019s2` | 原工作单位 |
| `fm019s3` | 社会保险机构 |
| `fm019s4` | 商业保险公司 |
| `fm019s5` | 其他 |

## 映射与限制

将五个槽位接入既有概念 `retirement_pension_benefit_source`，只为字段检索和问卷菜单追溯；不把五个字段计为五种养老金暴露。Codebook抽取结果呈现各槽位选项索引及汇总频数，不能证明获批发布文件中逐人字段的存储约定、未选项的编码、空值意义或可分析分母。字段目录的“值标签”因此只记录“问卷选项槽含义”，明确它不是回答值标签。所有五项均锁定 `DO NOT ANALYZE`，直至在官方获批数据版本及数据字典中核实存储。

分析分母还须满足全部题目路由：退休类型FM011=1或2，且经FM010确认正在领取养老金；不得将结构性跳题当作未领取、否或零。Codebook频数不得用作数据替代或估计结果。

## 实施位置

- 映射生成：`scripts/build_retirement_history_exposure_crosswalk.py`
- 选项槽说明：`scripts/build_work_exposure_value_labels.py`
- 目录锁定：`scripts/build_charls_atlas_catalog.py`
- 主映射表：`audit/work_exposure_crosswalk_v1.csv`

没有读取微观记录，没有计算任何关联或比例。
