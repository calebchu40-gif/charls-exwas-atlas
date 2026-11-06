#!/usr/bin/env python3
"""Cross-module consistency audit.

Every derived module (cross-wave meta, replication scorecard) quotes numbers that
must match the rows in the published association payload. This script re-derives
both and reports any mismatch, so the site cannot show two different values for
the same estimate.

Writes ``audit/module_consistency_2026-11-02.md`` and a JSON sibling.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site-prototype" / "dist"
AUDIT = ROOT / "audit"
MD = AUDIT / "module_consistency_2026-11-02.md"
JSON_OUT = AUDIT / "module_consistency_2026-11-02.json"
TOLERANCE = 1e-6


def load(name):
    return json.loads((SITE / name).read_text(encoding="utf-8"))


def main() -> int:
    payload = load("association_results_v1.json")
    rows = [row for family in payload["families"] for row in family["rows"]]
    index = {}
    for row in rows:
        key = (row["wave"], row["exposure_concept_id"], row["phenotype_concept_id"],
               row.get("contrast", ""), row.get("model_id", ""))
        index[key] = row

    meta = load("cross_wave_meta_v1.json")
    missing, mismatched, checked = [], [], 0
    for pair in meta["pairs"]:
        for entry in pair["inputs"]:
            checked += 1
            key = (entry["wave"], pair["exposure_concept_id"], pair["phenotype_concept_id"],
                   pair.get("contrast", ""), entry["model_id"])
            row = index.get(key)
            if row is None:
                missing.append(key)
                continue
            if abs(float(row["estimate"]) - float(entry["estimate"])) > TOLERANCE:
                mismatched.append({"key": key, "payload": row["estimate"],
                                   "module": entry["estimate"]})

    replication = load("replication_v1.json")
    rep_checked, rep_missing, rep_mismatched = 0, [], []
    for pair in replication["pairs"]:
        for wave, field in (("2011", "beta_2011"), ("2015", "beta_2015")):
            rep_checked += 1
            found = False
            for row in rows:
                if row["wave"] != wave:
                    continue
                if row["phenotype_concept_id"] != pair["phenotype_concept_id"]:
                    continue
                if abs(float(row.get("estimate") or "nan") - float(pair[field])) <= TOLERANCE:
                    found = True
                    break
            if not found:
                rep_mismatched.append({"wave": wave, "phenotype": pair["phenotype_concept_id"],
                                       "value": pair[field]})

    summary = {
        "payload_rows": len(rows),
        "meta_inputs_checked": checked,
        "meta_missing": len(missing),
        "meta_mismatched": len(mismatched),
        "replication_values_checked": rep_checked,
        "replication_unmatched": len(rep_mismatched),
    }
    lines = ["# 模块一致性审计（2026-11-02）\n",
             "校验派生模块引用的数字是否与公开 payload 完全一致。\n",
             "| 检查项 | 数量 |", "|---|---|"]
    for key, value in summary.items():
        lines.append(f"| {key} | {value} |")
    if mismatched:
        lines.append("\n## 不一致明细\n")
        for item in mismatched[:20]:
            lines.append(f"- {item['key']}: payload={item['payload']} module={item['module']}")
    if missing:
        lines.append("\n## 未在 payload 中找到的键\n")
        for key in missing[:20]:
            lines.append(f"- {key}")
    if rep_mismatched:
        lines.append("\n## 复现值未匹配\n")
        for item in rep_mismatched[:20]:
            lines.append(f"- {item}")
    MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    JSON_OUT.write_text(json.dumps({"summary": summary, "mismatched": mismatched[:50],
                                    "missing": [list(key) for key in missing[:50]],
                                    "replication_unmatched": rep_mismatched[:50]},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
