"""Reconcile matched binary exposures between published 2011 rows and pilot v3."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
reg = pd.read_csv(BASE / "private/derived_wave_tables/registry_2011_core_v3.csv")
pilot = pd.read_csv(BASE / "private/results/pilot_2011_core_v3.csv", low_memory=False)
pub = pd.DataFrame([r for f in json.loads((BASE / "code/site-prototype/dist/association_results_v1.json").read_text(encoding="utf-8"))["families"] for r in f["rows"]])
pub = pub[pub["wave"] == "2011"]
pub["estimate"] = pd.to_numeric(pub["estimate"], errors="coerce")
pub["p_value"] = pd.to_numeric(pub["p_value"], errors="coerce")

e = reg[(reg["role"] == "E") & (reg["kind"] == "binary")]
concept_map = dict(zip(e["concept_id"], e["variable"]))
pheno_map = dict(zip(reg[reg["role"] == "P"]["concept_id"], reg[reg["role"] == "P"]["variable"]))

m = pub[pub["exposure_concept_id"].isin(concept_map)].copy()
m["pilot_exposure"] = m["exposure_concept_id"].map(concept_map)
m["pilot_phenotype"] = m["phenotype_concept_id"].map(pheno_map)
m = m.dropna(subset=["pilot_phenotype"])

pl = pilot[(pilot["fit_status"] == "success") & (pilot["model_id"] == "M1")]
merged = m.merge(pl, left_on=["pilot_exposure", "pilot_phenotype"],
                 right_on=["exposure_variable", "phenotype_variable"], suffixes=("_pub", "_pilot"))
print("published candidates:", len(m), "| matched fits:", len(merged))
if len(merged):
    merged["sign_agree"] = np.sign(merged["estimate_pub"]) == np.sign(merged["estimate_pilot"])
    print("sign agreement:", round(float(merged["sign_agree"].mean()), 3))
    print("estimate correlation:", round(float(merged[["estimate_pub", "estimate_pilot"]].corr().iloc[0, 1]), 3))
    sig_agree = (merged["p_value_pub"] < 0.05) == (merged["p_value_pilot"] < 0.05)
    print("significance agreement:", round(float(sig_agree.mean()), 3),
          "| pub sig", int((merged["p_value_pub"] < 0.05).sum()),
          "pilot sig", int((merged["p_value_pilot"] < 0.05).sum()))
    print(merged[["exposure_concept_id", "phenotype_variable", "estimate_pub", "estimate_pilot",
                  "p_value_pub", "p_value_pilot", "sign_agree"]].head(12).to_string())
