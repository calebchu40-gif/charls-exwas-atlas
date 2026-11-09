"""List db-prefixed items (ADL/IADL) and CES-D items per wave."""
import json
from pathlib import Path

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
inv = json.loads((BASE / "private/derived_wave_tables/column_inventory.json").read_text(encoding="utf-8"))

for wave in ("2011", "2013", "2015", "2018", "2020"):
    labels = inv[wave]["labels"]
    db = [(c, l) for c, l in labels.items() if c.startswith("db0") and l]
    print("==", wave, "db items", len(db))
    for col, label in db[:26]:
        print("   ", col, "|", label[:56])
