# 工作与就业复选框类别标签导入（2026-10-22）

## 审查与变更

`audit/work_exposure_value_labels_v1.csv` 中有两类已审定工作/就业复选框类别此前没有显示在主目录：

1. `official selected-option label; checkbox slot, absence is not a negative response`（42个字段）。
2. `official questionnaire checkbox menu and codebook slot coding; frequencies omitted; absence is not a negative response outside the routed checklist`（11个字段）。

目录构建器现在只对这两个精确状态导入标签；没有将其他待核的问卷菜单、题目身份冲突或路由不确定标签一起放行。它们均是可检索的选项说明，不表示未选中、空白或不在路由中的记录等于“No”。代码本频数不导入、不用于样本量。

## 验证

- 53个逐波字段全部匹配主目录，标签与审定映射逐字相同，冲突0、缺字段0。
- 网站字段表现会在类别文本旁显示中文提示“官方复选框选项；未选中或空白不解释为No”或“官方问卷复选框选项；路由外或未选中记录不推断为No”，而不是仅将警告留在悬停说明中。
- 全量目录构建和网站元数据生成成功。E/P目录现有2,744行带审定类别/连续语义标签；唯一标签冲突仍是2013 `fn056_w2_5`。
- 33项 `DO NOT ANALYZE` 锁定与分流清单逐项一致；4项结果表合成测试通过；网站28个JSON均可解析，前端JavaScript语法通过。
- 未读取受访者回答、未拟合模型。这些多选字段仍须遵守映射中的题目路由与选项存储限制，不因显示标签成为分析就绪变量。

## 复现

`scripts/build_charls_atlas_catalog.py` 中 `work_exposure_value_labels_v1.csv` 的审核状态白名单控制导入；运行 `python scripts/build_ep_atlas_metadata.py` 可重建。
