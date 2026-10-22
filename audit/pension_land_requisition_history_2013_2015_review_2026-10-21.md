# 2013/2015土地征收经历与征地养老金金额格式字段审核

日期：2026-10-21。依据CHARLS 2013/2015官方问卷与对应代码本；未读取个人级数据。

2013/2015征地养老金模块的`FN079_W2_1`询问土地是否曾被征收，取值为Yes/No；回答Yes才进入`FN079_W2_2`询问征收年份。因此分别映射为“土地征收经历”和“土地被征收年份”候选暴露，保留该筛选路由。土地征收年份是回顾性时间信息，正式分析前应结合受访者年龄、访谈波次和目标估计量定义，不可将其解释为当前居住地或暴露剂量。

`FN079_W2_9`（2013/2015）是预期征地养老金待遇的金额形式选择器：1=每月人民币，2=一次性人民币；金额分别储存在`fn079_w2_9_1/_2`。该父项转为C类测量元数据。预期金额只属于相应计划的未领取待遇路由，不能解读为参保状态；孩子字段保留不同单位。

问卷与代码本来源：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`、`CHARLS_2013_Codebook_extracted.txt`、`CHARLS_2015_Questionnaire_extracted.txt`、`CHARLS_2015_Codebook_extracted.txt`。构建规则写入`build_pension_exposure_crosswalk.py`、`build_pension_supplementary_crosswalk.py`和`apply_catalog_role_overrides.py`；角色和协议记录写入`catalog_role_override_review_v1.csv`及`measurement_protocol_crosswalk_v1.csv`。候选映射不代表已完成样本资格/缺失处理审查。
