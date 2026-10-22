# 雇用人数与近期求职字段映射复核

更新：2026-10-17。依据CHARLS 2018/2020官方问卷和代码本核对候选就业暴露字段；仅使用公开题目、字段元数据和答案标签，不读取受访者记录或代码本频数。

## 新增目录映射

|候选概念|波次与源字段|题意/单位|边界|
|---|---|---|---|
|非农自营企业/生意规模（雇用/雇员人数）|2018 `fh009_w4`；2020 `fd004`|2018询问公司/生意一般雇用多少人（0–9999人）；2020询问非农自营生意雇用了多少人（0–9999人，明确允许0）|仅适用于自营企业/生意题组。两波措辞略有差异，目录连到同一宽口径候选概念，但不自动视为完全可比；分析前应确认“企业一般雇员数”与“本人雇用数”的口径。|
|过去1个月是否寻找新工作|2020 `ff003`|问卷题目为过去一个月是否找新工作；答案1=Yes、2=No|单波个人自报行为，不等于失业状态。印刷版题目顺序未提供清晰的FF003跳转分母说明；分析前须依据获批发行版确认实际适用人群和有效值。|

## 变量码和波次不可互换

`fd004`在2011、2013、2015和2018官方变量目录中是“工作地点/工作场所位置”；2020同名字段变成“雇用人数”。因此交叉表只将2020 `fd004`映射到企业规模概念，不会把早期四波 `fd004`按同名变量并入。检索时必须用“波次+字段码+概念”，不能只看代码。

## 官方来源与实现

- `sources_official/CHARLS_2018_Questionnaire_extracted.txt`：2018 FH部分的`FH009_W4`（官方问卷约p.198）。
- `sources_official/CHARLS_2018_Codebook_extracted.txt`：`fh009_w4`标签为Number of Employees。
- `sources_official/CHARLS_2020_Questionnaire_English_extracted.txt`：2020 FD非农自营工作`FD004`及FF求职题`FF003`（约pp.65–66）。
- `sources_official/CHARLS_2020_Codebook_extracted.txt`：`fd004` Number of Employees；`ff003` Did You Search for a Job Last Month。只转录答案类别语义，不复制任何频数或比例。

字段映射由`scripts/build_work_exposure_crosswalk.py`生成并纳入`work_exposure_crosswalk_v1.csv`、E/P主crosswalk和`site-prototype/dist/work_exposures_v1.json`。二者是候选目录项；正式关联分析前仍需确认调查路由、缺失值、分母、协变量/权重方案和跨波可比性。
