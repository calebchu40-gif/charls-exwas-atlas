"""Debug why blood outcomes fail the numeric check."""
import numpy as np
import pandas as pd
import pyreadstat

TABLE = "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta"
cols = ["qc1_vb002", "newhba1c", "qc1_vb001", "bloodweight"]
df, _ = pyreadstat.read_dta(TABLE, usecols=[c for c in cols])
for col in df.columns:
    s = df[col]
    numeric = pd.to_numeric(s.replace("", np.nan), errors="coerce")
    print(col, "dtype", s.dtype, "head", list(s.head(6)), "numeric share", round(float(numeric.notna().mean()), 3))
