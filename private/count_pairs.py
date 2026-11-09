"""Count unique exposure-phenotype pairs across the full registries."""
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables")
pairs = set()
per_wave = {}
for wave in ("2011", "2013", "2015", "2018", "2020"):
    reg = pd.read_csv(BASE / f"registry_{wave}_full.csv")
    e = reg[reg["role"] == "E"]["concept_id"].unique()
    p = reg[reg["role"] == "P"]["concept_id"].unique()
    per_wave[wave] = (len(e), len(p), len(e) * len(p))
    for a in e:
        for b in p:
            pairs.add((a, b))
    print(wave, "E", len(e), "P", len(p), "pairs", len(e) * len(p))
print("unique pairs across waves:", len(pairs))
