# CHARLS 2013 Wave 2 权重文件表头入库闸门（2026-10-25）

## 目的与官方来源

Wave 2 官方发布说明将 `Weights.dta` 列为独立文件，并说明其中含横截面与纵向样本资格标记。CHARLS Wave 2 官方下载清单仍列出 2015-11-18 版本，SHA1 为 `22c4fc89df2e55fa8faf051e88830eebe0e035c0`。该权重文件目前仍未进入本机受保护接收目录。

新增 `scripts/audit_2013_weights_intake.py` 作为合并前的轻量闸门：首先校验官方 SHA1，再用 `pyreadstat.read_dta(metadataonly=True)` 确认 Stata 表头含 `ID`、`crosssection`、`longitudinal` 和至少一个权重变量。只在 `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\` 写入不含个人记录的表头摘要。该脚本不读取标记值、权重值或ID，不计算样本数，也不合并文件。

文件通过表头闸门后，仍须运行 [`wave2_official_weight_intake_2026-10-23.md`](wave2_official_weight_intake_2026-10-23.md) 中已有的受保护合并脚本。合并前会再次校验同一 SHA1；随后校验ID唯一、准备表完全匹配、现有权重不冲突及样本标记存在。标记恢复仍不等于已选定权重、目标估计量或方差设计。

## 运行方法

将经本人获准CHARLS账户下载的官方 `Weights.dta` 放在本地隔离目录：

```powershell
python scripts/audit_2013_weights_intake.py `
  --weights "$env:LOCALAPPDATA\\CHARLS_ExWAS_Atlas\\incoming_2013_weights\\Weights.dta"
```

只有该闸门成功后，才按原接收手册执行 `scripts/merge_2013_official_weights.py`。禁止把来源不明的替代文件、原始文件、合并后的个体表或本机QA输出放入OneDrive、项目目录、GitHub或Pages。

## 验证范围

合成 Stata 文件测试覆盖：哈希及必要表头通过、错误来源哈希在尝试解析文件前被拒绝、即使测试哈希匹配但必要样本标记缺失也被拒绝。测试不包含 CHARLS 记录。当前尚未取得官方文件，因此没有真实文件的表头QA或合并结果。

## 官方出处

- [CHARLS Wave 2 官方数据页](https://charls.charlsdata.com/pages/Data/2013-charls-wave2/en.html)（`Weights` 更新日期及文件SHA1）
- [CHARLS Wave 2 Release Note](https://charls.pku.edu.cn/en/data/Release2013.pdf)（文件范围、资格标记和权重口径）
