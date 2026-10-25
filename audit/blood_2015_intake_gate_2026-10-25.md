# CHARLS 2015 Blood Data 安全入库闸门（2026-10-25）

## 已确认的官方发布信息

- CHARLS 官方 Wave 3 数据页将 **Blood Data** 作为独立文件列出，更新日期为 2019-06-20，官方页面列出的下载文件 SHA1 为 `DE5B1D80E9B72D61B690DFF19B191F50F21EE8C5`。官方发布新闻称需登录注册后的数据网站下载，因此本项目不尝试绕过账号流程，也不使用未经验证的第三方副本。
- 官方 Blood Data Release Note VersionID `20190620` 的 SHA1 为 `F48C549A7F1253230D4C11CBAE1687966A3D39D5`；本机PDF已重算并匹配。官方数据页和发布说明均列明静脉血分析物、单位与字段定义。
- 发布说明记载 2015 Wave 3 有 21,100 名访谈对象，13,420 人回应血样；其中横截面样本有 20,284 人，13,013 人回应血样。提供的 `Blood_weight` 是横截面血检权重，由个体横截面权重乘以血检应答概率逆权重构成，逆概率因子在第99百分位截尾；不提供纵向血检权重。
- 发布说明称 `ID` 可连接 Wave 3 其他数据和早期 Wave 1 血检数据；若回连 Wave 1，须按 Wave 2 发布说明调整基线 householdID/ID。血样是模块子样本，不能把一般 Wave 3 横截面权重直接替代 `Blood_weight`。

## 本机文件状态与闸门脚本

截至本次受控文件名扫描，2015独立 Blood Data 文件仍不在本地准备目录。官方授权用户取得下载项后，应把原始下载项及 Stata 文件分别放入 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\incoming_2015_blood\`，不要放进OneDrive、项目目录、GitHub或Pages。

脚本 `scripts/audit_2015_blood_intake.py` 默认核验官方 Blood Data 下载项 SHA1，并通过 `pyreadstat` 的 `metadataonly=True` 检查 DTA 表头：`ID`、`Blood_weight`、16项分析物字段、空腹标记和TG顶码标记；同时核验发行说明所列13,420行。它不会读取受访者数值、展示ID、合并准备表或输出统计结果。只有通过哈希和表头闸门后，才进入单独的ID唯一性、样本旗标、权重和测量值审计；上述后续步骤尚未执行。

默认本地命令（在项目根目录运行）：

```powershell
python scripts/audit_2015_blood_intake.py `
  --artifact "$env:LOCALAPPDATA\CHARLS_ExWAS_Atlas\incoming_2015_blood\Blood_Data_2015_download" `
  --stata-file "$env:LOCALAPPDATA\CHARLS_ExWAS_Atlas\incoming_2015_blood\Blood_Data_2015.dta"
```

如果 CHARLS 下载项本身就是 DTA，`--artifact` 与 `--stata-file` 可指向同一文件。若下载项是压缩文件，先在受控目录中人工解压，再分别传入原始下载项和提取后的 DTA；脚本会校验下载项的官方SHA1和DTA表头，不会自动解压或改写源文件。聚合QA仅写入受保护的 `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\qa_outputs\blood_2015_intake_metadata.json`。

## 官方来源

- [CHARLS 2015 Wave 3 官方数据页](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html)（列出 Blood Data 文件、更新时间和SHA1）
- [CHARLS 2015 Blood Data Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf)
- [CHARLS 2015 血检数据发布公告](https://charls.pku.edu.cn/en/info/1010/1012.htm)（说明登录下载）
