# 2011年养老金参保门槛与多选类型映射复核

依据 CHARLS 2011 基线全国问卷 FN038–FN039、FN071–FN072、FN077–FN079 和 2011 CodeBook，新增三个待分析资格审查的 E 候选概念及9条源字段映射；另将月待遇金额`fn079`接入已有概念，不重复计数。既有FN072九项映射只补充路由说明：

| 概念 | 源字段 | 题目含义 | 编码解释 |
|---|---|---|---|
| `pension_nonbasic_program_participation_any` | `fn038` | 是否参加至少一种列明的养老金项目 | 1=是，2=否 |
| `pension_participation_type_multi_select` | `fn039s1`–`fn039s6` | 企业补充、商业、农村、居民、城镇居民及其他养老金类型（可多选） | 选项号表示该选项被选中；空值不能直接当作未参加 |
| `new_rural_social_pension_participation` | `fn071` | 是否参加新型农村社会养老保险（新农保） | 1=是，2=否 |
| `pension_monthly_benefit_amount`（既有概念） | `fn079` | 新农保开始发放后的月养老金金额 | 连续值，元/月；仅`fn077=是`后询问 |
| `pension_nonparticipation_reason_new_rural_social`（既有概念） | `fn072s1`–`fn072s9` | 未参加新农保的原因（可多选）：当地未开展、经济负担、待遇/性价比、办理或缴费不便、制度设计、无本地户口、已有其他养老保险、其他 | 仅`fn071=否`者回答；选项号表示选中，未问/空值不代表“没有该原因” |

FN038题干明确排除机关事业单位养老金和企业基本养老保险；其“否”回答跳至FN071。FN039是在FN038“是”的路由下询问。故FN038不是“领取养老金”指标，不能与当前养老金领取、待遇金额、缴费状态或其他计划类型混为一谈；FN039的六个槽位也不能仅因空值就编码为未参保。FN071是单独的新农保参保题；“是”跳至首次参保年月，“否”进入FN072原因多选。FN072的分母因此只包括未参加者，未问原因项不能按“否”处理。FN079仅在开始领取（FN077=是）后询问，分母是领取者，不能把未问/缺失当成0元。FN079连接到已有月养老金金额概念，并修复该概念此前乱码的中文显示名。跨波等价性尚未建立，本轮只纳入2011变量目录，不推断其他波次。

## NHANES目录结构的可迁移做法

将问卷项目概念作为可搜索条目，同时保留波次、CHARLS原始变量码、官方变量标签、答案值码/选项语义、题目路由、数据来源和映射状态。这里的编码映射是公开的变量字典元数据，不是受访者逐条数据，也不产生任何关联结果。原始编码必须按波次与题目解释，不能直接假定是跨波统一编码。

## 构建与质量控制

- 生成脚本：`scripts/build_pension_participation_crosswalk.py`
- 新增字段级表：`audit/pension_participation_crosswalk_v1.csv`；FN072既有映射在`audit/pension_exposure_variable_mapping_v1.csv`中补充路由限制，`fn079`并入既有养老金月待遇概念。
- 概念汇总：`audit/pension_participation_summary_v1.csv`
- 依据：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`、`sources_official/CHARLS_2011_Codebook_extracted.txt`
- 代码本频数未复制或用作推断；没有读取个人记录。
- `fn038`、`fn071`二元值码与题干一致；FN039六类参保多选、FN071新农保状态及FN079月待遇分别映射；限定各题路由语义；未把结构性空值转为“No”。

候选映射仍不代表已经通过分析适格性审查。后续若构造正式变量，还需依据数据使用协议、实际分析样本适用路由、缺失码、抽样设计与目标估计量制定波次内分析规则。
