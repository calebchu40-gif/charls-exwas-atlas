"""Reconcile pilot v3 against published 2011 rows on single-term matches."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
registry = pd.read_csv(BASE / "private/derived_wave_tables/registry_2011_core_v3.csv")
pilot = pd.read_csv(BASE / "private/results/pilot_2011_core_v3.csv", low_memory=False)
published = json.loads((BASE / "code/site-prototype/dist/association_results_v1.json").read_text(encoding="utf-8"))
pub = pd.DataFrame([row for family in published["families"] for row in family["rows"]])
pub = pub[pub["wave"] == "2011"]

pilot_ok = pilot[(pilot["fit_status"] == "success") & (pilot["model_id"] == "M1")].copy()
# single-term pairs only: one row per (exposure_variable, phenotype_variable) in pilot
counts = pilot_ok.groupby(["exposure_variable", "phenotype_variable"]).size().rename("n_terms")
pilot_single = pilot_ok.merge(counts[counts == 1].reset_index(), on=["exposure_variable", "phenotype_variable"])

merged = pub.merge(
    pilot_single[["exposure_variable", "phenotype_variable", "estimate", "p_value", "model_id"]],
    on=["exposure_variable", "phenotype_variable"],
    suffixes=("_pub", "_pilot"),
)
print("matched single-term rows:", len(merged))
if len(merged):
    merged["sign_agree"] = np.sign(merged["estimate_pub"]) == np.sign(merged["estimate_pilot"])
    print("sign agreement:", round(float(merged["sign_agree"].mean()), 3))
    print("correlation of estimates:", round(float(merged[["estimate_pub", "estimate_pilot"]].corr().iloc[0, 1]), 3))
    print(merged[["exposure_variable", "phenotype_variable", "estimate_pub", "estimate_pilot", "sign_agree"]].head(12).to_string())
    # same significance calls
    pub_sig = merged["p_value_pub"] < 0.05
    pilot_sig = merged["p_value_pilot"] < 0.05
    print("significance agreement:", round(float((pub_sig == pilot_sig).mean()), 3),
          "| pub significant:", int(pub_sig.sum()), "pilot significant:", int(pilot_sig.sum()))
