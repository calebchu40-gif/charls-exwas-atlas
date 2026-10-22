# 2013平衡测试门槛与膝高测量同意字段复核

复核依据为 CHARLS 2013 Biomarker Questionnaire 与 Codebook 的字段身份、题干和响应码标签；只使用公开文档元数据，未读取个人级记录。

- `PD001`（Any Problems Prevent Balance）在平衡测试前询问近期手术、损伤或其他健康问题是否会妨碍受访者从椅子站起并保持平衡。目录将它从自动推断的E/P双候选改为单波P候选 `balance_test_preventing_health_problems_2013`，答案标签为1=Yes、5=No。它是自报的功能/测量适宜性问题，不是平衡障碍诊断、客观表现分数或一般疾病结局。分析须保留测试流程和缺失/跳题信息。
- `PK001`（代码本标签 Knee Height）实际询问是否理解膝高测量说明并同意测量，因此转为C类测量协议元数据 `knee_height_measurement_agreement_2013`，答案标签为1=Yes、5=No，排除于E/P关联矩阵。实际膝高记录在 `QK002`；PK001不是数值测量。
- 映射分别落在 `audit/health_symptom_variable_mapping_v1.csv`、`audit/biomarker_measurement_gate_crosswalk_v1.csv`，目录角色修正在 `audit/catalog_role_override_review_v1.csv`；自动构建器为 `scripts/build_balance_assessment_crosswalk.py`。
- 全量重建后：目录7,839行（E/P 7,225、C 614）；候选E/P概念1,177（E=909、P=277、E-only=900、P-only=268、双角色=9）；E/P源链接5,951条且全部匹配目录；全来源crosswalk6,110条（C 159，其中156匹配、3条目录外协议/资格记录）。2013元数据共现对98,770，仅是候选目录共现量，不是有效样本量。
- 核验：`pd001` 的候选角色只保留P；`pk001`只保留C；crosswalk标签和限制均可见；全部网站JSON可解析、`app.js`通过 `node --check`。不代表数据可用性、样本量或关联结果已经验证。
