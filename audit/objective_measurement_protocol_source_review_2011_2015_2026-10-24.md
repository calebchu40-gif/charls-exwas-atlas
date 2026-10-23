# CHARLS 客观测量协议字段来源复核：2011–2015

日期：2026-10-24。仅审阅官方问卷、代码本与字段元数据；没有读取 CHARLS 个体回答、Codebook 统计频数或测量结果。

## 核实结果

- 2011 官方体检手册记录，血压测试前30分钟内是否吸烟、运动、饮酒或进食；手册项目号为 `LI875`。2011发布 Codebook 对应候选字段标签为 `QA017`，并列有1=Yes、5=No、8=Don't know。目录现明确保存手册项目号与发布字段名的差异。该字段是血压测试背景，不能解释为习惯性行为、一般饮食暴露或抽血空腹状态。
- 同一2011手册把椅子起立测试座椅高度记录为 `LI007`；2011 Codebook 则将 `QH006` 标作 Height。当前材料不足以闭合这两个代码的发布字段对应关系，故 `2011/QH006` 保留在 C 类并标为 `HOLD FOR RELEASE FIELD IDENTITY RECONCILIATION`，不显示答案标签，也不与受访者站立身高 `QI002` 混淆。
- 2013 官方体检问卷将 `QH006` 定义为椅面离地高度，单位厘米；它属于重复椅子起立测试的测量设置。
- 2015 官方体检问卷把 `QH006` 用作椅子类型选择：1=CHARLS 42 cm椅、2=其他椅；只有选择其他椅时，`QH006_1` 才记录其他椅高度（cm）。因此不把2015的 `QH006` 当成连续椅高，也不把条件缺失解释成0。

这些都是测量协议/背景字段，仅用于解释相应体测过程，不进入E/P关联配对。它们的跨波字段与意义不可自动合并。2011身份待核不会解除正式E/P分析锁；全局 `DO NOT ANALYZE` 清单保持89条。

## 资料与实现

2011手册由 CHARLS 公开数据资料页链接下载：<https://charls.charlsdata.com/Public/ashelf/public/uploads/document/public_documents/application/Biomarker-manual-2011.doc>。仓库保存原始公开文件及提取文本；原始文件 SHA256：`5D269E24409F0C2BCC1910BBC483498440FDDA26069AF03BFF2C5379181C71D2`。2013/2015逐波依据保存在 `sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt`、`CHARLS_2013_Codebook_extracted.txt`、`CHARLS_2015_Biomarker_Questionnaire_extracted.txt`、`CHARLS_2015_Codebook_extracted.txt`。

审计映射：`audit/measurement_protocol_crosswalk_v1.csv`；专项幂等更新器：`scripts/apply_objective_measurement_protocol_review.py`。两种元数据流水线都会先应用通用C审阅，再应用本复核，避免来源信息被泛化覆盖。C占位审核表记录2015正式选择标签，并将逐字段来源和路由信息传至主目录及网站分片。

完整 `python scripts/build_ep_atlas_metadata.py --finalize-only` 重建成功；全部200项Python测试通过，所有静态JSON解析、JavaScript语法检查、Python编译及 `git diff --check` 通过。站点C分片986行；E=4,750、P=2,068；E/P概念1,429、源字段映射6,625；正式模型数为0。
