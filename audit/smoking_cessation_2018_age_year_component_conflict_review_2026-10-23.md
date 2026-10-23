# 2018年吸烟戒烟时间年龄/日历年组件冲突复核（2026-10-23）

## 结论

2018年DA062为“完全戒烟时间”项目。官方问卷第3089–3090行写明“DA062_1 Age / DA062_2 Year”；同波Codebook第43140–43158行却将DA062_1标为Year、DA062_2标为Age。两份官方材料对同一字段的组件身份直接冲突，不能根据变量名、分布或其他波次推断哪一份正确。

因此，DA062_1与DA062_2继续留在可检索目录，但均标记DO NOT ANALYZE；不赋予年龄或日历年单位，不进行跨波合并。DA062本身作为格式选择器归入C类测量元数据，不进入E/P矩阵；由于对应子字段映射有冲突，暂不展示其选择器代码标签。只有CHARLS官方发行说明/勘误或字段级澄清可解除该锁定。没有读取个体记录，也没有将Codebook频数作为样本量。

## 依据与实现

- `sources_official/CHARLS_2018_Questionnaire_extracted.txt:L3087-L3091`
- `sources_official/CHARLS_2018_Codebook_extracted.txt:L43128-L43158`
- `audit/behavior_exposure_variable_mapping_v1.csv`保留两份材料各自的标签和明确冲突说明。
- `audit/catalog_role_override_review_v1.csv`将DA062改为C类，并对两个组件增加波次精确的分析锁。
- `scripts/apply_catalog_role_overrides.py`会将自动发现遗漏的组件字段补回为可检索E候选并锁定，避免冲突字段因角色推断而消失。

2013、2015及2020的戒烟时间选择器另经问卷和Codebook核对：1=Age、2=Year，已作为C类元数据处理；具体回答组件仍分别保留年龄/年份含义。

## 验证

未访问受限参与者级数据。验证项目包括完整元数据流水线、锁定项清单一致性、Python单元测试、前端脚本语法、延迟加载器测试及Git差异空白检查。
