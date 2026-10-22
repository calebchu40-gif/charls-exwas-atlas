# 2011疼痛、行动和认知锚定情景字段角色审计

核查日期：2026-10-21。基线家户问卷在DE007–DE024题组开头说明：受访者将对与本人年龄和背景相同的假设人物进行健康评价；题目的人名性别在家户内随机选定。DE007–DE009是疼痛情景，DE010–DE012是睡眠情景，DE013–DE015是行动情景，DE016–DE018是认知情景。它们测量受访者对标准化虚构健康情景的评分，不是受访者本人疼痛、行动能力或认知结局。

原始答案尺度为1=None、2=Mild、3=Moderate、4=Severe、5=Extreme。此前DE010–DE012因错误的2011问卷来源而暂列P并锁定；正确基线问卷已确认它们为睡眠情景，现与其他题一并列C，详见`audit/codebook_only_sleep_severity_2011_identity_review_2026-10-21.md`（更正日期2026-10-22）。目录将十二字段从自动E/P角色移至C类测量/锚定情景元数据，按疼痛、睡眠、行动、认知分组；标签与问卷/Codebook来源保留。它们不得进入个人表型矩阵，且与DE001–DE006随机抽中受访者本人回答的健康问题区分。

依据：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`中DE题组说明、随机性别程序及上述情景；`sources_official/CHARLS_2011_Codebook_extracted.txt`对应字段。映射由`scripts/build_health_anchoring_vignette_metadata_crosswalk.py`生成，并由`audit/catalog_role_override_review_v1.csv`实施角色修正。完整入口：`python scripts/build_ep_atlas_metadata.py`。未读取个人回答。
