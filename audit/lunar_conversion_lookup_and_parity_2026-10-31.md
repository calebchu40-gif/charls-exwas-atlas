# 农历转换：官方查表、许可边界与直接等价性（2026-10-31）

**结论：农历↔公历的「转换表」这一层已经可以关闭，而且不需要 Stata。**
剩下的只是**由出生日期推导年龄区间**的方法问题（部分日期、闰月歧义、BA004 路由），不是转换本身。

本轮未读取任何参与者记录、未解包数据、未拟合模型。

---

## 1. 官方查表本身就是完整答案

CHARLS 官方包 `github.com/charls-data/lunar2solar`（commit `2284ccff`，**MIT 许可**）包含：

| 文件 | 作用 |
|---|---|
| `lunar2solar.ado` | 只做读取与写入，**不计算结果** |
| `lunar2solar.mmat` | **预计算好的查表**：普通表 49,949 行 + 闰月表 1,521 行，每行 `(solar YYYYMMDD, lunar YYYYMMDD)` |
| `lunar2solar.sthlp` | 帮助文件 |

也就是说：`LunarDate(...).toSolarDate()` 的**全部信息**都已经在这张表里，Stata 只是把它读出来。
本项目已把该 MIT 包完整纳入 `references/charls_lunar2solar/`（含 LICENSE）。

表文件 SHA-256：`ebec9fe5109295a347894ec6173aa3750adbb270329f0ba357d2778636d20aa2`
覆盖范围：太阳历 `1900-01-31` – `2040-12-31`，共 **51,470** 个映射。

## 2. 直接逐格对照：0 处不一致（已复现）

用固定的 `python-lunardate 0.1.4`（源码 SHA-256 `3b2eb1b9…`）逐行比对官方表：

| 表 | 行数 | 唯一农历键 | Python 无法转换 | 映射不一致 |
|---|---|---|---|---|
| 普通 | 49,949 | 49,949 | 0 | **0** |
| 闰月 | 1,521 | 1,521 | 0 | **0** |

- 首次执行：2026-10-30 09:13（本机受保护 QA）
- **本轮独立复现**：2026-10-31，输出 `official_lunar_mmat_vs_python014_reproduced_20261031.json`，与首次结果逐字段相同

复现命令：

```bash
python scripts/verify_official_lunar_table_parity.py \
  --official-mmat references/charls_lunar2solar/src/lunar2solar.mmat \
  --lunardate-source <external>/lunardate-0.1.4/lunardate.py \
  --output <private>/qa_outputs/official_lunar_mmat_vs_python014_reproduced_20261031.json
```

> 此前的交接记录里仍写着“尚未与 CHARLS Mata 查找表逐值验证”。该表述已过期：直接对照已经做过并有可复现输出；未执行的是另一条“用 Stata 跑合成网格”的工作流，而它对本问题的必要性已被上面的直接对照取代。

## 3. 许可边界：不把 GPLv3 带进仓库

`python-lunardate` 的 `PKG-INFO` 明确写 **License: GPLv3**（其源码头注明衍生自 GPLv2 的 lunar 项目）。
把它 vendor 进本仓库会引入传染性许可义务，因此**不纳入**。它只作为**外部交叉验证工具**使用，不随仓库分发。

项目自身的转换实现只依赖 MIT 的官方表：

- 新增 `scripts/lunar_lookup.py`：加载官方 `.mmat`（校验 SHA-256），提供
  `to_solar(y, m, d, leap=False)` 与 `from_solar(y, m, d)`；未知键返回 `None` 而不是抛异常。
- 新增 `tests/test_lunar_lookup.py`：7 项测试，含**全表 51,470 行往返一致性**、闰月与普通月区分、
  表被篡改时拒绝加载、越界返回 `None`。

## 4. 对年龄门的影响

| 子问题 | 之前状态 | 现在 |
|---|---|---|
| 农历→公历转换是否与官方一致 | “未逐值验证” | ✅ **已验证（0 不一致）且可回归** |
| 是否依赖 Stata | 曾被当作阻断 | ❌ 不依赖；表即答案 |
| 部分日期/闰月歧义的年龄区间 | 未决 | 仍未决（属方法问题，需独立审阅） |
| BA002/BA003/BA004 路由 | 已修正并记录 | 仍需审阅确认 |

因此年龄门的剩余内容收敛为：**用已核实的转换 + 已修正的路由，把“不完整/闰月日期”的区间规则写清楚并交独立审阅**，
不再需要等 Stata 或等外部工具。

## 5. 边界声明

- 本轮只读公开查表文件与公开文档；
- 未读取出生日期、暴露、结局；
- 未运行任何关联模型；
- 正式关联模型数仍为 **0**。
