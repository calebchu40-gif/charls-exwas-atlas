# 家户捐助与补偿来源选择字段审计（2026-10-22）

CHARLS 2011、2013、2015家户收入问卷的 `GD003` 均询问过去一年家户是否收到所列来源收入/补偿，采用可多选清单，并在后续字段中分别记录捐助价值、征地补偿和住房拆迁补偿金额。官方 Codebook 将来源选择字段标为 `gd003s1`（社会捐助）、`gd003s2`（征地补偿）、`gd003s3`（拆迁补偿），另有 `gd003s4`（None）。

本轮将前三项按“来源选择状态”分别接入三个三波候选概念；金额仍使用既有 `gd003_1/_2/_3` 金额概念。来源选择字段的代码是选项标记，不是金额，也不把 `gd003s4` 的共同“None”项当作第四种暴露。该共同None选项单列为C类清单元数据，不进入E/P配对。代码本中的选项频数没有复制或用于样本量推断。

分析边界：保留官方选项码及各波字段，不将源选项码误作0/1量表；没有勾选的存储形式必须回到获准发行数据字典验证，空白、跳题和不适用不得自动等同于No。`gd003s4`是共同无来源选项，不能同时作为三条源选择的独立负值；家户来源也不可直接赋给每位家庭成员。本次没有读取微观作答值或派生个体暴露。

重建脚本 `scripts/build_household_transfer_receipt_crosswalk.py` 输出 `audit/household_transfer_receipt_crosswalk_v1.csv` 并进入主构建流水线。官方依据为各波家户收入问卷及Codebook，摘录保存在`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`、`CHARLS_2013_Questionnaire_extracted.txt`、`CHARLS_2015_Questionnaire_extracted.txt`和相应波次Codebook。
