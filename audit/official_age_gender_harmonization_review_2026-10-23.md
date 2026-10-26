# 年龄与性别核心协变量：官方构造规则复核（2026-10-23）

## 结论

核心协变量表此前已提醒年龄和性别需要复核。本次查到 CHARLS 网站托管的 Gateway to Global Aging Data《Harmonized CHARLS Documentation, Version D (2011–2018)》对前四波年龄、性别构造的明确说明。它提供了可复现的 harmonized 规则，但不是 CHARLS 原始变量说明；不能把其派生变量冒称为CHARLS原始字段。项目应将其作为跨波QA和算法参照，并另行核对CHARLS原始波次字段、2020发行版定义及授权数据中的差异。

## 年龄规则

该Codebook第48–53页说明：

- `RwAGEY`为受访者当波访谈时的年龄年数，依据访谈年/月（`RwIWY`, `RwIWM`）和最近报告的出生年/月（`RABYEAR`, `RABMONTH`）计算；不能只做“访谈年减出生年”。文档所述年龄算法没有使用访谈日或出生日，因此不要将它表述为按具体访谈日精确判定的完整周岁。
- 出生月缺失时按6月处理；Wave 1/2出生年缺失时才回退到当波自报年龄；Wave 3/4不再询问当前年龄，出生年缺失应保留缺失状态，不能沿用早期的自报年龄规则。
- Wave 1/2返访者需核实前次出生日期；Wave 3起记录身份证/户口出生日期，并在与实际出生日期不同时再问实际日期。回答为农历时，出生年月日按CHARLS团队提供的`lunar2solar`程序转换。
- `RABYEAR/RABMONTH/RABDAY`采用最近一次报告的出生日期信息；出生年在未来或等于访谈年、农历转换失败、拒答/不知道等状态有不同特殊缺失码，应保留来源/状态，不可把特殊码当数值年龄。

项目现有2011–2018候选表用Harmonized CHARLS D `RwAGEY`作第三方参照，2020使用释放字段`xrage`。本地汇总覆盖为17,532、18,483、20,998、19,751、19,395；官方 Codebook 中前四波描述统计N为17,533、18,490、20,999、19,751。差异虽小，仍需逐版本和ID匹配核验，当前候选不能直接视为最终年龄字段。2020本地`xrage`覆盖与Wave 5 Codebook总表一致，但其跨模块分表N不同；统一表按19,395，说明对照时必须匹配正确文件和模块。

下一步实现前置条件：明确每波原始分析表中的访谈日期、出生年月日、历法标记和纠错/预载字段；确认CHARLS团队提供的`lunar2solar`程序版本与许可/来源；用合成日期测试生日在访谈日前后、缺出生月、无效/未来出生日期、农历闰月和转换失败；随后将私有逐人派生年龄与`RwAGEY`按ID比较，只公开聚合差异QA。不得以第三方H-CHARLS值静默覆盖原始构造或把个体出生日期上传到网站/GitHub。

数据输入清点显示，当前私有`person_analytic.dta`准备表在2011、2013波没有`iyear/imonth`，而项目原始字段目录将它们定位在`weight`与`Weights`模块；2015、2018、2020准备表含`iyear/imonth`。因此不能用现有2011/2013年龄表直接精确复算`RwAGEY`。待取得/恢复相应非个人发布辅助文件后，按唯一受访者ID做本地受控连接；在此之前保留Harmonized年龄作为第三方比较值，避免粗略年差替代。该字段来源和缺口也应写入模型就绪状态。

### 2020官方派生年龄公式已确认

进一步逐行核对CHARLS 2020英文问卷的“Auxiliary Variable Definition”（`XRAge`段）后，Wave 5规则已从“定义待查”更新为已知：若`ZRBirthYear`缺失或`XRType=2`（新访），则`XRAge = 2020 - BA003_1`；若`XRType=1`（返访）且`ZRBirthYear`非缺失，则`XRAge = 2020 - ZRBirthYear`。`BA003_1`是受访者按阳历报告的实际出生年份。该算法是固定调查年减出生年，不按访谈月份/日精算周岁；不应误写成Harmonized CHARLS `RwAGEY`的访谈年月算法。它是CHARLS官方CAPI派生字段，但用于本项目时仍需核验发行版、目标样本与缺失/特殊值，不能仅凭存在就纳入全部模型。

2020 Codebook全样本概要将`xrage`列为19,395个观察值，模块变量详情部分又列出19,367；因此覆盖核验必须对应实际源文件/版本及字段文件，不能把不同表格的Obs简单视作矛盾后自行改写。当前私有整合表`xrage`非空19,395仅是本地版本QA，需在源模块和样本标记确认后才可用于分析覆盖。

## 性别规则

