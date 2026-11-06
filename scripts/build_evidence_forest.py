#!/usr/bin/env python3
"""Assemble the ten evidence lines into one forest-plot payload.

Every number is read from the published module JSONs so the forest can never
drift from the tables. The gradient entry is kept out of the pooled forest
(different scale) and listed separately.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site-prototype" / "dist"
OUT = SITE / "evidence_forest_v1.json"


def load(name):
    return json.loads((SITE / name).read_text(encoding="utf-8"))


def main() -> int:
    entries = []

    def add(label, group, estimate, low, high, p=None, n=None, note=""):
        entries.append({"label": label, "group": group, "estimate": estimate,
                        "ci_lower": low, "ci_upper": high, "p": p, "n": n, "note": note})

    pilot = load("association_results_v1.json")
    rows = [row for family in pilot["families"] for row in family["rows"]
            if str(row.get("model_id", "")).startswith("Pilot105")]

    def pilot_row(exposure, phenotype="blood_uric_acid"):
        for row in rows:
            if row["exposure_concept_id"] == exposure and row["phenotype_concept_id"] == phenotype:
                return row
        return None

    for exposure, label in (("cooking_fuel_coal", "单项：煤 vs 电"),
                            ("cooking_fuel_crop_residue_or_wood", "单项：秸秆木材 vs 电"),
                            ("running_water_at_residence", "单项：自来水")):
        row = pilot_row(exposure)
        if row:
            add(label, "单项对照 2011", float(row["estimate"]), float(row["ci_lower"]),
                float(row["ci_upper"]), float(row["p_value"]), row.get("n_model"))

    solid = load("solid_fuel_blood_v1.json")
    row = next(item for item in solid["results"] if item["phenotype_concept_id"] == "blood_uric_acid")
    add("固体燃料合并", "合并 2011", row["estimate"], row["ci_lower"], row["ci_upper"],
        row["p"], row["n"])

    joint = load("joint_household_model_v1.json")
    for term, label in (("fuel_coal", "联合模型：煤"), ("fuel_crop_residue_or_wood", "联合模型：木材"),
                        ("water_yes", "联合模型：自来水")):
        cell = next(item for item in joint["results"]
                    if item["term"] == term and item["phenotype_concept_id"] == "blood_uric_acid")
        add(label, "联合模型 2011", cell["estimate"], cell["ci_lower"], cell["ci_upper"],
            cell["p_value"], cell["n_model"])

    lifestyle = load("lifestyle_restricted_v1.json")
    for item in lifestyle["results"]:
        add(f"生活方式限制：{item['term']}", "敏感性分析", item["estimate"], item["ci_lower"],
            item["ci_upper"], item["p_value"], item["n_model"])

    strata = load("uric_strata_v1.json")
    for item in strata["results"]:
        add(item["stratum"], "分层分析", item["estimate"],
            item["ci_lower"], item["ci_upper"], item["p_value"], item["n_model"])

    wave2015 = load("wave2015_solid_fuel_v1.json")
    row = wave2015["results"][0]
    add("2015 固体燃料（完整协变量）", "跨波复现", row["estimate"], row["ci_lower"], row["ci_upper"],
        row["p_value"], row["n_model"])

    gradient = load("fuel_gradient_v1.json")
    row = next(item for item in gradient["results"] if item["phenotype_concept_id"] == "blood_uric_acid")
    payload = {
        "schema_version": 1,
        "outcome": "blood_uric_acid (standardised beta unless noted)",
        "entries": entries,
        "gradient": {"label": "清洁度梯度（每等级）", "estimate": row["estimate"],
                     "ci_lower": row["ci_lower"], "ci_upper": row["ci_upper"],
                     "p": row["p"], "n": row["n"]},
        "summary": {"entries": len(entries),
                    "negative": sum(1 for item in entries if item["estimate"] < 0),
                    "p_lt_05": sum(1 for item in entries if (item["p"] or 1) < 0.05)},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                   encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
