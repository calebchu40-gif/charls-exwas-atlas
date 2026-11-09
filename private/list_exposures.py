"""List pilot registry exposures and match them against published 2011 concepts."""
import json
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
reg = pd.read_csv(BASE / "private/derived_wave_tables/registry_2011_core_v3.csv")
e = reg[reg["role"] == "E"][["concept_id", "variable", "kind", "source_variable", "yes_code", "no_code", "levels", "reference"]]
print(e.to_string(max_rows=60))

pub = json.loads((BASE / "code/site-prototype/dist/association_results_v1.json").read_text(encoding="utf-8"))
rows = [r for f in pub["families"] for r in f["rows"] if r["wave"] == "2011"]
concepts = {r["exposure_concept_id"] for r in rows}
print("\npublished concepts:", sorted(concepts))
matched = [c for c in concepts if c in set(e["concept_id"])]
print("direct concept matches:", matched)
