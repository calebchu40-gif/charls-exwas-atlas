"""Debug coverage computation for registry v3."""
import numpy as np
import pandas as pd
import pyreadstat

TABLE = "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta"
cols = ["bloodweight", "ind_weight", "qc1_vb002", "i022", "da059", "da007_1_"]
df, _ = pyreadstat.read_dta(TABLE, usecols=[c for c in cols])

for weight_col in ("bloodweight", "ind_weight"):
    w = pd.to_numeric(df[weight_col].replace("", np.nan), errors="coerce")
    print(weight_col, "nonmissing", int(w.notna().sum()), "positive", int(w.gt(0).sum()), "median", float(w.median()))
    mask = w.gt(0)
    for col in ("qc1_vb002", "i022", "da059", "da007_1_"):
        v = pd.to_numeric(df[col].replace("", np.nan), errors="coerce")
        print("   ", col, "coverage in sample", round(float(v[mask].notna().mean()), 3),
              "n", int(v[mask].notna().sum()))
