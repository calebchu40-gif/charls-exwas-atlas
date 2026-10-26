# CHARLS 数据状态、个人设备迁移与复现步骤

更新日期：2026-10-22

## 先看当前数据状态

- 项目服务器的 CHARLS 专属工作目录已进行只读清点：目录存在，但没有 `.dta`、`.zip`、`.rar` 等 CHARLS 数据文件。
- 当前电脑的非同步私有目录保留了五个按波次分开的个人级分析表（2011、2013、2015、2018、2020），以及年龄候选、慢病状态、教育/户籍、性别/婚姻派生表和 2011 社区/PSU 文件。个人设备迁移 ZIP 中包含这些私有材料。
- 当前私有目录没有原始五波官方 ZIP/RAR，也没有 Harmonized CHARLS D 原文件。因此旧分析表可直接支持继续做候选变量审计、方法/权重设计和管线开发，但无法从官方源档案重新生成原始变量目录或完整准备表；需要源级重建时，按下文自行申请并下载。
- 2026-10-22再次按已记录的输入目录核查，`%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\raw_archives`、`D:\CHARLS_Source`和桌面`CHARLS_Source`均不存在；不能据此推断其他未登记位置没有数据。当前源级重建仍待从官方端取得发行档案。
- 项目此前的数据清点记录曾指出 2015 独立 Blood Data 和 2014 Life History 为缺项。即使后来重新下载五波主包，也应单独核对这两项是否需要及是否已获准。

## 私有输出路径

