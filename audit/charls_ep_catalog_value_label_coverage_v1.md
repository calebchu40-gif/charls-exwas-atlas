# E/P值标签覆盖审计

更新：2026-10-23。由`scripts/summarize_value_label_coverage.py`从当前字段目录和覆盖CSV自动生成。

- E/P字段—角色—类别目录行：6,633；不同波次—字段码：6,552。一条字段可能按多个候选类别/角色出现，均不是独立分析指标。
- 有非空官方/已审标签文本的E/P目录行：3,199；不同波次—字段码：3,173。连续测量、计数值及测量流程字段可以已审但没有类别标签，因此不计入此覆盖数。
- 明确标为`conflict`的E/P字段码：0；详情按主目录波次和变量码检索。
- 问卷/Codebook编码差异尚未调和并锁定`DO NOT ANALYZE`的E/P字段：2011 `fb010`。此项独立于上面的精确`conflict`标签计数。
- 值标签仅说明回答编码，不代表分析资格。题干、跳题、分母、特殊缺失、单位、跨波可比性、权重与方差设计仍须逐项审核。未使用代码本频数或个人记录。

## 按角色和类别汇总（2026-10-23）

|角色|网站类别|字段—角色—类别行（非互斥）|有标签文本行|子类别数|
|---|---|---:|---:|---:|
|e|behavior|243|158|4|
|e|community context|187|59|1|
|e|early-life and family socioeconomic context|3|3|1|
|e|environmental perception|1|1|1|
|e|family and intergenerational context|6|6|1|
|e|food and household environment|160|87|1|
|e|housing and built environment|480|33|2|
|e|social determinants|2,155|915|20|
|e|social protection|1,331|432|30|
|p|anthropometric|15|0|1|
|p|biochemistry|32|0|1|
|p|blood pressure|27|0|1|
|p|chronic disease|248|240|1|
|p|chronic disease ancillary|664|520|70|
|p|cognition|338|305|1|
|p|health and symptoms|161|155|3|
|p|healthcare access|108|15|2|
|p|mental health|50|50|1|
|p|physical function|260|169|7|

## 当前值标签审核状态

