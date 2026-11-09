"""List dc0* item labels per wave to locate recall and serial-7 items."""
import json
from pathlib import Path

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
inv = json.loads((BASE / "private/derived_wave_tables/column_inventory.json").read_text(encoding="utf-8"))

for wave in ("2011", "2013", "2015", "2018", "2020"):
    labels = inv[wave]["labels"]
    hits = [(c, l) for c, l in labels.items() if c.startswith("dc0") and l]
    print("==", wave, len(hits))
    for col, label in hits[:40]:
        print("   ", col, "|", label[:60])
