# 2011 FM010当前养老金领取状态复核

核对文件：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`及`CHARLS_2011_Codebook_extracted.txt`。仅依据官方问卷与Codebook元数据，未读取个人级记录。

- 问卷FM模块的访员说明限定为已办理退休或退职者：FB011=1或FB012=1。FM010直接询问当前是否领取养老金，问卷标签为1=Yes、2=No；回答Yes跳至FM018养老金详情，No跳至FM042。Codebook同样列出1=Yes、2=No。
- 将`2011::fm010`接入现有候选概念`pension_receipt_after_job_exit`，中文定义为退休/退职后当前养老金领取状态。它是E侧单波、条件性样本候选；不得解释为全体样本养老金覆盖、养老保险参保，亦不得替代一般养老金模块。分析时分母须限于问卷定义的已退休/退职人群，并核实发布数据中FM010是否对该完整分母均有回答。
- `audit/retirement_history_exposure_mapping_review_2026-10-17.md`曾因当时未在所审问卷片段中定位该题而暂缓映射。本次已在正确的2011基线家庭问卷退休模块找到题干和路由，故更新决定；此前搁置属于信息未完整，不是题目不存在。
- 构建器：`scripts/build_retirement_history_exposure_crosswalk.py`；值标签从2011 Codebook提取并仅保留答案类别、不含频数。仍是候选变量，不是已验证的实际分析变量或结果。
