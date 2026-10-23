# 年龄与性别核心协变量：官方构造规则复核（2026-10-23）

## 结论

核心协变量表此前已提醒年龄和性别需要复核。本次查到 CHARLS 网站托管的 Gateway to Global Aging Data《Harmonized CHARLS Documentation, Version D (2011–2018)》对前四波年龄、性别构造的明确说明。它提供了可复现的 harmonized 规则，但不是 CHARLS 原始变量说明；不能把其派生变量冒称为CHARLS原始字段。项目应将其作为跨波QA和算法参照，并另行核对CHARLS原始波次字段、2020发行版定义及授权数据中的差异。

## 年龄规则

该Codebook第48–53页说明：

- `RwAGEY`为受访者当波访谈时的整岁年龄，依据访谈年/月（`RwIWY`, `RwIWM`）和最近报告的出生年/月（`RABYEAR`, `RABMONTH`）计算；不能只做“访谈年减出生年”。
- 出生月缺失时按6月处理；Wave 1/2出生年缺失时才回退到当波自报年龄；Wave 3/4不再询问当前年龄，出生年缺失应保留缺失状态，不能沿用早期的自报年龄规则。
- Wave 1/2返访者需核实前次出生日期；Wave 3起记录身份证/户口出生日期，并在与实际出生日期不同时再问实际日期。回答为农历时，出生年月日按CHARLS团队提供的`lunar2solar`程序转换。
- `RABYEAR/RABMONTH/RABDAY`采用最近一次报告的出生日期信息；出生年在未来或等于访谈年、农历转换失败、拒答/不知道等状态有不同特殊缺失码，应保留来源/状态，不可把特殊码当数值年龄。

项目现有2011–2018候选表用Harmonized CHARLS D `RwAGEY`作第三方参照，2020使用释放字段`xrage`。本地汇总覆盖为17,532、18,483、20,998、19,751、19,395；官方 Codebook 中前四波描述统计N为17,533、18,490、20,999、19,751。差异虽小，仍需逐版本和ID匹配核验，当前候选不能直接视为最终年龄字段。2020本地`xrage`覆盖与Wave 5 Codebook总表一致，但其跨模块分表N不同；统一表按19,395，说明对照时必须匹配正确文件和模块。

下一步实现前置条件：明确每波原始分析表中的访谈日期、出生年月日、历法标记和纠错/预载字段；确认CHARLS团队提供的`lunar2solar`程序版本与许可/来源；用合成日期测试生日在访谈日前后、缺出生月、无效/未来出生日期、农历闰月和转换失败；随后将私有逐人派生年龄与`RwAGEY`按ID比较，只公开聚合差异QA。不得以第三方H-CHARLS值静默覆盖原始构造或把个体出生日期上传到网站/GitHub。

## 性别规则

该Codebook第54–56页说明：Wave 1人口学模块的性别作为当波构造值；Wave 2–4人口学与健康模块可能不一致，跨波也可能出现更改。`RAGENDER`依照最一致的报告确定性别，`RAFGENDR`记录采用人口学众数、健康/居住模块众数或首个非缺失报告的情形。因此，`xrgender`不能在没有冲突QA和标记的情况下被视为完整的统一构造。

2020 Codebook中`xrgender`全样本存在，但本次审阅到的说明尚未建立它与前四波`RAGENDER/RAFGENDR`完全同定义。2020人口学模块还出现`zrgender`、`xr20gender`、`xr18gender`和当轮确认/访员记录等字段。先按波次整理字段与Codebook定义、比较冲突聚合数并标注构造来源，再决定M1使用的字段。公开目录不展示个人性别或身份冲突记录。

## 官方来源

- Gateway to Global Aging Data，[Harmonized CHARLS Documentation Version D（CHARLS网站托管PDF）](https://charls.pku.edu.cn/en/team/Codebook.pdf)，Section A “Demographics and Identifiers”，年龄pp.48–53、性别pp.54–56；文档封面标注Version D (2011–2018), June 2021，前言说明Harmonized CHARLS由USC Gateway团队制作。访问日期：2026-10-23。
- Gateway to Global Aging Data，[Harmonized CHARLS Creation Code说明](https://g2aging.org/harmonized-charls/creation-code)，说明Version D.2需要Wave 1–4及2014 Life History文件，并使用CHARLS GitHub上的`lunar2solar.mmat`。
- CHARLS团队维护的[Chinese lunar to solar date transformation代码库](https://github.com/charls-data/lunar2solar)，说明Stata安装文件包含`.ado`、`.mmat`、`.sthlp`。当前项目尚未复制或调用该程序；应先固定版本/校验和，再用于逐人日期转换。
- Harmonized CHARLS Codebook要求在使用其数据或Codebook信息的书面分析中致谢Gateway团队；若后续论文实际使用Harmonized CHARLS数据或其信息，应按原文添加致谢并遵循其当前说明。项目当前只是方法和QA参照，没有自动向外发送邮件。
- 项目本地逐波问卷与Codebook仍是原始字段、问卷路由和值编码的优先证据；上述Harmonized Codebook负责说明其汇总变量的构造，而不是替代每波问卷。

