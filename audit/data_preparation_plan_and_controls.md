# CHARLS 数据准备流程与使用控制

更新：2026-10-10。此文件只记数据流程和使用限制，不包含个人记录。

整体软件流程可借鉴 NHANES PE Atlas / `nhanespewas` 的目录、配对、模型配置和汇总结果架构；具体数据定义与所有统计规则以 CHARLS 官方材料为准，实施边界见 `nhanes_to_charls_implementation_contract_v1.md`。不得复制 NHANES 的变量、权重、周期合并、分析门槛或人群范围。

## 官方条款与存放原则

CHARLS 注册条款将数据限定为学术研究，禁止以任何形式发布原始微观数据或向他人转交/提供数据；可发布的应是无法关联到受访者的统计或分析结果。当前输入目录和本项目均位于 OneDrive Desktop 路径下，因此分析级个人数据不写入该目录。派生数据放在本机 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\derived_wave_tables`。尚未向服务器复制微观或派生个人级数据。

官方依据：[CHARLS 用户协议](https://charls.charlsdata.com/users/sign_up/agreement/zh-cn.html)、[2020 Wave 5 用户手册及发布页](https://charls.charlsdata.com/pages/Data/2020-charls-wave5/zh.html)、[2015 Blood Data 发布说明和下载页](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/zh-cn.html)。

网站阶段需要坚持统计结果发布，不提供下载/查询个人记录；对小样本组合、稀有类别和可反推信息做披露审查，并按 CHARLS 条款显示要求的致谢/引用。服务器副本只有在确认目录为本人独占访问、权限限制与学校/项目批准相符后再做；私有目录权限本身不能取代数据使用协议。

## 当前派生表定义

脚本 `scripts/prepare_charls_wave_tables.py` 从已提供的官方波次包构建波次分开的 respondent-level Stata 表：

- 以当轮 `Demographic_Background` 为个人主表，要求 `ID` 唯一；每轮保留受访者行数，不做跨波堆叠。
- 个人模块仅按 `ID` 一对一左连接。家庭收入/住房按 `householdID` 多对一连接；社区/PSU 模块仅在 `communityID` 键唯一时纳入，否则记录为未合并模块。
- `Weights` 拆成 respondent weight 与 household weight 两张唯一键小表；先验证同一 ID/household 下各自权重列一致，不能安全折叠时就不并入。
- 关系 roster/子女/父母/兄弟姐妹表、退出访谈/死亡模块及 verbal autopsy 保持独立，避免把关系记录扩展成多行个人表或把退出样本错误塞进当前受访者表。
- 2011 独立 `Blood_20140429.dta` 按 ID 并入；2015独立 Blood Data 未在当前文件中，不能凭 Biomarker 问卷生成检验结果。
- 变量名尽可能沿用原始名；遇到冲突才加模块短前缀。冲突映射、逐模块匹配比例和跳过原因均写入 QA CSV。

## 目录字段与本地准备表的头信息对照（2026-10-25）

新增 `scripts/audit_prepared_catalog_field_availability.py`。脚本只读取 Stata 文件的变量名头信息，不遍历受访者记录；将公开候选目录中的波次/角色/字段代码与本机五张波次个人表做名称级筛查，并把汇总表、未匹配字段代码和权重/样本标记字段清单写入 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\qa_outputs`。输出不含 ID、字段取值、非缺失记录数、配对样本量或关联结果，不进入项目仓库。名称命中不证明数据文件模块身份、字段可用分母或可分析性；这些仍需依据官方问卷、发布说明和批准使用的源文件逐项核实。

本机头信息对照显示：2018和2020的目录代码均能在对应准备表找到同名字段；2011有270个社区模块暴露代码未在个人表中，社区表继续独立保留以避免 `communityID` 非唯一连接；2013有26个父母/子女关系模块代码未进入一人一行个人表；2015有26个父母/子女/兄弟姐妹关系模块代码和独立2015 Blood Data中的16个暴露及16个表型代码未进入个人表。这里报告的是候选字段代码数，不是受访者数量或实验室结果覆盖人数。2013表头目前仍无官方 `crosssection` 与 `longitudinal` 字段，因此仍不得推断该轮横断面样本资格或进行加权分析。逐字段 QA 仅保存在本机受控目录。

## 运行和验证

建议按单波运行以控制内存，并确保 `--out-dir` 是非同步、仅本人可访问的路径：

```powershell
python scripts/prepare_charls_wave_tables.py --input-root "<含原始数据+问卷2011~2020的父目录>" --out-dir "$env:LOCALAPPDATA\CHARLS_ExWAS_Atlas\derived_wave_tables" --waves 2011
```

将 `--waves` 改为 2013、2015、2018 或 2020 逐一运行。每轮完成后核查输出 DTA 可读回、行列数、`ID` 唯一性、基表行数一致性、每个模块的键匹配比例以及权重常量性。不要因某模块低匹配而删除主表样本；先回查该模块的适用调查对象、跳题/部分访问和 wave release note。

## 尚未纳入/需单独审计的来源

- 2015独立 Blood Data 文件缺失；获得后依据 2015 Blood Data Release Note 的 ID 对齐、检测单位、样本筛选与专属 `Blood_weight`，作为独立 assay module 加入，不与当轮 Biomarker 体格测量模块混淆。
- 2014 Life History 文件缺失；当前基础表不含完整生命历程暴露。
- 2011 `community.dta` 有454行、450个`communityID`和454个`communityID+sub_commuID`组合；2个PSU含多条社区模块记录（最多3条），而respondent表只有`communityID`、没有`sub_commuID`。聚合审计估计，按`communityID`直接左连接会额外复制182条respondent行，影响到91名受访者。详见`audit/community_2011_key_aggregate_qa_v1.csv`。该模块继续独立存放；在问卷确认变量单位并解决个人/家庭到子社区的归属前，不挑选、均值合并或复制子社区值进入个人ExWAS。
- 退出模块和 verbal autopsy 应作为死亡/退出结局的独立数据源，通过官方 ID 规则与跟访状态资料审查后再整合。
- 当前合并是结构准备，不等于每个字段已完成跨波概念 harmonization，更没有估计任何暴露—结局关联。
