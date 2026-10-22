# 2018年健康原因导致的自家农业工作缺勤字段审计

2018官方问卷将`FC013`置于“Self-Employed Agricultural Work（农业自雇）”模块，题干中文明确询问过去一年有多少天因健康原因不能干农活，范围0–366天，并要求没有缺勤时填0。相邻FC009–FC012也围绕过去一年自家农业工作；该字段不能解释为所有形式就业的总缺勤，也不是临床疾病诊断。

Codebook将`fc013`标为“Days Not Working due to Health Problems”，Obs=8,970、观测最小值0、最大值365；问卷允许填至366。保留问卷允许范围和Codebook观察最大值差异，获批数据字典及个人记录授权到位后再核实，不自行裁剪或删除366。0仅表示题目适用人群中没有缺勤日；未进入模块的结构性缺失不填0。

本字段列为单波候选表型`health_related_household_agricultural_workdays_missed_2018`。虽然与2013 FC013同码且均涉及健康相关工作缺勤，但2018题干明确为自家农活、位于农业自雇子模块；2013题目位于不同工作模块且问“work days missed”。在路由及分析对象未经进一步等价审查前分开建概念，不直接合并。

来源：`sources_official/CHARLS_2018_Questionnaire_extracted.txt`（工作状态题、FA007_W4/FA_END_W4路由、FC Self-Employed Agricultural Work及FC013）；`sources_official/CHARLS_2018_Codebook_extracted.txt`（变量类型及观测范围）。生成脚本：`scripts/build_health_work_absence_crosswalk.py`。未读取个人回答。
