"""Build a core registry for one wave (continuous + binary + categorical).

Usage: python build_registry_wave.py 2013
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
CATALOG = BASE / "code" / "site-prototype" / "dist" / "catalog.json"
INVENTORY = BASE / "private" / "derived_wave_tables" / "column_inventory.json"
TABLES = {
    "2011": BASE / "private" / "derived_wave_tables" / "CHARLS_wave2011_person_analytic.dta",
    "2013": BASE / "private" / "derived_wave_tables" / "CHARLS_wave2013_person_analytic.dta",
    "2015": BASE / "private" / "derived_wave_tables" / "CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": BASE / "private" / "derived_wave_tables" / "CHARLS_wave2018_person_analytic.dta",
    "2020": BASE / "private" / "derived_wave_tables" / "CHARLS_wave2020_person_analytic.dta",
}

MIN_COVERAGE = 0.50
MIN_LEVEL_N = 30

E_CATEGORIES = {
    "housing and built environment", "food and household environment", "behavior",
    "social protection", "social determinants", "community context", "healthcare access",
    "family and intergenerational context", "environmental perception",
    "life-course and reproductive history", "internal biomarker",
}
P_CONTINUOUS = {"biochemistry", "anthropometric", "blood pressure"}
P_BINARY = {"chronic disease", "health and symptoms", "physical function", "mental health", "social wellbeing"}

MISSING_WORDS = ("don't know", "dont know", "do not know", "refuse", "missing", "not applicable", "unknown")


def roles(row: dict) -> set[str]:
    return {part.strip() for part in str(row.get("epcf", "")).split(",") if part.strip()}


def unit_of(row: dict) -> str:
    return str(row.get("Concept.Unit.Candidates") or row.get("candidate_concept_units") or "").strip()


def concept_of(row: dict) -> str:
    ids = [c.strip() for c in str(row.get("candidate_concept_ids", "")).replace(";", ",").split(",") if c.strip()]
    return ids[0] if ids else ""


def parse_labels(text: str) -> dict[str, str]:
    parsed = {}
    for part in str(text or "").split(";"):
        if "=" not in part:
            continue
        code, label = part.split("=", 1)
        code, label = code.strip(), label.strip()
        if code:
            parsed[code] = label
    return parsed


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace("", np.nan), errors="coerce")


def main(wave: str) -> None:
    table = TABLES[wave]
    design = json.loads((BASE / "private" / f"design_{wave}.json").read_text(encoding="utf-8"))
    weight_col = design["weight"]
    out = BASE / "private" / "derived_wave_tables" / f"registry_{wave}_core.csv"

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    columns = set(inventory[wave]["columns"])

    candidates = []
    for row in catalog:
        if wave not in str(row.get("waves", "")).split(","):
            continue
        variable = str(row.get("Variable.Name", "")).strip()
        if variable not in columns:
            continue
        if "DO NOT ANALYZE" in str(row.get("Review.Flag", "")) + str(row.get("value_labels", "")):
            continue
        role_set = roles(row)
        category = str(row.get("category"))
        if "e" in role_set and category in E_CATEGORIES:
            role = "E"
        elif "p" in role_set and (category in P_CONTINUOUS or category in P_BINARY):
            role = "P"
        else:
            continue
        cid = concept_of(row)
        if not cid:
            continue
        candidates.append({
            "concept_id": cid, "role": role, "variable": variable,
            "label": str(row.get("Variable.Description") or variable)[:110],
            "unit": unit_of(row)[:40], "labels": parse_labels(row.get("value_labels", "")),
        })

    by_key = {}
    for entry in candidates:
        key = (entry["concept_id"], entry["variable"])
        if key not in by_key or (entry["role"] == "P" and by_key[key]["role"] == "E"):
            by_key[key] = entry
    candidates = list(by_key.values())

    variables = sorted({entry["variable"] for entry in candidates})
    df, _ = pyreadstat.read_dta(table, usecols=["ID", weight_col] + variables)
    weight = numeric(df[weight_col])
    sample = weight.gt(0)

    rows, dropped = [], Counter()
    for entry in candidates:
        values = numeric(df[entry["variable"]])
        coverage = float(values[sample].notna().mean()) if sample.any() else 0.0
        if coverage < MIN_COVERAGE:
            dropped["low_coverage"] += 1
            continue
        in_sample = values[sample]
        base = {
            "concept_id": entry["concept_id"], "role": entry["role"], "label": entry["label"],
            "wave": wave, "source_variable": entry["variable"], "unit": entry["unit"],
            "valid_min": "", "valid_max": "", "yes_code": "", "no_code": "",
        }
        if entry["unit"] and in_sample.notna().sum() >= 500:
            sd = float(in_sample.std())
            if not np.isfinite(sd) or sd <= 1e-9:
                dropped["zero_variance"] += 1
                continue
            rows.append({**base, "kind": "continuous", "variable": entry["variable"],
                         "transform": "z", "levels": "", "reference": "", "family": "gaussian"})
            continue
        codes = entry["labels"]
        real = {code: label for code, label in codes.items() if not any(w in label.lower() for w in MISSING_WORDS)}
        if not codes or not (2 <= len(real) <= 8):
            dropped["unclassified"] += 1
            continue
        counts = in_sample.value_counts()
        present = {code: int(counts.get(float(code), counts.get(code, 0))) for code in real}
        present = {code: n for code, n in present.items() if n >= MIN_LEVEL_N}
        if len(present) < 2:
            dropped["level_too_small"] += 1
            continue
        if len(present) == 2:
            codes_sorted = sorted(present, key=lambda c: float(c))
            yes = next((c for c in codes_sorted if real[c].lower().startswith("yes")), codes_sorted[0])
            no = next((c for c in codes_sorted if c != yes), codes_sorted[1])
            rows.append({**base, "kind": "binary", "transform": "",
                         "variable": f"__bin_{entry['concept_id']}", "levels": "0|1", "reference": "0",
                         "family": "binomial" if entry["role"] == "P" else "gaussian",
                         "yes_code": yes, "no_code": no})
        else:
            reference = max(present, key=present.get)
            rows.append({**base, "kind": "categorical", "transform": "",
                         "variable": entry["variable"], "levels": "|".join(sorted(present, key=lambda c: float(c))),
                         "reference": reference, "family": "gaussian"})

    deduped, seen = [], set()
    for entry in rows:
        key = (entry["role"], entry["concept_id"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(entry)

    fields = ["concept_id", "role", "label", "wave", "variable", "kind", "unit", "transform",
              "valid_min", "valid_max", "levels", "reference", "family", "source_variable", "yes_code", "no_code"]
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for entry in deduped:
            writer.writerow({f: entry.get(f, "") for f in fields})

    counts = Counter((entry["role"], entry["kind"]) for entry in deduped)
    print(json.dumps({"wave": wave, "kept": len(deduped),
                      "breakdown": {f"{r}-{k}": v for (r, k), v in counts.items()},
                      "dropped": dict(dropped), "registry": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
