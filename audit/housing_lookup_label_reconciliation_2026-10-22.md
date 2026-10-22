# 住房/家户检索页与主目录值标签对账（2026-10-22）

## 对账结论

`site-prototype/dist/housing_catalog_v1.json`由住房变量、食物环境、烹饪燃料和家户耐用品映射合并构成，共817条检索行、174条含非空标签/测量语义。严格只取状态明确为`Official codebook response labels reviewed`或`official questionnaire/codebook response labels reviewed; frequencies omitted; wave-specific`的条目，共131个波次—字段键。

将这131个精确`wave + code`与主目录`site-prototype/dist/catalog.json`连接后，均找到相同官方标签且无冲突；其中对应主目录E类131行，另有3个相同字段键还出现在C类元数据行。**没有任何额外值标签需要补入主目录**，因为这些明确审定的回答标签已由住房、食物环境或家户资产审计链写入主目录。故不另建重复的标签导入逻辑；专页仍提供更丰富的概念、构造和警示语义。

状态为`catalog-label candidate; questionnaire review pending`的条目没有被当作已审标签转入主目录。连续数量的单位说明也未伪装成离散回答类别。对账只比较公开字段级标签文本和来源，不读取个人回答或CodeBook频数。

## 复核方法和来源

- 专页来源：`scripts/build_housing_catalog.py`；站点数据：`site-prototype/dist/housing_catalog_v1.json`。
- 主目录来源：`scripts/build_charls_atlas_catalog.py`；站点数据：`site-prototype/dist/catalog.json`。
- 连接键：调查波次与小写规范化源字段码。
- 标签审核门槛：仅接受上文明确的官方CodeBook/问卷审定状态；候选、连续单位语义和待审状态排除。
- 在审计时间点，总E/P目录仍有2,478行非空值标签文本；此项对账没有增加标签计数。

住房专页没有填补总体标签覆盖的缺口；剩余问题仍需按字段题意、跳题、波次可比性和字段类型逐项审查，不能因为已出现在专页就视为模型就绪。
