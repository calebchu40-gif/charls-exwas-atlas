"""Build the 2011 core-set registry (continuous exposures x continuous blood outcomes).

Reads the reviewed public catalog and the private column inventory, keeps only
variables that actually exist in the 2011 analytic table, and writes a registry
CSV the ExWAS engine can consume.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
CATALOG = BASE / "code" / "site-prototype" / "dist" / "catalog.json"
INVENTORY = BASE / "private" / "derived_wave_tables" / "column_inventory.json"
OUT = BASE / "private" / "derived_wave_tables" / "registry_2011_core_continuous.csv"

WAVE = "2011"

E_CATEGORIES = {
    "housing and built environment",
    "food and household environment",
    "behavior",
    "social protection",
    "social determinants",
    "community context",
    "healthcare access",
    "family and intergenerational context",
    "environmental perception",
    "life-course and reproductive history",
    "internal biomarker",
}
P_CATEGORIES = {"biochemistry"}


def roles(row: dict) -> set[str]:
    return {part.strip() for part in str(row.get("epcf", "")).split(",") if part.strip()}


def unit(row: dict) -> str:
    return str(row.get("Concept.Unit.Candidates") or row.get("candidate_concept_units") or "").strip()


def concept(row: dict) -> str:
    ids = [c.strip() for c in str(row.get("candidate_concept_ids", "")).replace(";", ",").split(",") if c.strip()]
    return ids[0] if ids else ""


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    columns = set(inventory[WAVE]["columns"])

    rows = []
    skipped = Counter()
    for row in catalog:
        if WAVE not in str(row.get("waves", "")).split(","):
            continue
        variable = str(row.get("Variable.Name", "")).strip()
        if variable not in columns:
            skipped["not_in_table"] += 1
            continue
        if "DO NOT ANALYZE" in str(row.get("Review.Flag", "")) or "DO NOT ANALYZE" in str(row.get("value_labels", "")):
            skipped["do_not_analyze"] += 1
            continue
        if not unit(row):
            skipped["no_unit"] += 1
            continue
        role_set = roles(row)
        if "e" in role_set and str(row.get("category")) in E_CATEGORIES:
            role, family, transform = "E", "gaussian", "z"
        elif "p" in role_set and str(row.get("category")) in P_CATEGORIES:
            role, family, transform = "P", "gaussian", "z"
        else:
            skipped["out_of_scope"] += 1
            continue
        cid = concept(row)
        if not cid:
            skipped["no_concept"] += 1
            continue
        rows.append({
            "concept_id": cid,
            "role": role,
            "label": str(row.get("Variable.Description") or row.get("Concept.Label.Candidates") or variable)[:120],
            "wave": WAVE,
            "variable": variable,
            "kind": "continuous",
            "unit": unit(row)[:40],
            "transform": transform,
            "valid_min": "",
            "valid_max": "",
            "levels": "",
            "reference": "",
            "family": family,
        })

    unique = []
    by_key: dict[tuple[str, str], dict] = {}
    for entry in rows:
        key = (entry["concept_id"], entry["variable"])
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = entry
        elif entry["role"] == "P" and existing["role"] == "E":
            by_key[key] = entry
    unique = list(by_key.values())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(unique[0].keys()))
        writer.writeheader()
        writer.writerows(unique)

    counts = Counter(entry["role"] for entry in unique)
    print(json.dumps({"rows": len(unique), "E": counts["E"], "P": counts["P"],
                      "skipped": dict(skipped), "path": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