五波个人级准备表、派生协变量/结局表和由它们计算的QA汇总默认均位于 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas`：个人表放在各自的 `derived_*` 子目录，派生覆盖/路由/配对计数写入 `qa_outputs`。这些报告也留在本机受控目录，不进入同步项目目录。若需指定目录，使用 `CHARLS_EXWAS_PRIVATE_ROOT`、`CHARLS_EXWAS_DATA_DIR` 和 `CHARLS_EXWAS_QA_DIR`；脚本会拒绝把个人数据或数据派生输出写进 OneDrive、Dropbox、Google Drive 或 iCloud 路径。仅 `site-prototype/dist/` 的字段级公开目录可随 GitHub 提交。

## 个人设备迁移包的安全使用

个人设备包包含 CHARLS 受访者级数据，只用于同一位已获授权用户在本人设备间迁移。不要把它放进 OneDrive/其他同步目录、GitHub、公开网盘或公共服务器，也不要发送给其他研究者。官方协议对原始微观数据披露和访问有明确限制；该迁移包不代表 CHARLS 官方数据授权。

解压到新的设备后，建议放入非同步且只有本人可访问的本地目录。ZIP 内部有顶层文件夹 `CHARLS_ExWAS_Atlas_DeviceTransfer`；例如选择解压到 `D:\` 后，实际根目录为 `D:\CHARLS_ExWAS_Atlas_DeviceTransfer`。该根目录下有 `CHARLS_ExWAS_Atlas`（项目代码、文档、公开资料和 `private_data` 个人级分析表）。不要把整个解压目录放入同步盘。

## 新设备上立即继续（无需重新下载源数据）

在 PowerShell 中将路径改成自己的解压位置：

```powershell
$transfer = 'D:\CHARLS_ExWAS_DeviceTransfer\CHARLS_ExWAS_Atlas_DeviceTransfer'
$project = Join-Path $transfer 'CHARLS_ExWAS_Atlas'
$private = Join-Path $transfer 'CHARLS_ExWAS_Atlas\private_data'
$env:CHARLS_EXWAS_PRIVATE_ROOT = $private
$env:CHARLS_EXWAS_DATA_DIR = Join-Path $private 'derived_wave_tables'
$qa = Join-Path $private 'qa_outputs'
New-Item -ItemType Directory -Path $qa -Force | Out-Null
python -m pip install pandas pyreadstat
python -m compileall -q (Join-Path $project 'scripts')
python (Join-Path $project 'scripts\validate_prepared_wave_tables.py') --data-dir $env:CHARLS_EXWAS_DATA_DIR --output-dir $qa
python (Join-Path $project 'scripts\build_core_concept_coverage.py') --data-dir $env:CHARLS_EXWAS_DATA_DIR --project-dir $project --output-dir $qa
```

这会先验证五波准备表，再重建核心概念覆盖与逐对可用人数等聚合 QA。已在原设备实跑：五波均为 `PASS`（行数分别17,705、18,605、21,095、19,816、19,395；ID缺失和重复均为0），核心概念覆盖重建为31个概念、945行配对可用性结果。新设备运行时应获得相同结构；若数字不同，先核对数据版本和校验清单。其他已可用的波次审计脚本位于 `scripts/`。`audit_harmonized_age_reference.py`、`build_age_candidate_tables.py` 及需要 Harmonized D 的慢病 crosswalk 仍需该 DTA 文件；缺文件时先跳过，不要把其他波次数据当作替代品。

## 申请数据后从官方源重新构建

CHARLS 是官方公开发布、可供研究者申请的数据（通常不收取数据费），但“公开”不等于匿名直接下载或可以转发微观记录。官网要求用户注册、签署协议、核验邮箱，并逐轮申请公开发布的数据；FAQ 目前写明申请一般在三个工作日内审核。协议限制用途并禁止用户向他人披露或授予数据访问。每位实际使用者都应按 CHARLS 当前要求取得自己的许可：

- 官方协议：<https://charls.charlsdata.com/users/sign_up/agreement/en.html>
- 官方 FAQ / 申请流程：<https://charls.pku.edu.cn/en/Faq/Frequently_Asked_Questions.htm>
- 官方数据门户：<https://charls.pku.edu.cn/en/>
- 官方2020 Wave 5发布通知：<https://charls.pku.edu.cn/en/info/1190/1331.htm>（说明该波于2023-11-16发布，并引导用户登录门户注册下载）

2026-10-22以官方FAQ和Wave 5发布通知复核：CHARLS数据可由研究者注册申请，下载前须提供真实身份信息并签署协议/完成邮箱核验；官方FAQ称申请通常需约三个工作日审核。此项目没有可用的官方账号会话，因此当前不从匿名链接猜测或抓取受限微观数据。用户或合作者各自从官方门户取得许可后，可按下列归档清单运行准备脚本；本项目网站和交接包继续只包含字段级元数据与公开文档。

下载后先逐波阅读官方用户指南、问卷、代码本、发布说明和权重文件，校验档案完整性/官网 SHA-1。若要运行现有准备脚本，将原始数据按下列文件名放在某个非同步根目录下的 `原始数据+问卷2011~2020\<波次>` 子目录：

- `2011\household_and_community_questionnaire_data.rar`
- `2013\CHARLS2013_Dataset.zip`
- `2015\CHARLS2015r.zip`
- `2018\CHARLS2018r.zip`
- `2020\CHARLS2020r.zip`

再运行：

```powershell
$rawRoot = 'D:\CHARLS_Source'
python (Join-Path $project 'scripts\prepare_charls_wave_tables.py') --input-root $rawRoot --out-dir (Join-Path $private 'derived_wave_tables') --waves 2011,2013,2015,2018,2020
```

注意脚本会在 `$rawRoot` 下自动追加 `原始数据+问卷2011~2020`。2011 RAR 解包依赖系统 `tar`/兼容解包工具；运行前用 `tar --version` 确认可用。Harmonized CHARLS D 单独下载后设置：

```powershell
$env:CHARLS_HARMONIZED_D_PATH = 'D:\CHARLS_Private\H_CHARLS_D_Data.dta'
```

2015 Blood Data 是独立血液数据文件，不要假定包含在2015主 ZIP 中；2014 Life History 是可选扩展。是否纳入由 Atlas 变量范围决定，并按官网单独申请/核验发布文件。

## 项目内容与适用边界

- 个人设备迁移 ZIP：用于本人设备间延续当前分析，含本机派生表；不等同于原始数据的完整备份。
- `CHARLS_ExWAS_Atlas_协作者交接包.zip`：可用于分享代码、公开文件、方法记录和非个人级结果，不含任何微观数据。
- 个人级输入和派生表仅放在非同步、受控目录。进入项目目录的只能是可披露的汇总 QA；发布网站前仍须进行 CHARLS 条款和披露审查。

### CHARLS公开数据的访问方式（官方FAQ核实，2026-10-16）

CHARLS历年公开发布数据是免费提供给研究者申请的公开数据，但不属于匿名、免注册、无条件直链下载的开放数据。官方FAQ说明：使用者需在官网注册、签署数据使用协议、提供真实个人信息并确认邮箱；之后对各次已公开发布的数据分别提交申请，官方页面说明通常在3个工作日内审核回复。CHARLS 2020发布公告也要求登录网站注册后下载。这里的“申请”是免费公开数据的访问手续，不代表数据收费、非公开，也不需要绕过流程；不同研究者应各自按规则申请。官方用户指南和问卷随波次提供，应在分析前阅读。

官方来源：CHARLS [中文FAQ](https://charls.pku.edu.cn/Faq/cjwt.htm)、[英文FAQ](https://charls.pku.edu.cn/en/Faq/Frequently_Asked_Questions.htm)、[Wave 5 2020发布公告](https://charls.pku.edu.cn/info/1131/1812.htm)。

### 2026-10-17 clean7 设备迁移包结构核对

最新个人设备迁移包位于 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas_DeviceTransfer_2026-10-17_clean14.zip`。包内顶层为 `CHARLS_ExWAS_Atlas_DeviceTransfer`，其中项目代码、公开官方资料及 `private_data` 一并位于 `CHARLS_ExWAS_Atlas`。解压后按本文件“新设备上立即继续”部分设置 `$project`、`$private` 即可运行；包内保留703个准备数据文件，不含五波原始发布ZIP/RAR，也不含Harmonized CHARLS D。仅限同一位已授权用户在本人受控设备间迁移。

