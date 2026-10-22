"""Ensure every catalog analysis lock appears exactly once in the triage note."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CATALOG = AUDIT / "charls_atlas_candidate_fields_v0.csv"
TRIAGE = AUDIT / "do_not_analyze_triage_2026-10-22.md"
ROW = re.compile(r"\b(2011|2013|2015|2018|2020) `([^`]+)`")
GROUP = re.compile(r"^###\s+(\d+)条：", re.MULTILINE)

with CATALOG.open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
locked = {
    (row.get("Source.Wave", ""), row.get("Variable.Name", ""))
    for row in catalog
    if "do not analyze" in row.get("Review.Flag", "").lower()
}

text = TRIAGE.read_text(encoding="utf-8")
section = text.split("## 字段清单", 1)[1].split("## 执行规则", 1)[0]
lines = section.splitlines()
listed: list[tuple[str, str]] = []
declared_total = 0
for index, line in enumerate(lines):
    match = GROUP.match(line)
    if not match:
        continue
    declared_total += int(match.group(1))
    next_line = next((candidate for candidate in lines[index + 1:] if candidate.strip()), "")
    listed.extend(ROW.findall(next_line))

listed_set = set(listed)
duplicates = sorted({item for item in listed if listed.count(item) > 1})
if duplicates or len(listed) != declared_total or listed_set != locked:
    missing = sorted(locked - listed_set)
    extra = sorted(listed_set - locked)
    raise SystemExit(f"DO NOT ANALYZE triage mismatch: catalog={len(locked)}, listed={len(listed)}, declared={declared_total}, duplicates={duplicates}, missing={missing}, extra={extra}")

print(f"PASS catalog locks={len(locked)}; triage rows={len(listed)}; all wave-field entries match exactly")
