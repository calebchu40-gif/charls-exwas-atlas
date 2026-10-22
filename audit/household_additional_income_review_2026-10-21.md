# 2020家户农业光伏与其他资产租赁收入字段审计（2026-10-21）

## 新增构念

依据2020年Household Income模块问卷和代码本，新增3个单波家户层候选构念：

| 字段 | 指标 | 单位/语义 | 路由与限制 |
|---|---|---|---|
| `ge011` | 家户光伏发电收入 | 过去一年人民币；题干明确包括自家使用的电力价值与售电收入 | 仅2020；不能解释为现金收入或并入一般自雇净收入 |
| `ge014` | 非住房、非土地其他资产租赁收入状态 | 官方代码标签：1=Yes/rental income，2=Not applicable，997=Don't know，999=Refuse | 示例包括树木、固定资本、耐用品、牲畜；代码2不是通用No，不把结构未问/缺失当No |
| `ge014_1` | 非住房、非土地其他资产租赁收入金额 | 人民币；在租赁收入条件路由内 | 该金额题干没有明确说明参考期间，不自行标注年度，也不对未进入路由者填0 |

它们均为家户层指标，由财务回答者提供，不等同于个人收入。适用分母、特殊值及字段关系需在获授权的2020数据字典和数据中核验。

## 证据位置

- `sources_official/CHARLS_2020_Questionnaire_English_extracted.txt`：GE009–GE011（光伏是否、安装年份、过去一年收入，含自用和售电价值）；GE014–GE014_1（其他资产租赁收入类别与金额）。
- `sources_official/CHARLS_2020_Codebook_extracted.txt`：GE011、GE014、GE014_1变量标签和响应类型；代码本频数不复制到目录。
- `audit/raw_variable_catalog_v1.csv`：五项中3个目标字段均存在于2020 Household_Income模块。

新增映射由`scripts/build_household_additional_income_crosswalk.py`生成并纳入`build_ep_atlas_metadata.py`完整入口及主概念crosswalk。未读取个人级数据，未估计家户收入关联。
