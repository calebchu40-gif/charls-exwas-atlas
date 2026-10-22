# 2018其他养老保险参与/领取状态字段审计

更新：2026-10-22。2018问卷FN083_W2询问已列养老计划之外，受访者是否正在参加、正在领取或没有参加其他养老保险。问卷选项为1=正在参加但尚未领取，2=正在领取，3=没有参加。官方2018 Codebook概括为Yes Participate、Yes Receive、No，未对No显示数值码，因此目录取值码3仅依问卷选项核对。

该题有前序计划条件：FN083_W2不是无条件对所有人提问；FN083=3时还依各已列养老金计划状态跳至后续题。已映射到2013/2015已有的`pension_current_participation_or_receipt_unspecified_scheme`候选概念，同时保留波次路由。FN084_W4只在此题组后进一步问这份计划当前是否领取，二者并非重复字段；不得以一个字段替代另一字段或把跳题当作“未参加”。

来源：`sources_official/CHARLS_2018_Questionnaire_extracted.txt`中FN083_W2条件路由及题目；`sources_official/CHARLS_2018_Codebook_extracted.txt`中fn083_w2条目。实现见`scripts/build_pension_supplementary_crosswalk.py`。没有读取个人回答。
