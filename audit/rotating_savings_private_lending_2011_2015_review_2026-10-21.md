# 轮转储蓄与私人借贷字段审计（2011–2015）

> **来源身份更正（2026-10-22）：**2011来源现更正为`CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`；旧路径文件实际为2013随访问卷。按正确2011问卷重核后，2011/2013题意一致；2015私人借贷题与Codebook措辞差异仍按下文保留。生成器已使用正确2011文件。

核查日期：2026-10-21。依据CHARLS 2011基线、2013/2015官方问卷及对应Codebook公开字段标签进行元数据审计；未读取个体回答，也未把Codebook频数当作有效分析分母。

2011与2013 `HC036`询问过去一年是否参加轮转储蓄/信用协会，`HC037`询问仍需偿还给该组织的金额。分别映射为参与状态与当前债务金额，不把二元参加状态当作债务额度；金额字段的路由需在授权数据中核验。

2015问卷改问过去一年是否参与“民间借贷（如标会等）”；随后`HC037`询问当前还欠民间借贷多少钱。Codebook继续将`HC036/HC037`标为轮转储蓄/信用协会。因问卷用语更宽、Codebook用语较窄，2015状态与金额均保留为单独波次概念，不自动与2011/2013合并。问卷还在HC036后出现`HC036_W3`金额槽和`HC036_W3_1`区间追问，但2015公开Codebook和本项目发布变量目录均没有`HC036_W3`这一观测字段，故不生成数据字段映射、不把文本题槽当作有数据变量。

来源：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`第6894–6903行附近及`sources_official/CHARLS_2011_Codebook_extracted.txt`；`sources_official/CHARLS_2013_Questionnaire_extracted.txt`第9145行附近及2013 Codebook；`sources_official/CHARLS_2015_Questionnaire.pdf`印刷页219（PDF页225）与`CHARLS_2015_Codebook_extracted.txt`约29834–29845行。构建器：`scripts/build_household_lending_debt_crosswalk.py`；全量重建：`python scripts/build_ep_atlas_metadata.py`。

## 2011来源身份复核补充（2026-10-22）

正确的2011基线问卷第6894行附近确认HC036询问过去一年是否参与rotating savings and credit association；HC037问仍需偿还给该组织的资金。回答HC036=No跳转至HD001；只有Yes路径继续到HC037。2013同一题组也将No路由至HD001；2015问卷改称private lending，并有问卷中出现但官方变量目录/Codebook未列的HC036_W3文本字段，仍不生成该字段映射。代码生成脚本`build_household_lending_debt_crosswalk.py`已使用正确2011基线问卷来源，本次仅更正文档及确认路由，不读取个人记录。
