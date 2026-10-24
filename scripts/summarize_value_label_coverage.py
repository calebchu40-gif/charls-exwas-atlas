"""Summarize value-label coverage from the final public role catalogues."""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "site-prototype" / "dist"
AUDIT = ROOT / "audit"


def read_json(path: Path) -> list[dict[str, str]]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


groups: dict[tuple[str, str], dict[str, object]] = {}
subgroups: dict[tuple[str, str, str], dict[str, object]] = {}
all_ep: list[dict[str, str]] = []
for role in ("e", "p"):
    rows = read_json(DIST / f"catalog_{role}.json")
    all_ep.extend(rows)
    for row in rows:
        category = str(row.get("category", "")).strip() or "Uncategorized"
        key = (role, category)
        group = groups.setdefault(key, {"rows": 0, "labels": 0, "subcategories": set(), "wave_fields": set()})
        group["rows"] = int(group["rows"]) + 1
        group["labels"] = int(group["labels"]) + bool(str(row.get("Value.Labels", "")).strip())
        group["subcategories"].add(str(row.get("subcategory", "")).strip())
        code = str(row.get("Variable.Name", "")).strip().lower()
        wave = str(row.get("Source.Wave", "")).strip()
        if code:
            group["wave_fields"].add((wave, code))
        subcategory = str(row.get("subcategory", "")).strip()
        subkey = (role, category, subcategory)
        sub = subgroups.setdefault(subkey, {"rows": 0, "labels": 0, "wave_fields": set()})
        sub["rows"] = int(sub["rows"]) + 1
        sub["labels"] = int(sub["labels"]) + bool(str(row.get("Value.Labels", "")).strip())
        if code:
            sub["wave_fields"].add((wave, code))

coverage_rows = []
for (role, category, subcategory), group in sorted(subgroups.items()):
    coverage_rows.append({
        "epcf": role,
        "category": category,
        "subcategory": subcategory,
        "field_category_rows": group["rows"],
        "distinct_wave_fields": len(group["wave_fields"]),
        "rows_with_reviewed_labels": group["labels"],
    })
write_csv(AUDIT / "charls_ep_catalog_value_label_coverage_v1.csv", coverage_rows,
          ["epcf", "category", "subcategory", "field_category_rows", "distinct_wave_fields", "rows_with_reviewed_labels"])

wave_fields = {(row.get("Source.Wave", ""), row.get("Variable.Name", "").lower()) for row in all_ep}
labelled = [row for row in all_ep if str(row.get("Value.Labels", "")).strip()]
labelled_wave_fields = {(row.get("Source.Wave", ""), row.get("Variable.Name", "").lower()) for row in labelled}
status_counts = Counter(str(row.get("Value.Label.Review", "")) for row in all_ep)
conflicts = {(row.get("Source.Wave", ""), row.get("Variable.Name", "")) for row in all_ep
             if row.get("Value.Label.Review", "") == "conflict"}
source_discrepancies = sorted({
    (row.get("Source.Wave", ""), row.get("Variable.Name", "")) for row in all_ep
    if "DO NOT ANALYZE" in row.get("Value.Label.Review", "")
    and "questionnaire:" in row.get("Value.Label.Review", "")
})
ep_pending = sum(row.get("Value.Label.Review", "").strip().lower() == "not yet reviewed" for row in all_ep)
c_rows = read_json(DIST / "catalog_c.json")
c_pending = sum(row.get("Value.Label.Review", "").strip().lower() == "not yet reviewed" for row in c_rows)

lines = [
    "# E/P值标签覆盖审计", "",
    f"更新：{date.today().isoformat()}。由`scripts/summarize_value_label_coverage.py`读取最终网站角色分片`catalog_e.json`、`catalog_p.json`和`catalog_c.json`生成；不读取早期中间字段表。", "",
    f"- 最终E/P目录行：{len(all_ep):,}；不同波次—字段码：{len(wave_fields):,}。一个字段可对应多个候选类别/角色。",
    f"- 有非空标签文本的E/P目录行：{len(labelled):,}；不同波次—字段码：{len(labelled_wave_fields):,}。连续测量、计数值及测量流程字段可已审但不需要离散标签。",
    f"- 最终E/P中精确状态为`not yet reviewed`的目录行：{ep_pending:,}；C目录对应行：{c_pending:,}。具体来源审查状态不等同于通用待审。",
    f"- 明确标为`conflict`的E/P字段码：{len(conflicts)}；问卷/Codebook差异仍锁定`DO NOT ANALYZE`的字段：{', '.join(f'{wave} `{code}`' for wave, code in source_discrepancies) if source_discrepancies else '无'}。",
    "- 值标签仅说明回答编码，不代表分析资格。题干、跳题、分母、特殊缺失、单位、跨波可比性、权重与方差设计仍须逐项审核。未使用代码本频数或个人记录。", "",
    f"## 按角色和类别汇总（{date.today().isoformat()}）", "",
    "|角色|网站类别|字段—角色—类别行|不同波次—字段码|有非空标签文本行|子类别数|",
    "|---|---|---:|---:|---:|---:|",
]
for (role, category), group in sorted(groups.items()):
    lines.append(f"|{role}|{category}|{group['rows']:,}|{len(group['wave_fields']):,}|{group['labels']:,}|{len(group['subcategories']):,}|")
lines.extend(["", "## 当前值标签审核状态", "", "|审核状态|最终E/P目录行|", "|---|---:|"])
for status, count in status_counts.most_common():
    safe_status = status.replace("|", "\\|")
    lines.append(f"|{safe_status}|{count:,}|")
lines.extend(["", "覆盖CSV与本报告均按最终网站角色分片重算；各类别可非互斥，不能将行数或类别数解释为独立测量指标、分析资格、样本量或关联结果。", ""])
(AUDIT / "charls_ep_catalog_value_label_coverage_v1.md").write_text("\n".join(lines), encoding="utf-8")
print(f"E/P rows={len(all_ep)}; distinct wave-fields={len(wave_fields)}; labelled rows={len(labelled)}; generic pending E/P={ep_pending}; C={c_pending}")
