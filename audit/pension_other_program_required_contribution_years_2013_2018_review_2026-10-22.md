# 2013–2018其他养老金所需缴费年限审计

更新：2026-10-22。2013、2015与2018问卷的FN091_W2问“还需要缴费多少年”，描述所选其他养老计划未来所需缴费年限；三波原始字段名为`fn091_w2`，均以年计。将其映射到已存在的`pension_required_contribution_years`候选概念，避免与同题既有链接重复计数。

分母限于该计划需要缴费者：前序FN087_W2=1时继续；FN087=2（不需要缴费）跳至预期领取问题，不可填0年。计划名称由FN084题组提供，制度可能异质；此概念仅表示受访者报告的所需年数。它不等于已经缴费年限（FN090_W4等）、加入该计划的年/月或预期领取年龄/等待时间。

问卷对超过法定上限设软校验，属于访问时提示而不是拒绝范围；不据此筛除原始值。Codebook统计极值只作审计线索，不作为分析可用范围。逐波特殊缺失码、有效值与实际计划分母待获准发布版字典/受控QA确认。未读取个人回答。

来源：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`、`CHARLS_2015_Questionnaire_extracted.txt`、`CHARLS_2018_Questionnaire_extracted.txt`中FN087–FN091；对应三波Codebook的fn091_w2。实现见`scripts/build_pension_supplementary_crosswalk.py`。
