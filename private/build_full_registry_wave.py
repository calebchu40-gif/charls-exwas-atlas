"""Build a full registry for one wave from real availability (n>=100, no coverage cut).

Usage: python build_full_registry_wave.py 2015
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
TABLES = {
    "2011": BASE / "private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta",
    "2013": BASE / "private/derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
    "2015": BASE / "private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": BASE / "private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
    "2020": BASE / "private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
}

MIN_N = 100
MIN_LEVEL_N = 20
MAX_LEVELS = 8
EXCLUDE_P_CATEGORIES = {"chronic disease ancillary"}
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
        if "=" in part:
            code, label = part.split("=", 1)
            if code.strip():
                parsed[code.strip()] = label.strip()
    return parsed



def level_key(code: str) -> float:
    try:
        return float(code)
    except (TypeError, ValueError):
        return 1e9


def count_for(counts, code: str) -> int:
    try:
        return int(counts.get(float(code), 0))
    except (TypeError, ValueError):
        return int(counts.get(code, 0))

def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace("", np.nan), errors="coerce")


def main(wave: str) -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    availability = json.loads((BASE / "private/derived_wave_tables" / f"availability_{wave}.json").read_text(encoding="utf-8"))
    avail = availability["variables"]
    table = TABLES[wave]
    weight = json.loads((BASE / "private" / f"design_{wave}.json").read_text(encoding="utf-8"))["weight"]

    candidates = []
    for row in catalog:
        if wave not in str(row.get("waves", "")).split(","):
            continue
        variable = str(row.get("Variable.Name", "")).strip()
        info = avail.get(variable)
        if not info or info.get("n_sample", 0) < MIN_N:
            continue
        if "DO NOT ANALYZE" in str(row.get("Review.Flag", "")) + str(row.get("value_labels", "")):
            continue
        role_set = roles(row)
        category = str(row.get("category"))
        if "e" in role_set:
            role = "E"
        elif "p" in role_set and category not in EXCLUDE_P_CATEGORIES:
            role = "P"
        else:
            continue
        cid = concept_of(row)
        if not cid:
            continue
        candidates.append({
            "concept_id": cid, "role": role, "variable": variable,
            "label": str(row.get("Variable.Description") or variable)[:120],
            "unit": unit_of(row)[:40], "labels": parse_labels(row.get("value_labels", "")),
        })

    by_key = {}
    for entry in candidates:
        key = (entry["concept_id"], entry["variable"])
        if key not in by_key or (entry["role"] == "P" and by_key[key]["role"] == "E"):
            by_key[key] = entry
    candidates = list(by_key.values())

    # read candidate columns once for classification and level counts
    variables = sorted({entry["variable"] for entry in candidates})
    df, _ = pyreadstat.read_dta(table, usecols=["ID", weight] + variables)
    weight_values = numeric(df[weight])
    sample = weight_values.gt(0)

    rows, dropped = [], Counter()
    for entry in candidates:
        values = numeric(df[entry["variable"]])
        in_sample = values[sample]
        n = int(in_sample.notna().sum())
        if n < MIN_N:
            dropped["too_few"] += 1
            continue
        base = {
            "concept_id": entry["concept_id"], "role": entry["role"], "label": entry["label"],
            "wave": wave, "source_variable": entry["variable"], "unit": entry["unit"],
            "valid_min": "", "valid_max": "", "yes_code": "", "no_code": "",
        }
        raw_sample = df.loc[sample, entry["variable"]].replace("", np.nan).notna().sum()
        numeric_share = n / raw_sample if raw_sample else 0.0
        codes = {code: label for code, label in entry["labels"].items()
                 if not any(w in label.lower() for w in MISSING_WORDS)}
        levels = {}
        if codes and 2 <= len(codes) <= MAX_LEVELS:
            counts = in_sample.value_counts()
            present = {code: count_for(counts, code) for code in codes}
            levels = {code: value for code, value in present.items() if value >= MIN_LEVEL_N}
        if len(levels) == 2:
            ordered = sorted(levels, key=level_key)
            yes = next((c for c in ordered if codes[c].lower().startswith("yes")), ordered[0])
            no = next((c for c in ordered if c != yes), ordered[1])
            rows.append({**base, "kind": "binary", "variable": f"__bin_{entry['concept_id']}",
                         "transform": "", "levels": "0|1", "reference": "0",
                         "family": "binomial" if entry["role"] == "P" else "gaussian",
                         "yes_code": yes, "no_code": no})
            continue
        if len(levels) >= 3:
            reference = max(levels, key=levels.get)
            rows.append({**base, "kind": "categorical", "variable": entry["variable"],
                         "transform": "", "levels": "|".join(sorted(levels, key=level_key)),
                         "reference": reference, "family": "gaussian"})
            continue
        numeric_ok = numeric_share >= 0.9
        if entry["unit"] or numeric_ok:
            sd = float(in_sample.std())
            if not np.isfinite(sd) or sd <= 1e-9:
                dropped["zero_variance"] += 1
                continue
            rows.append({**base, "kind": "continuous", "variable": entry["variable"],
                         "transform": "z", "levels": "", "reference": "", "family": "gaussian"})
            continue
        dropped["unclassified"] += 1

    deduped, seen = [], set()
    for entry in rows:
        key = (entry["role"], entry["concept_id"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(entry)

    fields = ["concept_id", "role", "label", "wave", "variable", "kind", "unit", "transform",
              "valid_min", "valid_max", "levels", "reference", "family", "source_variable", "yes_code", "no_code"]
    out = BASE / "private" / "derived_wave_tables" / f"registry_{wave}_full.csv"
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
