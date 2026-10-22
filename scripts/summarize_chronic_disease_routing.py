#!/usr/bin/env python3
"""Aggregate-only audit of chronic-disease answers by interview route/preload."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import pyreadstat

DISEASES = {"hypertension": 1, "dyslipidemia": 2, "diabetes": 3,
            "chronic_lung": 5, "heart_disease": 7, "stroke": 8,
            "kidney_disease": 9, "arthritis": 13}
WAVES = (2013, 2015, 2018, 2020)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    rows = []
    for wave in WAVES:
        path = a.data_dir / f"CHARLS_wave{wave}_person_analytic.dta"
        _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
        names = set(meta.column_names)
        xrtype = "xrtype" if "xrtype" in names else None
        for disease, idx0 in DISEASES.items():
            idx = 14 if wave == 2020 and disease == "arthritis" else idx0
            raw = f"da003_{idx}_" if wave == 2020 else f"da007_{idx}_"
            preload = f"zdisease_{idx}_" if wave in (2018, 2020) else None
            check = f"da007_w2_1_{idx}_" if wave in (2013, 2015) else None
            interval = f"da007_w2_2_{idx}_" if wave in (2013, 2015) else None
            cols = [c for c in (raw, xrtype, preload, check, interval) if c and c in names]
            if raw not in cols:
                rows.append(dict(wave=wave, disease=disease, status="raw_field_missing"))
                continue
            d, _ = pyreadstat.read_dta(str(path), usecols=cols)
            group_cols = [x for x in (xrtype, preload, raw, check, interval) if x and x in d]
            for key, g in d.groupby(group_cols, dropna=False, observed=True):
                vals = dict(zip(group_cols, key if isinstance(key, tuple) else (key,)))
                rows.append({"wave": wave, "disease": disease,
                    "xrtype": vals.get(xrtype), "preload": vals.get(preload),
                    "raw_response": vals.get(raw), "returner_validation": vals.get(check),
                    "interval_new_diagnosis": vals.get(interval), "n": len(g),
                    "status": "aggregate_route_cross_tab_only"})
    a.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(a.out, index=False)

if __name__ == "__main__":
    main()
