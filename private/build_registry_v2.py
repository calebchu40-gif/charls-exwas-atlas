"""Build the 2011 registry with data-driven checks (numeric share, SD, coverage)."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
CATALOG = BASE / "code" / "site-prototype" / "dist" / "catalog.json"
INVENTORY = BASE / "private" / "derived_wave_tables" / "column_inventory.json"
TABLE = BASE / "private" / "derived_wave_tables" / "CHARLS_wave2011_person_analytic.dta"
OUT = BASE / "private" / "derived_wave_tables" / "registry_2011_core_continuous_v2.csv"
DIAG = BASE / "private" / "derived_wave_tables" / "registry_2011_diagnostics.csv"

WAVE = "2011"
MIN_NUMERIC_SHARE = 0.90
MIN_NONMISSING = 500
MIN_SD = 1e-9

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

    candidates = []
    for row in catalog:
        if WAVE not in str(row.get("waves", "")).split(","):
            continue
        variable = str(row.get("Variable.Name", "")).strip()
        if variable not in columns:
            continue
        if "DO NOT ANALYZE" in str(row.get("Review.Flag", "")) or "DO NOT ANALYZE" in str(row.get("value_labels", "")):
            continue
        if not unit(row):
            continue
        role_set = roles(row)
        if "e" in role_set and str(row.get("category")) in E_CATEGORIES:
            role = "E"
        elif "p" in role_set and str(row.get("category")) in P_CATEGORIES:
            role = "P"
        else:
            continue
        cid = concept(row)
        if not cid:
            continue
        candidates.append({
            "concept_id": cid, "role": role, "variable": variable,
            "label": str(row.get("Variable.Description") or variable)[:120],
            "unit": unit(row)[:40], "category": str(row.get("category")),
        })

    # de-duplicate concept/variable, preferring P
    by_key: dict[tuple[str, str], dict] = {}
    for entry in candidates:
        key = (entry["concept_id"], entry["variable"])
        if key not in by_key or (entry["role"] == "P" and by_key[key]["role"] == "E"):
            by_key[key] = entry
    candidates = list(by_key.values())

    usecols = ["ID", "bloodweight"] + sorted({c["variable"] for c in candidates})
    df, _ = pyreadstat.read_dta(TABLE, usecols=usecols)

    kept, dropped = [], []
    for entry in candidates:
        series = df[entry["variable"]]
        numeric = pd.to_numeric(series.replace("", np.nan), errors="coerce")
        weight = pd.to_numeric(df["bloodweight"].replace("", np.nan), errors="coerce")
        in_sample = weight.gt(0)
        share = float(numeric[in_sample].notna().mean()) if in_sample.any() else 0.0
        nonmissing = int(numeric[in_sample].notna().sum())
        mask = in_sample & numeric.notna()
        if mask.sum() > 10:
            values = numeric[mask].to_numpy()
            weights = weight[mask].to_numpy()
            mean = float(np.average(values, weights=weights))
            sd = float(np.sqrt(np.average((values - mean) ** 2, weights=weights)))
        else:
            sd = 0.0
        if share < MIN_NUMERIC_SHARE:
            dropped.append({**entry, "reason": "non_numeric", "share": round(share, 3)})
        elif nonmissing < MIN_NONMISSING:
            dropped.append({**entry, "reason": "low_coverage", "nonmissing": nonmissing})
        elif not np.isfinite(sd) or sd <= MIN_SD:
            dropped.append({**entry, "reason": "zero_variance", "sd": sd})
        else:
            kept.append(entry)

    fields = ["concept_id", "role", "label", "wave", "variable", "kind", "unit",
              "transform", "valid_min", "valid_max", "levels", "reference", "family"]
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for entry in kept:
            writer.writerow({
                "concept_id": entry["concept_id"], "role": entry["role"], "label": entry["label"],
                "wave": WAVE, "variable": entry["variable"], "kind": "continuous",
                "unit": entry["unit"], "transform": "z", "valid_min": "", "valid_max": "",
                "levels": "", "reference": "", "family": "gaussian",
            })
    with DIAG.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["concept_id", "role", "variable", "reason", "share", "nonmissing", "sd"])
        writer.writeheader()
        for entry in dropped:
            writer.writerow({
                "concept_id": entry["concept_id"], "role": entry["role"],
                "variable": entry["variable"], "reason": entry["reason"],
                "share": entry.get("share", ""), "nonmissing": entry.get("nonmissing", ""),
                "sd": entry.get("sd", ""),
            })

    counts = Counter(entry["role"] for entry in kept)
    print(json.dumps({
        "candidates": len(candidates), "kept": len(kept), "E": counts["E"], "P": counts["P"],
        "dropped": Counter(entry["reason"] for entry in dropped),
        "registry": str(OUT), "diagnostics": str(DIAG),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
