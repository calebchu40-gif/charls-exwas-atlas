# 最后一批通用待核E字段审核（2026-10-23）

本批按官方波次问卷与Codebook逐字段核对重建前剩余的12条E类通用“not yet reviewed”状态。最终目录的通用待核E类值标签状态由12降至0。这里的“0”只表示没有泛化的待核提示，不代表这些指标都可直接用于分析；问卷路由、数据发布编码、分析分母、跨波可比性和模型纳入仍需逐项核验。

- **2011家庭支出金额（ge010_4、ge010_6、ge010_7）**：记录过去一个月的家具/耐用品消费、医疗和健身支出，单位为人民币元，属于家庭层级连续金额。Codebook描述性汇总不用于推导有效范围或分析截点；保留家庭财务回答者、参考期和波次，不将其解释为个人支出。
- **2013其他工作数量（fa006_w2_5）**：连续计数，指两次访谈之间至少做过一个月的其他工作数量。它不是离散类别；需保留跨访谈期窗口和问卷跳题，不能把未问到当作零。
- **其他资产租金收入状态（2018 ha064；2020 ge014）**：问卷和Codebook支持显示`1=Yes; 2=No; 997=Don't know; 999=Refused to answer`。这是家庭层级、路由后的状态题；展示编码不代替核实符合条件的家庭分母，也不把结构性跳题解释为否。
- **2020工资变化方向（ga006）**：显示`1=Decreased; 2=Increased; 3=Unaffected`。其参考期为春节至访谈、由受访者报告与COVID-19相关的工资方向；与条件触发的金额字段ga006_1/ga006_2分开，不代表因果效应。
- **2011职业分类（fh015_gb、fh015_isco）**：标明为GB/ISCO职业分类代码。分类体系定义不是问卷回答类别，故不添加虚构的值标签或Codebook频数；保留无酬家庭经营工作路线提示。
- **2020先前工作离职原因（fa019）**：目录补入官方问卷类别，同时维持既有`DO NOT ANALYZE`锁，直至先前状态修正路由和授权发布数据编码完成核对。
- **2020疫情家庭应对字段（gf015_s4、gf016_s8）**：gf015_s4显示Codebook可核对的`0=No; 4=Yes`，但保留“无上述情形”选项冲突对应的`DO NOT ANALYZE`锁。gf016_s8由于问卷与Codebook选项身份不一致，保持空值标签和冲突说明，并保留锁。两项的锁定状态、候选/分析状态均未被本次值标签导入改写。

本次没有将任何Codebook频数、参与者记录或描述性极值加入网站。生成目录中的元数据共现仍不是样本量，也没有计算正式关联模型。字段级主数据见`site-prototype/dist/catalog_e.json`；上游来源审核记录见`audit/household_covid_economic_crosswalk_v1.csv`、`audit/household_economic_exposure_mapping_v1.csv`、`audit/household_other_asset_rental_income_status_crosswalk_v1.csv`、`audit/interwave_other_job_crosswalk_v1.csv`、`audit/personal_income_exposure_mapping_v1.csv`和`audit/work_exposure_value_labels_v1.csv`。
