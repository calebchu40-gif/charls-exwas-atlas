"""Inspect dropped exposures to understand the non-numeric classification."""
import pandas as pd
import pyreadstat

BASE = "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private"
diag = pd.read_csv(f"{BASE}/derived_wave_tables/registry_2011_diagnostics.csv")
print(diag["reason"].value_counts())
sample = diag[diag["reason"] == "non_numeric"].head(8)
table = f"{BASE}/derived_wave_tables/CHARLS_wave2011_person_analytic.dta"
cols = ["bloodweight"] + sample["variable"].tolist()
df, _ = pyreadstat.read_dta(table, usecols=[c for c in cols if c])
weight = pd.to_numeric(df["bloodweight"].replace("", None), errors="coerce")
mask = weight > 0
for col in sample["variable"]:
    if col not in df:
        continue
    s = df[col]
    numeric = pd.to_numeric(s.replace("", None), errors="coerce")
    print(col, "dtype", s.dtype, "sample", list(s[mask].head(5)),
          "numeric share (subsample)", round(float(numeric[mask].notna().mean()), 3))
