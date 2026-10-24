# E/P值标签覆盖审计

更新：2026-10-24。由`scripts/summarize_value_label_coverage.py`读取最终网站角色分片`catalog_e.json`、`catalog_p.json`和`catalog_c.json`生成；不读取早期中间字段表。

- 最终E/P目录行：6,843；不同波次—字段码：6,568。一个字段可对应多个候选类别/角色。
- 有非空标签文本的E/P目录行：3,397；不同波次—字段码：3,320。连续测量、计数值及测量流程字段可已审但不需要离散标签。
- 最终E/P中精确状态为`not yet reviewed`的目录行：0；C目录对应行：171。具体来源审查状态不等同于通用待审。
- 明确标为`conflict`的E/P字段码：0；问卷/Codebook差异仍锁定`DO NOT ANALYZE`的字段：2011 `fb010`。
- 值标签仅说明回答编码，不代表分析资格。题干、跳题、分母、特殊缺失、单位、跨波可比性、权重与方差设计仍须逐项审核。未使用代码本频数或个人记录。

## 按角色和类别汇总（2026-10-24）

|角色|网站类别|字段—角色—类别行|不同波次—字段码|有非空标签文本行|子类别数|
|---|---|---:|---:|---:|---:|
|e|behavior|267|267|184|5|
|e|behavioral exposures|2|2|0|1|
|e|community context|198|198|69|1|
|e|early-life and family socioeconomic context|3|3|3|1|
|e|environmental perception|1|1|1|1|
|e|family and intergenerational context|6|3|6|1|
|e|food and household environment|161|161|104|1|
|e|healthcare access|109|109|51|1|
|e|housing and built environment|480|480|40|2|
|e|internal biomarker|49|49|0|1|
|e|social determinants|2,132|2,132|1,007|20|
|e|social protection|1,331|1,331|426|30|
|p|anthropometric|24|15|0|1|
|p|biochemistry|32|32|0|1|
|p|blood pressure|54|27|0|1|
|p|chronic disease|248|248|240|1|
|p|chronic disease ancillary|664|664|520|70|
|p|cognition|338|338|305|1|
|p|health and symptoms|162|162|156|4|
|p|healthcare access|217|217|66|2|
|p|internal biomarker|49|49|0|1|
|p|mental health|50|50|50|1|
|p|physical function|266|260|169|7|

## 当前值标签审核状态

