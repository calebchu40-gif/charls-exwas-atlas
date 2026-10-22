# 就业求职与离职补偿候选审计（2026-10-21）

> **来源身份更正（2026-10-21）：**本文旧版本引用的 `CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` 实际内容是2013随访问卷。本文涉及的2011题干或路由判断须对照正确的官方2011基线问卷复核；在复核完成前，不能把该旧摘录当作2011题意证据。处理范围及当前状态见 [`2011_questionnaire_source_identity_correction_2026-10-21.md`](2011_questionnaire_source_identity_correction_2026-10-21.md)。

## 范围和结论

依据本地CHARLS各波官方问卷、代码本和已建原始字段目录，补充5个工作/离职补偿候选概念、16条波次字段链接。它们都是目录候选，不是经个体数据验证的分析变量。所有公开代码本频数均未复制到网站或crosswalk。

| 候选Concept ID | 波次字段 | 题意/分支 | 单位与边界 |
|---|---|---|---|
| `job_search_in_past_month_2011_2018` | 2011/2013/2015/2018 `fk002` | 过去/上一个月是否找新工作，`1=Yes; 2=No` | 属于求职模块；不能当作失业诊断，需以释放数据核实各波适用人群/分母。与2020 `ff003`分开。|
| `non_retirement_compensation_at_job_exit_2011_2015` | 2011/2013/2015 `fl021` | 离开最近一份工作时，除法定退休金外是否得到其他款项，`1=Yes; 2=No` | 回溯性且限有最近工作史者。2013/2015举例包括慰问金/工伤补偿；不等同当前收入或养老金待遇。|
| `job_exit_compensation_amount_2011_2015` | 2011/2013/2015 `fl022_1` | 上项Yes后追问金额 | 元；名义金额，跨波比较需处理年份/价格变化。未问不等于0。|
| `service_years_used_for_compensation_2011_2015` | 2011/2013/2015 `fl022_2` | 上项Yes后追问补偿依据工作年数 | 年；不是总工龄的通用指标，保留受访者报告的补偿计算依据。|
| `job_exit_severance_package_2018` | 2018 `fl021`, `fl022_w4_1`, `fl022_w4_3` | 是否获离职补偿包、金额及强制离职待遇的计算年数 | 金额元；`_3`为用于计算被迫离职待遇的就业年数。2018问卷改用severance package并举买断工龄/伤残津贴等例子，与早期款项范围可能不同，因此单列概念，不与2011–2015直接等同。|

## 官方依据

- 2011基线家户问卷官方摘录：`sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt`，FK002和FL021–FL022部分。2011代码本`audit/CHARLS_2011_Codebook_extracted.txt`可确认FK002的Yes/No标签，但未检出FL021–FL022对应的代码本分布；不推断观测频数或实际变异。
- 2013、2015问卷与代码本：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`、`sources_official/CHARLS_2013_Codebook_extracted.txt`、`sources_official/CHARLS_2015_Questionnaire_extracted.txt`、`sources_official/CHARLS_2015_Codebook_extracted.txt`。FK002标签为Yes/No；FL021=Yes才问FL022的金额和工作年数。
- 2018问卷与代码本：`sources_official/CHARLS_2018_Questionnaire_extracted.txt`、`sources_official/CHARLS_2018_Codebook_extracted.txt`。FK002问过去一个月求职；FL021问severance package，Yes后问金额/支付依据/计算年数。
- 逐变量目录来源和单位见`audit/work_exposure_crosswalk_v1.csv`、`audit/work_exposure_value_labels_v1.csv`；站点概念详情见`site-prototype/dist/work_exposures_v1.json`。

## 路由与分析限制

1. 有值标签不代表普遍适用；求职和离职补偿问题须按波次核对模块路由、访谈类型、最近工作资格及实际缺失码。
2. 结构性缺失、拒答/不知道码、未问和No不可互换。分析前必须在获准数据中核实问卷路由及特殊码。
3. 2011 FL021–FL022虽有问卷字段，摘录代码本中没有相应观测分布；应保留为待核候选，不能宣称有足够变异。
4. 补偿金额为名义元，不宜未经通胀/价格基期处理直接合并。2020求职`ff003`另列，未据题意/模块名称假设与早波等价。
5. 不纳入雇主名称、地点或其他开放文本；也未读取个人级数据或估计关联。

## 构建与验证

就业专题生成脚本`python scripts/build_work_exposure_crosswalk.py`现生成72个工作暴露/工作史概念、199条映射；工作标签脚本`python scripts/build_work_exposure_value_labels.py`处理433条标签/语义记录。全量入口`python scripts/build_ep_atlas_metadata.py`完成；新增16条E/P链接均匹配主目录，新增5个候选概念没有同波同码重复链接。最新全目录845个候选E/P概念（E=585、P=269、交集9），E/P链接5,252条；C类来源记录23条，其中3条既有资格元数据不在E/P字段目录；总字段目录7,629行（E/P 7,151、C 478）。
