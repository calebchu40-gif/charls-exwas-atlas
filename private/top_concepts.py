"""List the most frequent exposures/outcomes in the public result set with labels."""
from collections import Counter
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
pairs = pd.read_csv(BASE / "private/results/pair_term_results_v1.csv", low_memory=False)
pairs = pairs[pd.to_numeric(pairs["n_model_min"], errors="coerce") >= 100]
labels = {}
for wave in ("2011", "2013", "2015", "2018", "2020"):
    reg = pd.read_csv(BASE / "private/derived_wave_tables" / f"registry_{wave}_full.csv")
    for cid, label in zip(reg["concept_id"], reg["label"]):
        labels.setdefault(cid, str(label))

for column, name in (("exposure_concept_id", "EXPOSURES"), ("phenotype_concept_id", "OUTCOMES")):
    counts = Counter(pairs[column])
    print(f"== {name} top 40")
    for cid, n in counts.most_common(40):
        print(f"{n:6d}  {cid}  |  {labels.get(cid, '')[:70]}")
