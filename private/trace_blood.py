"""Trace why blood outcomes are absent from registry v3."""
import json
import numpy as np
import pandas as pd
import pyreadstat

BASE = "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas"
catalog = json.loads(open(f"{BASE}/code/site-prototype/dist/catalog.json", encoding="utf-8").read())
inv = json.loads(open(f"{BASE}/private/derived_wave_tables/column_inventory.json", encoding="utf-8").read())
cols = set(inv["2011"]["columns"])

blood = [r for r in catalog
         if "2011" in str(r.get("waves", "")).split(",")
         and "p" in {x.strip() for x in str(r.get("epcf", "")).split(",")}
         and str(r.get("category")) == "biochemistry"]
print("blood rows", len(blood), "in table", sum(1 for r in blood if r["Variable.Name"] in cols))
print("example", blood[0]["Variable.Name"], blood[0].get("Concept.Unit.Candidates"))

table = f"{BASE}/private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta"
vars_ = [r["Variable.Name"] for r in blood if r["Variable.Name"] in cols]
df, _ = pyreadstat.read_dta(table, usecols=["bloodweight"] + vars_)
w = pd.to_numeric(df["bloodweight"].replace("", np.nan), errors="coerce")
mask = w.gt(0)
print("sample", int(mask.sum()))
for v in vars_[:3]:
    values = pd.to_numeric(df[v].replace("", np.nan), errors="coerce")
    print(v, "coverage", round(float(values[mask].notna().mean()), 3), "n", int(values[mask].notna().sum()),
          "sd", round(float(values[mask].std()), 3))
