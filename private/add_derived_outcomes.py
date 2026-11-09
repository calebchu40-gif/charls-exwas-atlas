"""Append the derived CES-D outcome to every wave registry (idempotent)."""
import csv
from pathlib import Path

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables")
FIELDS = ["concept_id", "role", "label", "wave", "variable", "kind", "unit", "transform",
          "valid_min", "valid_max", "levels", "reference", "family", "source_variable", "yes_code", "no_code"]

for wave in ("2011", "2013", "2015", "2018", "2020"):
    path = BASE / f"registry_{wave}_core.csv"
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if any(row["concept_id"] == "cesd_score" for row in rows):
        print(wave, "already has cesd_score")
        continue
    rows.append({
        "concept_id": "cesd_score", "role": "P", "label": "CES-D 10-item depressive symptom score",
        "wave": wave, "variable": "cesd_score", "kind": "continuous", "unit": "score",
        "transform": "z", "valid_min": "0", "valid_max": "30", "levels": "", "reference": "",
        "family": "gaussian", "source_variable": "cesd_score", "yes_code": "", "no_code": "",
    })
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(wave, "appended cesd_score, rows", len(rows))