### 2026-10-17 clean7 目录增量

clean7保留clean6中的703个本人个人级准备数据文件，并同步最新协作者项目材料，包括退休史45概念/238映射、E/P候选目录728概念、4,781条E/P映射及对应审计记录。目录与复现检查均已完成；原始CHARLS发布档案仍不在包内。该包只用于同一获授权用户的本人设备迁移。

### 2026-10-26 官方用户协议再核与公开站点致谢

重新核对 CHARLS 官方[中文用户条款](https://charls.charlsdata.com/users/sign_up/agreement/zh-cn.html)与[官方 FAQ](https://charls.pku.edu.cn/Faq/cjwt.htm)。官方条款明确：数据限学术研究、不得商业使用；不得以任何形式公开原始微观数据；不得转让、出售、出租、出借或以其他方式提供给他人；要求注册时提供真实姓名和单位。官方 FAQ 说明每位使用者需注册、签署协议并分别申请各公开数据集，申请通常在三个工作日内审核。数据授权仍是个人/账号层级，不因本项目仓库公开或同一研究团队协作而自动共享。

官方协议还要求使用 CHARLS 数据的发表物致谢“北京大学国家发展研究院和北京大学中国社会科学调查中心”，并对2011全国基线指定引用《China Health and Retirement Longitudinal Study, 2011-2012 National Baseline Users' Guide》。已在公开站点页脚加入数据致谢与官方用户指南链接；当前站点仍只有公开字段元数据，没有微观数据或真实关联结果。未来真实结果论文须保留完整指定引用；其他波次若有额外引用要求，按对应官方版本条款另行核实。

本次可检索到的官方协议网页经浏览器文本抽取仅显示同意控件，但官方搜索索引返回上述完整中文条款。此记录不代替实际注册时由 CHARLS 展示的协议版本；下载前仍须由数据申请者阅读并同意当时页面上的现行条款。
