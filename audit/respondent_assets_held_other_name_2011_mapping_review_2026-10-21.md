# 2011 受访者名下以他人姓名持有的金融资产字段补映

审计日期：2026-10-21。依据2011正确基线家庭问卷、2011 Codebook及2013/2015/2018对应问卷与Codebook题目标签；Codebook频数未用于定义指标或分母，本轮未读取个人级记录。

## 2011证据与映射

2011正确基线家庭问卷的个人资产部分询问：受访者是否还有属于自己的存款、政府债券、股票或基金，但登记在受访者本人或配偶以外的人名下（HC021）；若回答有，追问这些资产总价值（HC022）。2011 Codebook以`hc021`和`hc022`列出相应字段及标签；HC021选项为1=Yes、2=No。金额题没有在问卷中规定按市值或面值估价，故只保留“受访者报告金额”，不改称市场价值。HC022只在HC021肯定路径适用；跳题、拒答、特殊缺失及值为0的实际含义需在获批数据中核实。

跨波对照显示，2013、2015和2018也询问受访者拥有但登记在本人及配偶以外姓名下的存款/债券/股票/基金，并以HC022追问总价值。2018拒答选项与前几波的问卷呈现不同，目录保留逐波代码标签；四波概念可映射至同一候选概念，但不可把未提问或跳题自动视为无资产。该构念是受访者层级的“持有人与登记姓名不一致”状态/金额，不代表家庭金融资产总额。

## 修订内容

- 将2011 `HC021` 和 `HC022` 接入既有`respondent_assets_held_in_other_persons_name`及`value_of_respondent_assets_held_in_other_persons_name`概念；新建概念0个，增加两条波次—字段链接。
- 修正`build_personal_income_crosswalk.py`的2011来源引用：引用正确的`CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`，不再生成不存在或身份错误的泛化2011问卷路径。
- `HC021`显示逐波答案标签；保留2018的拒答码差异。`HC022`金额基础仍注明为受访者报告，不推断市值/面值。
- 2011 Codebook只用于确认字段标签及选项标签，不使用任何频数/百分比。

## 可复核文件

- 正确基线问卷：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`（HB/HC个人资产章节，HC021–HC022）。
- 2011字段标签/答案标签：`sources_official/CHARLS_2011_Codebook_extracted.txt`。
- 后续波次：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`、`CHARLS_2015_Questionnaire_extracted.txt`、`CHARLS_2018_Questionnaire_extracted.txt`及各自官方Codebook文本。
- 重建脚本：`scripts/build_personal_income_crosswalk.py`；结果进入`audit/personal_income_exposure_mapping_v1.csv`、E/P主目录与网站查询目录。
