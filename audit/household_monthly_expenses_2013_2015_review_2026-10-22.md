# 2013/2015家庭月度支出补充映射（2026-10-22）

## 核实结果

两轮官方问卷均在GE009题组询问“上个月”家庭在下列项目的支出：

- `ge009_4` 家政、管家和佣工费用（Codebook标签为Expenditure on Servants）；
- `ge009_5` 当地交通；Codebook简称Transportation。与长途旅行支出`ge010_2`分开；
- `ge009_7` 娱乐，包括书报、影音制品、影院和酒吧等相关费用。

2013、2015问卷均要求无相应支出填0、无法回忆填-9999。金额单位为人民币元，测量层级为家庭。三项按概念分别映射并只覆盖2013/2015，不向2011或其他波次推断题目存在，也不把家庭金额当作受访者个人消费。

## 字段映射

| 概念 | 2013 | 2015 | 窗口/单位 | 边界 |
|---|---|---|---|---|
| 家庭月度家政/佣工支出 | `ge009_4` | `ge009_4` | 上个月，元 | 不推断雇佣类型或服务时长 |
| 家庭月度当地交通支出 | `ge009_5` | `ge009_5` | 上个月，元 | 不与长途旅行费用合并 |
| 家庭月度娱乐支出 | `ge009_7` | `ge009_7` | 上个月，元 | 不由支出金额推断活动参与频率 |

0表示问卷指示下的无支出；-9999是无法回忆，必须作为特殊缺失处理，不能当负金额。跳题/结构缺失不能自动改为0。家庭财务回答者可能与主受访者不同，不能把家庭支出复制解释为个人暴露或与个人记录重复计数。代码本均值/频数未作样本量、标签或填补规则。

## 来源与实现

官方来源：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`、`sources_official/CHARLS_2013_Codebook_extracted.txt`、`sources_official/CHARLS_2015_Questionnaire_extracted.txt`、`sources_official/CHARLS_2015_Codebook_extracted.txt`。映射由`audit/household_ses_field_coverage_v1.csv`中的六条波次字段审计记录驱动，概念定义写入`scripts/build_household_economic_exposure_crosswalk.py`并汇入`audit/household_economic_exposure_mapping_v1.csv`。该候选映射不等于统计模型已获准或已验证；没有读取个体记录。
