"""Merge ADL/IADL columns into the wave outcome files and registries."""
import csv
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables")
FIELDS = ["concept_id", "role", "label", "wave", "variable", "kind", "unit", "transform",
          "valid_min", "valid_max", "levels", "reference", "family", "source_variable", "yes_code", "no_code"]

for wave in ("2011", "2013", "2015", "2018"):
    outcomes = BASE / f"outcomes_wave{wave}.csv"
    adl = pd.read_csv(BASE / f"outcomes_{wave}.csv", dtype={"ID": str})
    base = pd.read_csv(outcomes, dtype={"ID": str})
    merged = base.merge(adl[["ID", "adl_any", "iadl_any"]], on="ID", how="outer")
    merged.to_csv(outcomes, index=False)
    print(wave, "outcome columns", list(merged.columns), "rows", len(merged))

    reg_path = BASE / f"registry_{wave}_core.csv"
    with reg_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    existing = {row["concept_id"] for row in rows}
    for concept, label, column in (("adl_any", "Any ADL limitation", "adl_any"),
                                   ("iadl_any", "Any IADL limitation", "iadl_any")):
        if concept in existing:
            continue
        rows.append({
            "concept_id": concept, "role": "P", "label": label, "wave": wave,
            "variable": column, "kind": "binary", "unit": "", "transform": "",
            "valid_min": "", "valid_max": "", "levels": "0|1", "reference": "0",
            "family": "binomial", "source_variable": column, "yes_code": "1", "no_code": "0",
        })
    with reg_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(wave, "registry rows", len(rows))
