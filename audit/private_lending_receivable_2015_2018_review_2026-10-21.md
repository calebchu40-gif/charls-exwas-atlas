# 对外借款未偿回收字段及2015冲突审计（2015、2018）

核查日期：2026-10-21。仅据官方问卷原页、官方Codebook和公开字段目录进行元数据审计；未读取个体数据，Codebook频数不作为分析样本量。

2015问卷印刷页219显示：`HC039_W3`询问是否有人/单位尚欠受访者已借出的钱；若是，`HC040_W3`记录欠款金额（人民币元）。2018问卷相同代码的题意及Codebook标签也明确为借出未收回金额。概念上这是应收款，不是受访者欠他人的负债，需与HD001/HD003及2015同页之前关于民间借贷义务的题目分开。

但2015 Codebook将`hc039_w3`和`hc040_w3`都标成仍需偿还互助会/轮转储蓄信用组织的金额，与2015问卷题页的二元筛选题及后续应收金额题不符。目录保留2015问卷题意作为可检索候选，同时将这两个2015字段显式锁为“DO NOT ANALYZE”，直到CHARLS公开发行版字段身份/标签冲突由官方文件或数据字典版本核实。不能以Codebook频数形态单独裁定字段含义。2018映射依据问卷和Codebook一致证据，但仍须在授权数据内核实特殊码、实际分母及条件路由。

复现材料：`sources_official/CHARLS_2015_Questionnaire.pdf`印刷页219及`CHARLS_2015_Codebook_extracted.txt`约29848行；2018依据`CHARLS_2018_Questionnaire_extracted.txt`的HC039_W3/HC040_W3题组和`CHARLS_2018_Codebook_extracted.txt`字段标签。映射由`scripts/build_personal_income_crosswalk.py`生成；全量重建运行`python scripts/build_ep_atlas_metadata.py`。
