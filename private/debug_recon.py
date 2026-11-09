"""Debug reconciliation join keys."""
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
pilot = pd.read_csv(BASE / "private/results/pilot_2011_core_v3.csv", low_memory=False)
print("model ids:", pilot["model_id"].unique()[:5])
print("pilot exposures sample:", pilot["exposure_variable"].dropna().unique()[:8])
print("pilot phenotypes sample:", pilot["phenotype_variable"].dropna().unique()[:8])
print("status:", pilot["fit_status"].unique()[:5])

sub = pilot[(pilot["exposure_variable"] == "i017")]
print("i017 rows:", len(sub))
if len(sub):
    print(sub[["phenotype_variable", "exposure_term", "estimate", "model_id"]].head(6).to_string())
