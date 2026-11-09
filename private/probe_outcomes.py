"""Find CES-D, cognition and ADL/IADL item columns by label for each wave."""
import json
from pathlib import Path

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
inv = json.loads((BASE / "private/derived_wave_tables/column_inventory.json").read_text(encoding="utf-8"))

PATTERNS = {
    "cesd": ["depress", "everything i did", "trouble keeping", "bothered", "happy", "lonely", "could not get going", "fear", "sleep was restless", "felt sad"],
    "recall": ["word", "recall", "remember", "serial", "subtract", "100", "7"],
    "adl": ["dress", "bath", "eat", "bed", "toilet", "continence", "walk"],
    "iadl": ["housework", "cook", "shop", "money", "phone", "medicine"],
}

for wave in ("2011", "2013", "2015", "2018", "2020"):
    labels = inv[wave]["labels"]
    print("==", wave)
    for group, needles in PATTERNS.items():
        hits = []
        for col, label in labels.items():
            text = f"{label}".lower()
            if any(n in text for n in needles):
                hits.append((col, label[:50]))
        print("  ", group, hits[:8])