|审核状态|最终E/P目录行|
|---|---:|
|officially reviewed|2,612|
|official codebook field located; continuous/count or no categorical labels|727|
|numeric/time unit metadata available; no discrete labels assigned; see concept crosswalk|516|
|codebook field located; continuous/open response or no categorical labels|371|
|continuous measure metadata available|257|
|official Codebook extraction exposes only a partial response-code set for this field; do not infer omitted categories|208|
|numeric/time unit metadata available; no discrete labels assigned|151|
|audited measurement component; derive concept per crosswalk|138|
|official Codebook numeric/count response located; no discrete answer labels|129|
|Official Codebook response categories reviewed; frequencies and percentages omitted; preserve wave-specific coding|96|
|连续值/字段结构；代码本未提供离散值标签|93|
|official 2011 questionnaire identifies Yuan amount period and household-member roster slot; continuous amount with no discrete response categories; authorized-release storage scale and special values remain unverified|80|
|代码本逐值标签已核|76|
|official 2018 Codebook response categories transcribed; frequencies omitted; questionnaire route retained; respondent release coding and eligible denominator require validation|68|
|连续计数；参照期/机构槽位依波次；极值待核|58|
|official 2011 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|53|
|official Codebook lists numeric summary; no categorical response menu in this entry|52|
|official 2013 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|52|
|official 2015 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|52|
|字段标签已核；代码本呈现多选类别频数，未能从摘录确认未选/否的底层存储码|42|
|official selected-option label; checkbox slot, absence is not a negative response|42|
|official Codebook identifies selected activity/device option; respondent-level storage is unresolved; unselected state and eligible denominator are unresolved; no response-value labels assigned|41|
|continuous component, not a categorical code; component unit reviewed against wave-specific official codebook|32|
|continuous measure metadata available; see description/crosswalk|32|
|official questionnaire and Codebook option identity reviewed; participant-level No/unselected storage and denominator unresolved; no response-value labels assigned|30|
|official wave-specific Codebook response categories transcribed without frequencies; complete listed 1-10 set; ordered frequency categories are not equally spaced; preserve parent/spouse route and indexed roster; special missing and nonresponse semantics remain release-specific|27|
|Official questionnaire identifies a numeric monetary amount; continuous monetary amount; questionnaire reporting unit 10,000 Yuan; no discrete category labels assigned; release storage and special codes remain unverified.|27|
|official response categories/unit reviewed; Codebook frequencies omitted|25|
|continuous raw subtraction response; Codebook extreme maxima occur; valid range and scoring require authorized raw-data QA|25|
|代码本逐字段值标签已核|24|
|official 2013 questionnaire identifies Yuan amount period and household-member roster slot; continuous amount with no discrete response categories; authorized-release storage scale and special values remain unverified|24|
|official 2015 questionnaire identifies Yuan amount period and household-member roster slot; continuous amount with no discrete response categories; authorized-release storage scale and special values remain unverified|20|
|official questionnaire/Codebook response categories reviewed; frequencies omitted; option-specific Yes code verified|20|
|official 2020 questionnaire/Codebook response labels reviewed; prior-wave route retained; frequencies excluded|18|
|continuous beverage quantity, not a categorical code; last drinking event in past year; inspect out-of-range/special values and do not convert to ethanol grams without alcohol-strength assumptions|16|
|DO NOT ANALYZE; official 2011 baseline questionnaire option label; selected/unselected/missing value coding not verified; absence is not No|16|
|official 2018 questionnaire and Codebook identify continuous household expenditure; no discrete response categories|16|
|2020 official questionnaire and Codebook wording/response categories reviewed; frequencies excluded; routed missingness retained|15|
|continuous conditional component; unit and route reviewed; no response-category labels; codebook frequencies omitted|14|
|official 2011 questionnaire and Codebook identify continuous household expenditure; no discrete response categories|14|
|2020代码本逐字段多选标签已核；条件分母|14|
|official 2013 Codebook response categories transcribed; frequencies omitted; prior-interview recall route retained; release coding and eligible denominator require validation|14|
|official 2018 Codebook response categories transcribed; frequencies omitted; prior-interview recall route retained; release coding and eligible denominator require validation|14|
|official 2015 Codebook response categories transcribed; frequencies omitted; prior-interview recall route retained; release coding and eligible denominator require validation|14|
|candidate; questionnaire and Codebook labels reviewed; validate routes and eligible denominator in approved data|13|
|official 2020 questionnaire and Codebook identify continuous household expenditure; no discrete response categories|13|
|official questionnaire/Codebook identify a pension bracket endpoint; no discrete response categories|12|
|occupation/industry classification code; not a numeric scale or response menu; use the matching official classification lookup; Codebook frequencies omitted|12|
|continuous timed measurement; seconds and non-completion status codes reviewed from official instruments; no categorical response labels or Codebook summaries copied|12|
|official questionnaire checkbox menu and codebook slot coding; frequencies omitted; absence is not a negative response outside the routed checklist|11|
|official Codebook identifies affirmative caregiver-option code; unselected coding and eligible denominator unresolved; no response-value labels assigned|11|
|questionnaire options verified; all offered categories shown, including categories with no Codebook observations; frequencies omitted|11|
|official questionnaire confirms response options; frequencies omitted; self-awareness route retained; release coding and eligible denominator require validation|11|
|official Codebook identifies affirmative inheritance-source option; unselected storage and denominator unresolved; no response-value labels assigned|10|
|Official questionnaire identifies a numeric monetary amount; continuous monetary amount; questionnaire reporting unit 1,000 Yuan/square metre; no discrete category labels assigned; release storage and special codes remain unverified.|10|
|official questionnaire/Codebook field reviewed; continuous amount/count, no categorical response labels; preserve unit and route|9|
|official codebook response labels; prior-wave self-awareness/preload route retained; frequencies excluded|9|
|official Codebook extraction exposes only a partial response-code set; only the correct category is listed; do not infer unlisted codes|9|
|连续计数；条件提问；极值待核|8|
|连续计数（夜数）；条件提问；极值待核|8|
|official 2011 questionnaire/Codebook threshold categories transcribed; no response frequencies shown|8|
|continuous count measure; Codebook identifies 15-second animal-fluency intervals; summary statistics are not valid-range evidence|8|
|official 2018 questionnaire and Codebook identify total property value; continuous amount in 10,000 Yuan; no discrete labels|7|
|official 2018 questionnaire/Codebook categories reviewed for the slot-specific house-for-rent item|7|
|official 2018 questionnaire identifies estimated market rent per month for an indexed house property; continuous Yuan/month amount, no discrete labels|7|
|official questionnaire measurement/range note; continuous or count response, not categorical answer labels; route and special-value handling require release-level review|7|
|official wave-specific Codebook response categories transcribed without frequencies; partial Codebook category set; unlisted categories not inferred; ordered frequency categories are not equally spaced; preserve parent/spouse route and indexed roster; special missing and nonresponse semantics remain release-specific|6|
|official 2018 questionnaire identifies actual monthly rent for an indexed house property; continuous Yuan/month amount, no discrete labels|6|
|continuous count, not a categorical code; daily cigarette count; 2020 current and pre-quit values are separate|6|
|official 2020 questionnaire CAPI formula manually transcribed; descriptive codebook frequencies omitted; generated-field interpretation requires route validation|6|
|official questionnaire categories; frequencies omitted; FC020 multiple-job main-work route or FC021 single nonfarm-job route|6|
|official questionnaire numbered fallback categories; Codebook category labels checked and frequencies omitted; asked only when exact percentage is unknown; preserve separately from paired continuous percentage and verify released-data routing|6|
|official 2018 questionnaire confirms continuous percentage share; no discrete labels; Codebook summary extrema are not valid-range evidence; verify route and special values|5|
|official 2018 questionnaire and Codebook identify unit-area property value; continuous amount in 1,000 Yuan/square metre; no discrete labels|5|
|official Codebook response categories transcribed; frequencies omitted; cross-wave question scope and release coding pending|5|
|continuous measure, not a categorical code; nap duration appears in minutes; inspect special/missing codes|5|
|continuous measure, not a categorical code; past-month average sleep hours per night; inspect special/missing codes|5|
|selected option-code storage confirmed in authorized local table; route/denominator unresolved|5|
|official response categories transcribed; special/missing-code completeness pending|5|
|official Codebook response categories reviewed; frequencies and percentages omitted|4|
|full questionnaire menu transcribed without frequencies; 2011 codebook omits FL014 and later codebook menus may omit unobserved categories; not-currently-working prior-job route|4|
|local paired endpoint storage and FM011=3 route checked; Codebook extreme upper value retained; do not derive amount|4|
|official questionnaire option wording only; released numeric value codes not verified; DO NOT ANALYZE until reconciled to authorized release|4|
|Official questionnaire identifies a numeric monetary amount; continuous monetary amount; questionnaire reporting unit Yuan; no discrete category labels assigned; release storage and special codes remain unverified.|3|
|official 2015 questionnaire and Codebook identify continuous household expenditure; no discrete response categories|3|
|official 2013 questionnaire and Codebook identify continuous household expenditure; no discrete response categories|3|
|official 2020 questionnaire response categories; frequencies omitted; conditional work-history transition route|3|
|full official questionnaire response menu transcribed without frequencies; current employer firm route|3|
|continuous monetary amount, not a categorical code; self-reported price for 20 cigarettes at respondent-specific current/pre-quit reference time|3|
|official questionnaire categories transcribed without frequencies; preserve three-category employment/family-business status|3|
|official questionnaire categories; frequencies omitted; 2011 question wording controls its scope|3|
|questionnaire categories and Codebook title conflict recorded; frequencies omitted|3|
|official 2011 Codebook response categories transcribed; frequencies omitted; self-awareness route retained; release coding and eligible denominator require validation|3|
|official questionnaire confirms DA017 option 14=Testicle; codebook reports no observed categories; no response value label assigned; unselected/storage codes remain unknown; preserve wave-specific selected-slot/missing semantics|3|
|official 2020 Codebook response categories transcribed; frequencies omitted; self-awareness route retained; release coding and eligible denominator require validation|3|
|official wave codebook category verified; selected option only; frequencies excluded|3|
|问卷类别标签已核；代码本按连续型摘要呈现，发布文件值标签需复核|2|
|official 2018 questionnaire identifies continuous numeric measure (square metres); no discrete labels; Codebook summary extrema are not valid-range evidence; verify special values and route|2|
|source conflict recorded; do not display a reconciled unit or categories|2|
|official 2013 questionnaire/Codebook category wording reviewed; preserve wave-specific storage representation|2|
|official 2011 questionnaire/Codebook category wording reviewed; preserve wave-specific storage representation|2|
|official 2015 questionnaire/Codebook category wording reviewed; preserve wave-specific storage representation|2|
|official 2020 questionnaire identifies a past-week household Yuan amount; continuous measure with no discrete labels; check release-specific special values|2|
|official 2018 questionnaire identifies a past-week household Yuan amount; continuous measure with no discrete labels; check release-specific special values|2|
|official 2015 questionnaire identifies a past-week household Yuan amount; continuous measure with no discrete labels; check release-specific special values|2|
|official 2013 questionnaire identifies a past-week household Yuan amount; continuous measure with no discrete labels; check release-specific special values|2|
|official 2011 questionnaire identifies a past-week household Yuan amount; continuous measure with no discrete labels; check release-specific special values|2|
|official 2018 questionnaire identifies continuous numeric measure (10,000 Yuan); no discrete labels; Codebook summary extrema are not valid-range evidence; verify special values and route|2|
|official 2018 questionnaire identifies continuous numeric measure (Yuan/month); no discrete labels; Codebook summary extrema are not valid-range evidence; verify special values and route|2|
|questionnaire/Codebook item-identity conflict; DO NOT ANALYZE until official source identity and released-data coding are reconciled|2|
|continuous date component; preserve year/month unit and conditional prior-status correction route; month -1 indicates unable to report; DO NOT ANALYZE pending route and released-data reconciliation|2|
|official questionnaire/codebook categories; frequencies omitted; current employer benefit route|2|
|wave-specific official questionnaire categories transcribed without frequencies; retrospective first-workplace location|2|
|local string endpoint pairs checked; Codebook extreme upper value present; route/unit and sentinel semantics unresolved|2|
|occupation classification code; Codebook frequency distribution omitted; classification definitions are not response labels; unpaid family-business route retained|2|
|official questionnaire/Codebook identify a conditional bracket endpoint; Codebook provides numeric summaries but no discrete response categories|2|
|official questionnaire/Codebook identify a conditional bracket endpoint; Codebook explicitly says string; no discrete response categories|2|
|official 2013 Codebook response categories transcribed; frequencies omitted; disease-specific route retained; release coding and eligible denominator require validation|2|
|official 2018 Codebook response categories transcribed; frequencies omitted; disease-specific route retained; release coding and eligible denominator require validation|2|
|official 2015 Codebook response categories transcribed; frequencies omitted; disease-specific route retained; release coding and eligible denominator require validation|2|
|official 2020 questionnaire identifies a numeric underground floor number; continuous/ordinal measure without discrete value labels|1|
|official 2020 questionnaire identifies a numeric above-ground floor number; continuous/ordinal measure without discrete value labels|1|
|official 2020 questionnaire identifies a wave-specific categorical above-ground versus underground residence selector; preserve alongside routed count fields|1|
|official 2018 questionnaire identifies a numeric building floor number; continuous/ordinal measure without discrete value labels|1|
|official 2015 questionnaire identifies a numeric building floor number; continuous/ordinal measure without discrete value labels|1|
|official 2013 questionnaire identifies a numeric building floor number; continuous/ordinal measure without discrete value labels|1|
|official 2011 questionnaire identifies a numeric building floor number; continuous/ordinal measure without discrete value labels|1|
|official 2020 questionnaire identifies a numeric steps to main entrance; continuous/ordinal measure without discrete value labels|1|
|official 2013 questionnaire identifies continuous numeric calendar year measure; no discrete labels; Codebook extrema are not valid-range evidence; verify release special values and eligibility|1|
|official 2011 questionnaire identifies continuous numeric calendar year measure; no discrete labels; Codebook extrema are not valid-range evidence; verify release special values and eligibility|1|
|official 2015 questionnaire identifies continuous numeric calendar year measure; no discrete labels; Codebook extrema are not valid-range evidence; verify release special values and eligibility|1|
|official 2018 questionnaire identifies continuous numeric calendar year measure; no discrete labels; Codebook extrema are not valid-range evidence; verify release special values and eligibility|1|
|official 2020 questionnaire and Codebook identify a numeric living-room count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2018 questionnaire and Codebook identify a numeric living-room count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2015 questionnaire and Codebook identify a numeric living-room count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2013 questionnaire and Codebook identify a numeric living-room count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2011 questionnaire and Codebook identify a numeric living-room count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2020 questionnaire and Codebook identify a numeric bedroom count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2018 questionnaire and Codebook identify a numeric bedroom count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2013 questionnaire and Codebook identify a numeric bedroom count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2011 questionnaire and Codebook identify a numeric bedroom count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2020 questionnaire identifies continuous numeric square metres measure; no discrete labels; Codebook extrema are not valid-range evidence; verify release special values and eligibility|1|
|official 2013 questionnaire identifies continuous numeric square metres measure; no discrete labels; Codebook extrema are not valid-range evidence; verify release special values and eligibility|1|
|official 2011 questionnaire identifies continuous numeric square metres measure; no discrete labels; Codebook extrema are not valid-range evidence; verify release special values and eligibility|1|
|official 2020 questionnaire identifies respondent move-in calendar year; no discrete labels; questionnaire -1 unknown code requires authorized-release validation|1|
|official 2015 questionnaire and Codebook identify a numeric bedroom count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2015 questionnaire/Codebook review: numeric distance in meters, no discrete labels|1|
|official 2015 questionnaire and Codebook identify a numeric toilet count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2013 questionnaire/Codebook review: numeric distance in meters, no discrete labels|1|
|official 2013 questionnaire and Codebook identify a numeric toilet count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2011 questionnaire/Codebook review: numeric distance in meters, no discrete labels|1|
|official 2011 questionnaire and Codebook identify a numeric toilet count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2020 questionnaire identifies primary food purchaser through wave-specific household roster/other-person selector; dynamic identity choices are not fixed value labels|1|
|official 2020 questionnaire and Codebook identify respondent-as-primary-food-purchaser Yes/No; household-role item, not a dietary measure|1|
|official 2018 questionnaire identifies primary food purchaser through wave-specific household roster/other-person selector; dynamic identity choices are not fixed value labels|1|
|official 2018 questionnaire and Codebook identify respondent-as-primary-food-purchaser Yes/No; household-role item, not a dietary measure|1|
|official 2015 questionnaire identifies primary food purchaser through wave-specific household roster/other-person selector; dynamic identity choices are not fixed value labels|1|
|official 2015 questionnaire and Codebook identify respondent-as-primary-food-purchaser Yes/No; household-role item, not a dietary measure|1|
|official 2013 questionnaire identifies primary food purchaser through wave-specific household roster/other-person selector; dynamic identity choices are not fixed value labels|1|
|official 2018 questionnaire and Codebook identify a numeric toilet count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2013 questionnaire and Codebook identify respondent-as-primary-food-purchaser Yes/No; household-role item, not a dietary measure|1|
|official 2020 questionnaire/Codebook category wording reviewed; preserve wave-specific storage representation|1|
|official 2020 questionnaire/Codebook review: numeric distance in meters, no discrete labels|1|
|official 2020 questionnaire and Codebook identify a numeric toilet count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values|1|
|official 2018 questionnaire/Codebook category wording reviewed; preserve wave-specific storage representation|1|
|official 2018 questionnaire/Codebook review: numeric distance in meters, no discrete labels|1|
|official 2011 questionnaire identifies primary food purchaser through wave-specific household roster/other-person selector; dynamic identity choices are not fixed value labels|1|
|official 2011 questionnaire and Codebook identify respondent-as-primary-food-purchaser Yes/No; household-role item, not a dietary measure|1|
|official 2020 questionnaire identifies a numeric household person count; continuous count measure, no discrete category labels|1|
|official 2018 questionnaire identifies a numeric household person count; continuous count measure, no discrete category labels|1|
|official 2015 questionnaire identifies a numeric household person count; continuous count measure, no discrete category labels|1|
|official 2013 questionnaire identifies a numeric household person count; continuous count measure, no discrete category labels|1|
|official 2011 questionnaire identifies a numeric household person count; continuous count measure, no discrete category labels|1|
|official 2013 questionnaire/Codebook labels reviewed; six ordered self-reported usual meals-per-day categories|1|
|official 2011 questionnaire/Codebook labels reviewed; six ordered self-reported usual meals-per-day categories|1|
|official 2018 questionnaire identifies continuous numeric measure (calendar year); no discrete labels; Codebook summary extrema are not valid-range evidence; verify special values and route|1|
|official 2018 questionnaire identifies continuous numeric measure (1,000 Yuan/square metre); no discrete labels; Codebook summary extrema are not valid-range evidence; verify special values and route|1|
|official Codebook response labels complete; frequency counts omitted|1|
|official 2018 questionnaire identifies current-residence homestead land area in square meters; numeric continuous measure with no discrete value labels|1|
|official 2018 questionnaire and Codebook response categories reviewed; preserve Codebook labels; questionnaire wording differs slightly; confirm route and special values in release|1|
|official 2018 questionnaire identifies a numeric household-residence balcony count; continuous count, no discrete category labels|1|
|official 2018 questionnaire identifies a numeric household-residence kitchen count; continuous count, no discrete category labels|1|
|DO NOT ANALYZE; questionnaire: 1=Family, 2=Health, 3=School, 4=Unemployment/layoff, 5=Other; Codebook labels retained for reference: 1=Family, 2=Health, 4=School, 5=Unemployment/layoff, 6=Other; released-data coding unresolved|1|
|official 2011 questionnaire identifies a numeric household-residence balcony count; continuous count, no discrete category labels|1|
|official 2011 questionnaire identifies a numeric household-residence kitchen count; continuous count, no discrete category labels|1|
|official 2011 questionnaire identifies current-residence homestead land area in square meters; numeric continuous measure with no discrete value labels|1|
|official 2013 questionnaire identifies a numeric household-residence balcony count; continuous count, no discrete category labels|1|
|official 2013 questionnaire identifies a numeric household-residence kitchen count; continuous count, no discrete category labels|1|
|official 2013 questionnaire identifies current-residence homestead land area in square meters; numeric continuous measure with no discrete value labels|1|
|questionnaire/Codebook option identity conflict; DO NOT ANALYZE; no response-value labels assigned|1|
|official Codebook response labels transcribed; frequencies omitted; retain DO NOT ANALYZE lock pending none-option validation|1|
|official 2018 questionnaire identifies a numeric count of house properties titled to the main respondent and spouse; route-specific household property count|1|
|official 2015 questionnaire identifies a numeric household-residence balcony count; continuous count, no discrete category labels|1|
|official 2015 questionnaire identifies a numeric household-residence kitchen count; continuous count, no discrete category labels|1|
|official 2015 questionnaire identifies current-residence homestead land area in square meters; numeric continuous measure with no discrete value labels|1|
|official questionnaire response categories transcribed without frequencies; continuity of the specific prior-wave work activity|1|
|official Codebook field located; continuous job count; no categorical response labels; interwave route retained|1|
|future-helper route and category reviewed; unselected coding and eligible denominator unresolved; no response-value labels assigned|1|
|Codebook summary reports one observation; continuous count, no categorical labels; days measure and route retained|1|
|official questionnaire identifies caregiver option; Codebook reports no observations; unselected coding and eligible denominator unresolved; no response-value labels assigned|1|
|continuous amount; Codebook range available; inspect zero and special values|1|
|all observed codes verified against official Codebook; unobserved commercial-insurance option left unmapped|1|
|numbered official questionnaire categories; released-data value coding and no-fixed-address storage unverified; DO NOT ANALYZE pending reconciliation|1|
|official questionnaire answer wording; released numeric value codes not verified; DO NOT ANALYZE until reconciled to authorized release|1|
|official questionnaire categories; frequencies omitted; conditional agricultural-wage/other-job temporary-absence route|1|
|official questionnaire confirms DA017 option 2=Oral cavity; codebook reports no observed categories; no response value label assigned; unselected/storage codes remain unknown; preserve wave-specific selected-slot/missing semantics|1|
|official questionnaire confirms DA017 option 13=Prostate; codebook reports no observed categories; no response value label assigned; unselected/storage codes remain unknown; preserve wave-specific selected-slot/missing semantics|1|
|official questionnaire confirms DA017 option 21=Non-Hodgkin lymphoma; codebook reports no observed categories; no response value label assigned; unselected/storage codes remain unknown; preserve wave-specific selected-slot/missing semantics|1|
|2020代码本逐值标签已核；疫情期特异|1|
|questionnaire response scale verified; Codebook title conflict retained|1|
|2020 official questionnaire and Codebook ordinal categories reviewed; frequencies excluded; interpretation depends on the respondent-specific target age|1|

覆盖CSV与本报告均按最终网站角色分片重算；各类别可非互斥，不能将行数或类别数解释为独立测量指标、分析资格、样本量或关联结果。
