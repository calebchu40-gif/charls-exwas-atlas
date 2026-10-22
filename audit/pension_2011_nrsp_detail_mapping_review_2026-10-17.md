# 2011年新农保缴费与待遇时间字段复核

依据 CHARLS 2011 基线问卷 FN073–FN078 与 CodeBook，新增9条源字段映射，其中仅增加1个新候选概念；其余字段复用已有概念，避免同义或同单位构念重复计数。

| Concept ID | 字段 | 含义 | 单位/编码及边界 |
|---|---|---|---|
| `pension_new_rural_participation_start_date_components` | `fn073_1`, `fn073_2` | 首次加入新农保年月 | 2008–2011年和月份分开；月份0表示不记得，不是1月 |
| `pension_annual_contribution_amount`（已有） | `fn074_1`, `fn074_3` | 年度缴费额、一次性缴费方案下的年等值金额 | 元/年；不能与一次性金额相加或混单位 |
| `pension_lump_sum_contribution_amount`（已有） | `fn074_2` | 一次性缴费总额 | 元；与年缴费额分开 |
| `pension_required_contribution_years`（已有） | `fn075` | 领取待遇所需缴费年数 | 年；不等于已经缴费年数或参保年限 |
| `pension_contribution_payer_new_rural_social_program_or_current`（已有） | `fn076` | 新农保缴费承担者 | 1=本人；2=子女；3=其他家庭成员/亲属；4=其他 |
| `pension_benefit_start_date_components`（已有） | `fn078_1`, `fn078_2` | 新农保开始领取待遇年月 | 仅`fn077=Yes`后询问；年份与月份分列，月份0表示不记得 |

FN074的缴费方式题已在现有`pension_contribution_method`概念中；FN077开始领取待遇状态也已有对应候选概念；FN079每月待遇金额已连接到`pension_monthly_benefit_amount`。此次不再重复登记这三个父项/状态字段。所有字段都来自2011新农保条件路由，金额、日期组件和付款来源必须保留不同单位与分母。

## 构建与限制

- 构建脚本：`scripts/build_2011_nrsp_detail_crosswalk.py`，已进入全量目录流程。
- 映射表：`audit/pension_2011_nrsp_detail_crosswalk_v1.csv`；概念汇总：`audit/pension_2011_nrsp_detail_summary_v1.csv`。
- 依据：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`、`sources_official/CHARLS_2011_Codebook_extracted.txt`。
- 未复制代码本频数、未读取受访者记录、未运行关联模型。
- 新农保题组具有计划和波次特定分母。正式分析前须按数据发布版核实值域、特殊缺失、抽样设计和估计目标。
