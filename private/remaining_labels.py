"""List concepts that still have English labels, ranked by result count."""
import re
from collections import Counter
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
CJK = re.compile(r"[\u4e00-\u9fff]")
pairs = pd.read_csv(BASE / "private/results/pair_term_results_v1.csv", low_memory=False)
pairs = pairs[pd.to_numeric(pairs["n_model_min"], errors="coerce") >= 100]

labels = {}
for wave in ("2011", "2013", "2015", "2018", "2020"):
    reg = pd.read_csv(BASE / "private/derived_wave_tables" / f"registry_{wave}_full.csv")
    for cid, label in zip(reg["concept_id"], reg["label"]):
        labels.setdefault(cid, str(label))

counts = Counter(pairs["exposure_concept_id"]) + Counter(pairs["phenotype_concept_id"])
missing = [(n, cid, labels.get(cid, "")) for cid, n in counts.items() if not CJK.search(labels.get(cid, ""))]
missing.sort(reverse=True)
print("concepts without Chinese label:", len(missing))
for n, cid, label in missing[:90]:
    print(f"{n:6d}  {cid}  |  {label[:72]}")
