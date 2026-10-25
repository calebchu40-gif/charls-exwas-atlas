# C类自动协变量检索状态与网站标签审核（2026-10-25）

## 元数据快照

基于公开站点 `catalog_c.json`（982条字段元数据，非受访者记录）统计：测量/调查设计元数据625条，自动协变量检索命中290条，来源字段细节62条，明确列作协变量候选5条。另有235条记录的 `Candidate.Status` 仍表示自动关键词发现、尚未完成变量含义与调整资格审核；其中233条 `subcategory` 明确为 keyword discovery only。

这些字段是不同审核维度：值标签或单位已对照官方文件核验，并不代表该字段已经适合或获准纳入某个调整模型。C目录中的自动检索记录不是一组默认协变量，也不是研究团队推荐的调整集；纳入与否需由具体估计目标、问卷路由、时间顺序与因果结构决定。

## 页面标签调整

为避免把“协变量未选定”误读成“连官方字段标签也没有核验”，将筛选/表格中“自动关键词检索线索（未核验协变量）”改为“自动关键词命中（协变量未选定）”，并将子类别说明改为“关键词命中线索；字段定义/协变量资格需分别审核，不是调整建议”。官方原文和逐字段审核状态不变。

本次仅修改页面用语和缓存版本号，不重分类变量或作出任何模型纳入决定；未读取个人数据。

## 2026-10-25 后续字段状态核对

复查发现2018年 `ha025_w4_1_`–`ha025_w4_11_` 共11个房产名册位置字段已有官方问卷/Codebook标签与房产槽位解释，但其C目录仍残留“自动关键词发现、字段含义未审”的旧状态。已将这些字段改列为已审阅的房产上下文元数据，明确不是受访者当前住所或个人协变量；它们不再作为“待审变量含义”的自动关键词项计数。当前982条C记录中，仍有224条的 `Candidate.Status` 为自动发现状态（114个不同字段码）；另有244条 `subcategory` 保留关键词发现提示（121个字段码），这是不同元数据维度，不能互相替代或当作唯一审核计数。其余自动命中仍需逐项核验，不据此形成默认调整集。

随后复核2020 Wave 5核心人口学来源脚本发现，10条2020 C目录记录（9个字段码，`xrage`因来源索引重复出现两条）已做官方定义审核，却共用“age/gender definition”描述；该描述不适用于主观预期寿命的题目阈值`xfagepossibility`或访员观察访谈语言`dc030`。现改为逐字段审核状态，将年龄派生、最终确认性别、性别公式输入/预载、访员性别重编码、寿命题目目标年龄和访谈语言分别说明，并为8条此前仍显示“keyword discovery only”的记录更新中英文子类别。现982条C记录中，`Candidate.Status`仍为通用自动发现状态的有214条（105个字段码）；`subcategory`仍为关键词发现提示的有236条（114个字段码）。两个字段统计口径并不等价；剩余记录继续逐项审核。


## 2026-10-25 follow-up: residential-history and housing context statuses

The 2011–2018 `BB004` residential-history rows were rechecked against the wave-specific official questionnaire and Codebook. Later-wave rows now carry source-reviewed, wave-specific residential-history context status; the 2011 village/community versus county/city source identity conflict remains explicitly on hold. The 2018 property-roster positions, current-residence context, and household mortgage-payment measure now have field-specific source-reviewed C metadata, while route, aggregation, release special values, and eligibility questions remain open. These are not default adjustment recommendations. In the current 982-row C directory, 208 rows (104 field codes) still have generic automated-discovery `Candidate.Status`; 230 rows (111 field codes) retain a `keyword discovery only` subcategory. These are separate review dimensions and neither count is an analysis-ready covariate count. No participant-level values were inspected.


## 2026-10-25 follow-up: alcohol routing metadata statuses

Propagated the existing questionnaire/Codebook review of past-year drinking thresholds (`DA067`/2020 `DA051`), beverage-type selectors (`DA068`), retrospective drinking-history categories (`DA069`), and 2018 prior-wave carry-forward (`ZDA069`) to their exact-wave C directory rows. The statuses retain conditional routes and explicitly avoid treating skips as No/zero or these context fields as default covariates. The updated C directory still has 197 generic automated-discovery Candidate.Status rows (95 field codes) and 219 keyword-discovery subcategory rows (104 field codes), among 982 C rows. The two counts describe separate metadata fields; they are not analysis-ready covariate counts. No participant-level values were inspected.
