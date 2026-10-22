# 吸烟与饮酒年龄/日历年选择器角色复核（2026-10-22）

## 结论

11条吸烟/饮酒时间格式选择器现归为C类测量/问卷元数据，不作为暴露进入ExWAS关联配对。选择器本身只说明相邻回答组件应解释为年龄还是日历年；它既不是有序暴露，也不应单独作为数值结局。与之相邻的具体年龄、年份回答组件仍按字段原角色保留，后续需按波次选择器解读，不能把年龄与日历年跨波直接合并。

## 逐波标签

- 吸烟开始时间 `da065`：2013、2015为1=Age、2=Year；2018顺序反转为1=Year、2=Age。
- 饮酒开始/停止时间 `da070`、`da071`：2011为1=Age、2=Year；2013、2015、2018为1=Year、2=Age。

此差异说明必须逐波读取值标签，不能以单一全局编码表统一。映射来自 `audit/behavior_exposure_variable_mapping_v1.csv` 中带 `official selector code reviewed` 状态的官方代码本核对记录；原始来源文档路径列于 `Source.File` / `Source.Document`。未复制代码本频数或任何个体回答。

## 实施与验证

`audit/catalog_role_override_review_v1.csv` 为11条选择器记录明确指定 `remove_role=e`、`keep_role=c` 及 `age_year_component_selector` 类型；`scripts/apply_catalog_role_overrides.py` 将其从E候选中移除。`scripts/build_ep_concept_source_crosswalk.py` 将这些概念源行标为C，并保留波次标签、语义及来源。构建后的来源交叉表中11条均为C、0条为E；字段目录按角色统计为E 4,566、P-only 1,903、C 911、E/P双角色164，共7,544行。E/P来源交叉表为6,599条，网站目录含标签行2,808条。年龄/年份回答组件仍可作为候选字段，但应与选择器联动解释，并在授权数据QA阶段检查缺失、路由及发行版编码。

该修正只涉及公开字段元数据和检索角色，不读取个体记录、不生成样本量、不拟合关联模型。完整流水线、结果表结构合成测试、DO NOT ANALYZE清单、前端与JSON检查在本审计之后执行，结果记录在进度日志及打包说明中。
