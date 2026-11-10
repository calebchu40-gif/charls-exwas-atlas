"""List labels that remain English in the built public index."""
import json
import re
from pathlib import Path

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
index = json.loads((BASE / "private/results/public_full_scan_v2/index.json").read_text(encoding="utf-8"))
CJK = re.compile(r"[\u4e00-\u9fff]")
missing = [(item["n_results"], item["id"], item["label"]) for item in index["exposures"] + index["outcomes"]
           if not CJK.search(item["label"])]
missing.sort(reverse=True)
print("remaining", len(missing))
for n, cid, label in missing[:80]:
    print(f"{n:6d}  {cid}  |  {label[:72]}")
