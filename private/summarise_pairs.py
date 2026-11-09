"""Summarise the pair-level results."""
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/results")
df = pd.read_csv(BASE / "pair_term_results_v1.csv", low_memory=False)
print("rows (pair x term):", len(df))
print("unique exposure concepts:", df["exposure_concept_id"].nunique())
print("unique phenotype concepts:", df["phenotype_concept_id"].nunique())
print("unique pairs:", df.groupby(["exposure_concept_id", "phenotype_concept_id"]).ngroups)
print("wave counts:", df["waves"].value_counts().sort_index().to_dict())
print("n_model quantiles:", df["n_model_min"].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).round(0).to_dict())
for threshold in (100, 300, 500, 1000):
    print(f"rows with n>={threshold}:", int((df["n_model_min"] >= threshold).sum()))
print("p<0.05:", int((df["p_value"] < 0.05).sum()), "| q<0.05:", int((df["q_value"] < 0.05).sum()))
print("negative estimates:", int((df["estimate"] < 0).sum()), "| positive:", int((df["estimate"] > 0).sum()))
