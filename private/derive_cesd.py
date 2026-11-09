"""Derive the CES-D 10-item score for every wave.

Items 2011-2018: dc009..dc018; 2020 shifts by seven to dc016..dc025.
Positive-affect items (happy, hopeful) are reverse scored.  A score needs at
least eight valid items; responses outside 1-4 are treated as missing.
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
    "2020": f"{BASE}/CHARLS_wave2020_person_analytic.dta",
}
ITEMS = {
    "2011": ["dc009", "dc010", "dc011", "dc012", "dc013", "dc014", "dc015", "dc016", "dc017", "dc018"],
    "2013": ["dc009", "dc010", "dc011", "dc012", "dc013", "dc014", "dc015", "dc016", "dc017", "dc018"],
    "2015": ["dc009", "dc010", "dc011", "dc012", "dc013", "dc014", "dc015", "dc016", "dc017", "dc018"],
    "2018": ["dc009", "dc010", "dc011", "dc012", "dc013", "dc014", "dc015", "dc016", "dc017", "dc018"],
    "2020": ["dc016", "dc017", "dc018", "dc019", "dc020", "dc021", "dc022", "dc023", "dc024", "dc025"],
}
REVERSE = {"dc013", "dc016", "dc020", "dc023"}  # hopeful/happy items


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace("", np.nan), errors="coerce")


def main() -> None:
    for wave, table in TABLES.items():
        items = ITEMS[wave]
        df, _ = pyreadstat.read_dta(table, usecols=["ID"] + items)
        values = pd.DataFrame({item: numeric(df[item]) for item in items})
        values = values.where(values.isin([1, 2, 3, 4]))
        for item in REVERSE & set(items):
            values[item] = 5 - values[item]
        score = (values - 1).sum(axis=1, skipna=True)
        valid = values.notna().sum(axis=1)
        score = score.where(valid >= 8)
        out = pd.DataFrame({"ID": df["ID"].astype(str).str.strip(), "cesd_score": score})
        out.to_csv(f"{BASE}/outcomes_wave{wave}.csv", index=False)
        print(json.dumps({"wave": wave, "n": int(out["cesd_score"].notna().sum()),
                          "mean": round(float(out["cesd_score"].mean()), 2),
                          "sd": round(float(out["cesd_score"].std()), 2),
                          "max": int(out["cesd_score"].max())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
