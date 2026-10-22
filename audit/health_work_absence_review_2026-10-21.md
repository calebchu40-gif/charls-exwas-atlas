# 2013年健康原因导致的工作缺勤字段审计

核查日期：2026-10-21。2013 Codebook将`FC013`标为“Days No Work due to Health Problems”，并列为连续天数变量；问卷题干是“过去一年因健康问题缺勤多少个工作日”，回答范围0–366，且明确要求没有缺勤时记录0。

FC013位于FC当前工作/农业就业模块。问卷前部的FC branchpoint说明：上一年做过农业劳动（`FA001=1`）者进入FC001等农业工作题组；未做农业但上周做过非农业工作（`XF2=1`）者转到FC019。因此，目录把FC013定义为“健康原因导致的工作缺勤天数”，限于2013字段，并须保留农业工作分支的适用人群。显式0表示合格分支中没有因健康原因缺勤的工作日，不代表没有健康问题；结构性缺失不可置零。

该字段从自动E候选改列P候选，因为它是由健康原因造成的功能/工作参与结果；不当作诊断、一般残疾量表、暴露或其他波次的可比指标。后续分析须按FC001–FC012与FA001路由限定风险集，并核对实际发布变量字典和特殊缺失。候选Concept ID为`health_related_workdays_missed_2013`，单位为过去一年天数。

来源：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`（FC branchpoint及FC013题干/0值说明）、`sources_official/CHARLS_2013_Codebook_extracted.txt`（连续变量范围/可用性）；生成脚本：`scripts/build_health_work_absence_crosswalk.py`。未读取个体回答。
