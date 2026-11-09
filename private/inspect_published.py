"""Inspect published rows and expose which columns support level mapping."""
import json
from pathlib import Path

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
data = json.loads((BASE / "code/site-prototype/dist/association_results_v1.json").read_text(encoding="utf-8"))
rows = [r for f in data["families"] for r in f["rows"]]
print("rows", len(rows))
print("keys", list(rows[0].keys()))
for row in rows[:3]:
    print({k: row[k] for k in list(row)[:16]})

# exposure concept ids for 2011
concepts = sorted({r["exposure_concept_id"] for r in rows if r["wave"] == "2011"})
print("2011 exposure concepts", len(concepts))
print(concepts[:40])
