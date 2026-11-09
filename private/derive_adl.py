"""Derive ADL and IADL limitation indicators (2011-2018).

ADL items db010-db015 (dressing, bathing, eating, bed, toilet, continence);
IADL items db016-db020 (chores, cooking, shopping, assets, medication).
Codes: 1 = no difficulty, 2 = yes difficulty, 3 = cannot do, 4 = not applicable.
A wave-level indicator needs at least four valid items; 4 is treated as missing.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pyreadstat

BASE = "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables"
TABLES = {
    "2011": f"{BASE}/CHARLS_wave2011_person_analytic.dta",
    "2013": f"{BASE}/CHARLS_wave2013_person_analytic.dta",
    "2015": f"{BASE}/CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": f"{BASE}/CHARLS_wave2018_person_analytic.dta",
}
ADL = ["db010", "db011", "db012", "db013", "db014", "db015"]
IADL = ["db016", "db017", "db018", "db019", "db020"]


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace("", np.nan), errors="coerce")


def main() -> None:
    for wave, table in TABLES.items():
        df, _ = pyreadstat.read_dta(table, usecols=["ID"] + ADL + IADL)
        out = pd.DataFrame({"ID": df["ID"].astype(str).str.strip()})
        for name, items in (("adl", ADL), ("iadl", IADL)):
            values = pd.DataFrame({item: numeric(df[item]) for item in items})
            values = values.where(values.isin([1, 2, 3]))
            limitation = (values.isin([2, 3])).sum(axis=1)
            valid = values.notna().sum(axis=1)
            out[f"{name}_any"] = np.where(valid >= 4, (limitation > 0).astype(float), np.nan)
            out[f"{name}_count"] = np.where(valid >= 4, limitation.astype(float), np.nan)
        out.to_csv(f"{BASE}/outcomes_{wave}.csv", index=False)
        print(json.dumps({
            "wave": wave,
            "adl_n": int(out["adl_any"].notna().sum()),
            "adl_rate": round(float(out["adl_any"].mean()), 3),
            "iadl_n": int(out["iadl_any"].notna().sum()),
            "iadl_rate": round(float(out["iadl_any"].mean()), 3),
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
