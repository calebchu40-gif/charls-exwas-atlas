"""Build the 2011 core registry v3: continuous, binary and categorical exposures.

Adds binary chronic-disease outcomes and recoded binary exposures.  Every entry
carries its raw source column plus the yes/no codes so the runner can build a
clean 0/1 column before fitting.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
CATALOG = BASE / "code" / "site-prototype" / "dist" / "catalog.json"
INVENTORY = BASE / "private" / "derived_wave_tables" / "column_inventory.json"
TABLE = BASE / "private" / "derived_wave_tables" / "CHARLS_wave2011_person_analytic.dta"
OUT = BASE / "private" / "derived_wave_tables" / "registry_2011_core_v3.csv"

WAVE = "2011"
MIN_COVERAGE = 0.50
MIN_LEVEL_N = 30

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
P_CONTINUOUS = {"biochemistry", "anthropometric", "blood pressure"}
P_BINARY = {"chronic disease", "health and symptoms", "physical function", "mental health", "social wellbeing"}

MISSING_WORDS = ("don't know", "dont know", "do not know", "refuse", "missing", "not applicable", "unknown")


def roles(row: dict) -> set[str]:
    return {part.strip() for part in str(row.get("epcf", "")).split(",") if part.strip()}


def unit(row: dict) -> str:
    return str(row.get("Concept.Unit.Candidates") or row.get("candidate_concept_units") or "").strip()


def concept(row: dict) -> str:
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


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    columns = set(inventory[WAVE]["columns"])

    candidates: list[dict] = []
    for row in catalog:
        if WAVE not in str(row.get("waves", "")).split(","):
            continue
        variable = str(row.get("Variable.Name", "")).strip()
        if variable not in columns:
            continue
        flag = str(row.get("Review.Flag", "")) + str(row.get("value_labels", ""))
        if "DO NOT ANALYZE" in flag:
            continue
        role_set = roles(row)
        category = str(row.get("category"))
        if "e" in role_set and category in E_CATEGORIES:
            role = "E"
        elif "p" in role_set and (category in P_CONTINUOUS or category in P_BINARY):
            role = "P"
        else:
            continue
        cid = concept(row)
        if not cid:
            continue
        candidates.append({
            "concept_id": cid, "role": role, "variable": variable,
            "label": str(row.get("Variable.Description") or variable)[:110],
            "unit": unit(row)[:40], "category": category,
            "labels": parse_labels(row.get("value_labels", "")),
        })

    # de-duplicate concept/variable, preferring P
    by_key: dict[tuple[str, str], dict] = {}
    for entry in candidates:
        key = (entry["concept_id"], entry["variable"])
        if key not in by_key or (entry["role"] == "P" and by_key[key]["role"] == "E"):
            by_key[key] = entry
    candidates = list(by_key.values())

    variables = sorted({entry["variable"] for entry in candidates})
    df, _ = pyreadstat.read_dta(TABLE, usecols=["ID", "bloodweight"] + variables)
    weight = numeric(df["bloodweight"])
    sample = weight.gt(0)

    rows: list[dict] = []
    dropped = Counter()
    diag: list[dict] = []
    for entry in candidates:
        values = numeric(df[entry["variable"]])
        coverage = float(values[sample].notna().mean()) if sample.any() else 0.0
        if coverage < MIN_COVERAGE:
            dropped["low_coverage"] += 1
            diag.append({"variable": entry["variable"], "role": entry["role"], "reason": "low_coverage", "coverage": round(coverage, 3)})
            continue
        codes = entry["labels"]
        real = {code: label for code, label in codes.items() if not any(w in label.lower() for w in MISSING_WORDS)}
        base = {
            "concept_id": entry["concept_id"], "role": entry["role"], "label": entry["label"],
            "wave": WAVE, "source_variable": entry["variable"], "unit": entry["unit"],
            "valid_min": "", "valid_max": "", "yes_code": "", "no_code": "",
        }
        in_sample = values[sample]
        if entry["unit"] and in_sample.notna().sum() >= 500:
            sd = float(in_sample.std())
            if not np.isfinite(sd) or sd <= 1e-9:
                dropped["zero_variance"] += 1
                continue
            rows.append({
                **base, "kind": "continuous", "variable": entry["variable"],
                "transform": "z", "levels": "", "reference": "",
                "family": "gaussian",
            })
            continue
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
            rows.append({
                **base, "kind": "binary", "transform": None,
                "variable": f"__bin_{entry['concept_id']}",
                "levels": "0|1", "reference": "0",
                "family": "binomial" if entry["role"] == "P" else "gaussian",
                "yes_code": yes, "no_code": no,
            })
        else:
            reference = max(present, key=present.get)
            rows.append({
                **base, "kind": "categorical", "transform": None,
                "variable": entry["variable"],
                "levels": "|".join(sorted(present, key=lambda c: float(c))),
                "reference": reference, "family": "gaussian",
            })

    # one row per (role, concept): later duplicates add nothing for the scan
    deduped = []
    seen_concepts = set()
    for entry in rows:
        key = (entry["role"], entry["concept_id"])
        if key in seen_concepts:
            continue
        seen_concepts.add(key)
        deduped.append(entry)
    rows = deduped

    fields = ["concept_id", "role", "label", "wave", "variable", "kind", "unit",
              "transform", "valid_min", "valid_max", "levels", "reference", "family",
              "source_variable", "yes_code", "no_code"]
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for entry in rows:
            writer.writerow({**{f: entry.get(f, "") for f in fields}})

    import csv as _csv
    with open("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/registry_2011_v3_diag.csv", "w", newline="", encoding="utf-8") as handle:
        writer = _csv.DictWriter(handle, fieldnames=["variable", "role", "reason", "coverage"])
        writer.writeheader()
        writer.writerows(diag)
    counts = Counter((entry["role"], entry["kind"]) for entry in rows)
    print(json.dumps({"kept": len(rows), "breakdown": {f"{r}-{k}": v for (r, k), v in counts.items()},
                      "dropped": dict(dropped), "registry": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
