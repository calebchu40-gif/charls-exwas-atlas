# 2011年情绪/精神问题当前治疗方式映射复核

依据 CHARLS 2011 全国问卷 DA020 与 CodeBook，核实四个2011治疗选项并在主目录展示官方标签；此前尚未连接的`da020s3/s4`两字段接入既有 `reported_treatment_emotional_psychiatric` 概念。`da020s1/s2`已在原慢病辅助映射中，未重复新增：

| 字段 | 选项编码 | 官方含义 |
|---|---|---|
| `da020s1` | 1 | 精神科或心理治疗 |
| `da020s2` | 2 | 服用抗抑郁药 |
| `da020s3` | 3 | 服用镇静剂或安眠药 |
| `da020s4` | 4 | 以上均无 |

DA020题干询问当前对情绪、神经或精神问题采用的治疗方式，并允许多选；代码本为四项分别给出字段和值标签。新增行被映射为表型治疗/疾病管理类指标，不是环境暴露，也不代表精神疾病诊断。治疗方案是多选项；只可将明确的选项4解释为“以上均无”，不能把其他空槽或结构性缺失直接转成“No”。

这四项共享一个多选治疗构念，不拆成四个独立表型；2011扩展连接至已有2013/2015治疗概念，不新建重复Concept ID，也不暗示各波问法和路由已完全统一。目录删除了睡眠药词语触发的自动E分类，并清理了2011`da020s1/s2`的重复检索行。

- 构建脚本：`scripts/build_2011_psych_treatment_crosswalk.py`，已加入全量构建。
- 字段映射：`audit/psych_treatment_2011_crosswalk_v1.csv`。
- 官方依据：`sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`、`sources_official/CHARLS_2011_Codebook_extracted.txt`。
- 不复制CodeBook频数；不读取个人记录；没有拟合关联模型。
