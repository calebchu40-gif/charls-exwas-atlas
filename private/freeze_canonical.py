"""Freeze one canonical row per pair (M1 primary, M0 as sensitivity) and count."""
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/results")
frames = []
for wave in ("2011", "2013", "2015", "2018", "2020"):
    df = pd.read_csv(BASE / f"scan_{wave}_core_fdr.csv", low_memory=False)
    df = df[df["fit_status"] == "success"].copy()
    key = ["wave", "exposure_concept_id", "phenotype_concept_id", "phenotype_variable", "exposure_variable"]
    m1 = df[df["model_id"] == "M1"].drop_duplicates(key)
    m0 = df[df["model_id"] == "M0"][key + ["estimate", "p_value"]].rename(
        columns={"estimate": "estimate_M0", "p_value": "p_value_M0"})
    merged = m1.merge(m0, on=key, how="left")
    frames.append(merged)
    print(wave, "success rows", len(df), "| unique pairs (M1)", len(m1))

allp = pd.concat(frames, ignore_index=True)
print("TOTAL unique pairs across waves:", len(allp))
print("by wave:", allp["wave"].value_counts().to_dict())
print("unique exposure concepts:", allp["exposure_concept_id"].nunique())
print("unique phenotype concepts:", allp["phenotype_concept_id"].nunique())
print("p<0.05:", int((allp["p_value"] < 0.05).sum()), "| q<0.05:", int((allp["q_family"] < 0.05).sum()))
allp.to_csv(BASE / "canonical_results_v1.csv", index=False)
print("wrote", BASE / "canonical_results_v1.csv")
