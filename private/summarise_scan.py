"""Summarise the five-wave core scan."""
from collections import Counter
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
rows = []
for wave in ("2011", "2013", "2015", "2018", "2020"):
    path = BASE / "private/results" / f"scan_{wave}_core_v1.csv"
    if not path.exists():
        path = BASE / "private/results" / "pilot_2011_core_v3.csv"
    df = pd.read_csv(path, low_memory=False)
    df["wave"] = wave
    rows.append(df)
all_df = pd.concat(rows, ignore_index=True)
print("total rows:", len(all_df))
print("by wave:", Counter(all_df["wave"]).most_common())
print("status:", Counter(all_df["fit_status"]).most_common(4))

ok = all_df[all_df["fit_status"] == "success"].copy()
ok["p_value"] = pd.to_numeric(ok["p_value"], errors="coerce")
print("success rate:", round(100 * len(ok) / len(all_df), 1), "%")
print("p<0.05:", int((ok["p_value"] < 0.05).sum()), "=", round(100 * (ok["p_value"] < 0.05).mean(), 1), "%")
print("unique exposure concepts:", ok["exposure_concept_id"].nunique())
print("unique phenotype concepts:", ok["phenotype_concept_id"].nunique())
print("unique pairs:", ok.groupby(["wave", "exposure_concept_id", "phenotype_concept_id"]).ngroups)

for wave, group in ok.groupby("wave"):
    sig = (group["p_value"] < 0.05).sum()
    print(f"  {wave}: fits {len(group)}, p<0.05 {sig} ({100*sig/len(group):.1f}%)")