|审核状态|E/P目录行|
|---|---:|
|officially reviewed|2,536|
|not yet reviewed|1,668|
|official codebook field located; continuous/count or no categorical labels|608|
|continuous measure metadata available|214|
|official Codebook extraction exposes only a partial response-code set for this field; do not infer omitted categories|200|
|numeric/time unit metadata available; no discrete labels assigned|151|
|official Codebook numeric/count response located; no discrete answer labels|128|
|audited measurement component; derive concept per crosswalk|108|
|Official Codebook response categories reviewed; frequencies and percentages omitted; preserve wave-specific coding|97|
|连续值/字段结构；代码本未提供离散值标签|93|
|official 2018 Codebook response categories transcribed; frequencies omitted; questionnaire route retained; respondent release coding and eligible denominator require validation|68|
|official 2011 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|53|
|official 2013 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|52|
|official 2015 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|52|
|official Codebook lists numeric summary; no categorical response menu in this entry|51|
|official selected-option label; checkbox slot, absence is not a negative response|42|
|代码本逐值标签已核|38|
|continuous component, not a categorical code; component unit reviewed against wave-specific official codebook|38|
|continuous measure metadata available; see description/crosswalk|32|
|连续计数；参照期/机构槽位依波次；极值待核|29|
|continuous raw subtraction response; Codebook extreme maxima occur; valid range and scoring require authorized raw-data QA|25|
|official response categories/unit reviewed; Codebook frequencies omitted|25|
|字段标签已核；代码本呈现多选类别频数，未能从摘录确认未选/否的底层存储码|21|
|official 2020 questionnaire/Codebook response labels reviewed; prior-wave route retained; frequencies excluded|18|
|continuous beverage quantity, not a categorical code; last drinking event in past year; inspect out-of-range/special values and do not convert to ethanol grams without alcohol-strength assumptions|16|
|DO NOT ANALYZE; official 2011 baseline questionnaire option label; selected/unselected/missing value coding not verified; absence is not No|16|
|2020代码本逐字段多选标签已核；条件分母|14|
|official 2013 Codebook response categories transcribed; frequencies omitted; prior-interview recall route retained; release coding and eligible denominator require validation|14|
|official 2018 Codebook response categories transcribed; frequencies omitted; prior-interview recall route retained; release coding and eligible denominator require validation|14|
|official 2015 Codebook response categories transcribed; frequencies omitted; prior-interview recall route retained; release coding and eligible denominator require validation|14|
|candidate; questionnaire and Codebook labels reviewed; validate routes and eligible denominator in approved data|13|
|代码本逐字段值标签已核|12|
|official questionnaire confirms response options; frequencies omitted; self-awareness route retained; release coding and eligible denominator require validation|11|
|official questionnaire checkbox menu and codebook slot coding; frequencies omitted; absence is not a negative response outside the routed checklist|11|
|questionnaire options verified; all offered categories shown, including categories with no Codebook observations; frequencies omitted|11|
|official codebook response labels; prior-wave self-awareness/preload route retained; frequencies excluded|9|
|official Codebook extraction exposes only a partial response-code set; only the correct category is listed; do not infer unlisted codes|9|
|continuous count measure; Codebook identifies 15-second animal-fluency intervals; summary statistics are not valid-range evidence|8|
|official 2011 questionnaire/Codebook threshold categories transcribed; no response frequencies shown|8|
|continuous count, not a categorical code; daily cigarette count; 2020 current and pre-quit values are separate|6|
|official questionnaire categories; frequencies omitted; FC020 multiple-job main-work route or FC021 single nonfarm-job route|6|
|official Codebook response categories transcribed; frequencies omitted; cross-wave question scope and release coding pending|5|
|continuous measure, not a categorical code; nap duration appears in minutes; inspect special/missing codes|5|
|continuous measure, not a categorical code; past-month average sleep hours per night; inspect special/missing codes|5|
|official response categories transcribed; special/missing-code completeness pending|5|
|selected option-code storage confirmed in authorized local table; route/denominator unresolved|5|
|连续计数（夜数）；条件提问；极值待核|4|
|连续计数；条件提问；极值待核|4|
|full questionnaire menu transcribed without frequencies; 2011 codebook omits FL014 and later codebook menus may omit unobserved categories; not-currently-working prior-job route|4|
|local paired endpoint storage and FM011=3 route checked; Codebook extreme upper value retained; do not derive amount|4|
|official 2011 Codebook response categories transcribed; frequencies omitted; self-awareness route retained; release coding and eligible denominator require validation|3|
|official questionnaire confirms DA017 option 14=Testicle; codebook reports no observed categories; no response value label assigned; unselected/storage codes remain unknown; preserve wave-specific selected-slot/missing semantics|3|
|official wave codebook category verified; selected option only; frequencies excluded|3|
|official 2020 Codebook response categories transcribed; frequencies omitted; self-awareness route retained; release coding and eligible denominator require validation|3|
|official 2020 questionnaire response categories; frequencies omitted; conditional work-history transition route|3|
|full official questionnaire response menu transcribed without frequencies; current employer firm route|3|
|continuous monetary amount, not a categorical code; self-reported price for 20 cigarettes at respondent-specific current/pre-quit reference time|3|
|official questionnaire categories transcribed without frequencies; preserve three-category employment/family-business status|3|
|official questionnaire categories; frequencies omitted; 2011 question wording controls its scope|3|
|questionnaire categories and Codebook title conflict recorded; frequencies omitted|3|
|official 2013 Codebook response categories transcribed; frequencies omitted; disease-specific route retained; release coding and eligible denominator require validation|2|
|official questionnaire/codebook categories; frequencies omitted; current employer benefit route|2|
|wave-specific official questionnaire categories transcribed without frequencies; retrospective first-workplace location|2|
|local string endpoint pairs checked; Codebook extreme upper value present; route/unit and sentinel semantics unresolved|2|
|official 2018 Codebook response categories transcribed; frequencies omitted; disease-specific route retained; release coding and eligible denominator require validation|2|
|official 2015 Codebook response categories transcribed; frequencies omitted; disease-specific route retained; release coding and eligible denominator require validation|2|
|official questionnaire confirms DA017 option 2=Oral cavity; codebook reports no observed categories; no response value label assigned; unselected/storage codes remain unknown; preserve wave-specific selected-slot/missing semantics|1|
|official questionnaire confirms DA017 option 21=Non-Hodgkin lymphoma; codebook reports no observed categories; no response value label assigned; unselected/storage codes remain unknown; preserve wave-specific selected-slot/missing semantics|1|
|official questionnaire confirms DA017 option 13=Prostate; codebook reports no observed categories; no response value label assigned; unselected/storage codes remain unknown; preserve wave-specific selected-slot/missing semantics|1|
|问卷类别标签已核；代码本按连续型摘要呈现，发布文件值标签需复核|1|
|DO NOT ANALYZE; questionnaire: 1=Family, 2=Health, 3=School, 4=Unemployment/layoff, 5=Other; Codebook labels retained for reference: 1=Family, 2=Health, 4=School, 5=Unemployment/layoff, 6=Other; released-data coding unresolved|1|
|2020代码本逐值标签已核；疫情期特异|1|
|official questionnaire response categories transcribed without frequencies; continuity of the specific prior-wave work activity|1|
|questionnaire response scale verified; Codebook title conflict retained|1|
|all observed codes verified against official Codebook; unobserved commercial-insurance option left unmapped|1|
|continuous amount; Codebook range available; inspect zero and special values|1|
|official questionnaire categories; frequencies omitted; conditional agricultural-wage/other-job temporary-absence route|1|
