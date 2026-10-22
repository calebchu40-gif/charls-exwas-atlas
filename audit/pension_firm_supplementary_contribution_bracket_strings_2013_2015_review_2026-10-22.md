# 2013/2015企业补充养老金缴费区间字符串字段

更新：2026-10-22。2013和2015官方问卷FN035_W2均先询问个人与单位合计月缴费金额，并继续询问其中个人支付占比；FN035_W2_bracket在受访者拒答或不记得金额时按500、1,000、2,000、3,500、5,000元分级展开。问卷与代码本变量目录将区间端点记录为2013 `fn035_w2_bracketbracket_min/max`、2015 `fn035_w2_bracket_min/max`。

四个端点按合计缴费金额题接入既有`pension_combined_contribution_amount_or_share`来源概念；个人缴费百分比仍是独立概念。Codebook对端点声明`A String Variable`，所以这次只把其题意、角色和挂接关系写入目录，不把字符串转为数值，不依据括号阈值推断实际金额，也不做区间插补。单位是问卷上下文所示元/月，但实际存储形式须在获批发布字典确认后才可用于分析。

来源：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`中FN035_W2段落约7377行；`sources_official/CHARLS_2015_Questionnaire_extracted.txt`中FN035_W2段落约6392行；对应官方Codebook的min/max字段。构建规则：`scripts/build_pension_supplementary_crosswalk.py`。未读取个体数据。