该Codebook第54–56页说明：Wave 1人口学模块的性别作为当波构造值；Wave 2–4人口学与健康模块可能不一致，跨波也可能出现更改。`RAGENDER`依照最一致的报告确定性别，`RAFGENDR`记录采用人口学众数、健康/居住模块众数或首个非缺失报告的情形。因此，`xrgender`不能在没有冲突QA和标记的情况下被视为完整的统一构造。

2020英文问卷的辅助变量定义现已明确给出`XRGender`构造：若`ZRGender`非缺失且与访员记录`BA001`一致，取`BA001`；若两者不同，取受访者再次确认的`BA002`；若`ZRGender`缺失，取`BA001`。问卷将`BA001`和`BA002`编码为`1=Male; 2=Female`；`XR20Gender`是`BA001`的字符串重编码，`XR18Gender`由`ZRGender`重编码。因此这些字段不是六个独立性别测量：`BA001`、`BA002`、`ZRGender`为构造输入，`XR20Gender`/`XR18Gender`为辅助中间值，`XRGender`才是该轮按问卷逻辑确认的派生候选。该公式不等于Harmonized CHARLS `RAGENDER/RAFGENDR`前四波“跨模块最一致报告”算法，项目不能直接宣称完全跨波同定义。Wave 5样本中准备表的汇总分歧QA仍保留作发行版/整合检查，不替代官方公式。

已将2020年龄/性别字段逐项更新到候选目录元数据：为`xrage`标注固定年差及新访/返访来源；为性别字段分别标注当前访员记录、条件确认、前波预载或字符串派生角色，并转录官方类别标签（不含频数）。所有字段继续是C类元数据/协变量候选，目录明确提示不可自动作为调整集。实现脚本为`scripts/apply_wave5_core_demographic_review.py`，回归测试为`tests/test_wave5_core_demographic_review.py`。

对本机受控准备数据只作内存聚合比较：`ba000_w2_3`访员记录与`xrgender`在2013/2015/2018的共同非缺失分别为18,409/20,632/19,816，分歧分别为125/19/0；2020 `ba001`与`xrgender`共同非缺失19,395，分歧少于10，故按项目规则抑制。2020 `zrgender`与`xrgender`共同非缺失19,242、分歧36；当轮`ba002`与`xrgender`共同非缺失43且在该重叠子集一致。2020 `xr18gender`/`xr20gender`与`xrgender`在本准备表中没有共同非缺失值，不可据此推定等价或冲突。上述是内部变量质量QA摘要，未导出ID或个体记录，也不代表官方确定的优先级。官方公式已核实；仍需按授权发行版核对准备表中的`XRGender`是否按该公式生成，并只发布聚合差异QA。

## 官方来源

- Gateway to Global Aging Data，[Harmonized CHARLS Documentation Version D（CHARLS网站托管PDF）](https://charls.pku.edu.cn/en/team/Codebook.pdf)，Section A “Demographics and Identifiers”，年龄pp.48–53、性别pp.54–56；文档封面标注Version D (2011–2018), June 2021，前言说明Harmonized CHARLS由USC Gateway团队制作。访问日期：2026-10-23。
- Gateway to Global Aging Data，[Harmonized CHARLS Creation Code说明](https://g2aging.org/harmonized-charls/creation-code)，说明Version D.2需要Wave 1–4及2014 Life History文件，并使用CHARLS GitHub上的`lunar2solar.mmat`。
- CHARLS，[2020 Wave 5官方英文问卷PDF](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_Questionnaire_English.pdf)，`Auxiliary Variable Definition`中的`XRGender`、`XR20Gender`、`XR18Gender`与`XRAge`算法；`BA001/BA002/BA003_1`问卷题及官方编码。访问日期：2026-10-24。
- CHARLS团队维护的[Chinese lunar to solar date transformation代码库](https://github.com/charls-data/lunar2solar)，说明Stata安装文件包含`.ado`、`.mmat`、`.sthlp`。已固定到2026-10-27核验的提交`2284ccffdd74f057c234a446585ec32034b2d50d`，并记录三件套SHA-256、MIT许可、闰月调用要求及本机无Stata执行环境的限制；详见[`charls_lunar2solar_pinned_reference_2026-10-27.md`](charls_lunar2solar_pinned_reference_2026-10-27.md)。固定代码版本不等于已执行验证，也不替代逐波原始出生日期字段/路由核验。
- Harmonized CHARLS Codebook要求在使用其数据或Codebook信息的书面分析中致谢Gateway团队；若后续论文实际使用Harmonized CHARLS数据或其信息，应按原文添加致谢并遵循其当前说明。项目当前只是方法和QA参照，没有自动向外发送邮件。
- 项目本地逐波问卷与Codebook仍是原始字段、问卷路由和值编码的优先证据；上述Harmonized Codebook负责说明其汇总变量的构造，而不是替代每波问卷。

