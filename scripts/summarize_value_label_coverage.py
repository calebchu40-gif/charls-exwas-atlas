"""Rebuild the dated value-label coverage note from the current catalog."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


catalog = read_csv(AUDIT / "charls_atlas_candidate_fields_v0.csv")
ep_rows = [row for row in catalog if {part.strip() for part in row.get("epcf", "").split(",")} & {"e", "p"}]
labelled = [row for row in ep_rows if row.get("Value.Labels", "").strip()]
wave_codes = {(row.get("Source.Wave", ""), row.get("Variable.Name", "").lower()) for row in ep_rows}
labelled_wave_codes = {(row.get("Source.Wave", ""), row.get("Variable.Name", "").lower()) for row in labelled}
status_counts = Counter(row.get("Value.Label.Review", "") for row in ep_rows)
conflicts = [(row.get("Source.Wave", ""), row.get("Variable.Name", "")) for row in ep_rows if row.get("Value.Label.Review", "") == "conflict"]

coverage = read_csv(AUDIT / "charls_ep_catalog_value_label_coverage_v1.csv")
groups: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"rows": 0, "labels": 0, "subcategories": 0})
for row in coverage:
    role, category = row.get("epcf", ""), row.get("category", "")
    if role not in {"e", "p"}:
        continue
    group = groups[(role, category)]
    group["rows"] += int(row.get("field_category_rows", "0") or 0)
    group["labels"] += int(row.get("rows_with_reviewed_labels", "0") or 0)
    group["subcategories"] += 1

lines = [
    "# E/P值标签覆盖审计",
    "",
    f"更新：{date.today().isoformat()}。由`scripts/summarize_value_label_coverage.py`从当前字段目录和覆盖CSV自动生成。",
    "",
    f"- E/P字段—角色—类别目录行：{len(ep_rows):,}；不同波次—字段码：{len(wave_codes):,}。一条字段可能按多个候选类别/角色出现，均不是独立分析指标。",
    f"- 有非空官方/已审标签文本的E/P目录行：{len(labelled):,}；不同波次—字段码：{len(labelled_wave_codes):,}。连续测量、计数值及测量流程字段可以已审但没有类别标签，因此不计入此覆盖数。",
    f"- 明确标为`conflict`的E/P字段码：{len(set(conflicts))}；详情按主目录波次和变量码检索。",
    "- 值标签仅说明回答编码，不代表分析资格。题干、跳题、分母、特殊缺失、单位、跨波可比性、权重与方差设计仍须逐项审核。未使用代码本频数或个人记录。",
    "",
    f"## 按角色和类别汇总（{date.today().isoformat()}）",
    "",
    "|角色|网站类别|字段—角色—类别行（非互斥）|有标签文本行|子类别数|",
    "|---|---|---:|---:|---:|",
]
for (role, category), count in sorted(groups.items()):
    lines.append(f"|{role}|{category}|{count['rows']:,}|{count['labels']:,}|{count['subcategories']:,}|")
lines.extend(["", "## 当前值标签审核状态", "", "|审核状态|E/P目录行|", "|---|---:|"])
for status, count in status_counts.most_common():
    lines.append(f"|{status.replace('|', '\\|')}|{count:,}|")
lines.append("")
(AUDIT / "charls_ep_catalog_value_label_coverage_v1.md").write_text("\n".join(lines), encoding="utf-8")
print(f"E/P rows={len(ep_rows)}; distinct wave-fields={len(wave_codes)}; labelled rows={len(labelled)}; conflicts={len(set(conflicts))}")
