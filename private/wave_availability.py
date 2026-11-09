"""Count non-missing observations for every catalogued E/P variable in one wave.

Usage: python wave_availability.py 2015
Writes private/derived_wave_tables/availability_{wave}.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
CATALOG = BASE / "code" / "site-prototype" / "dist" / "catalog.json"
TABLES = {
    "2011": BASE / "private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta",
    "2013": BASE / "private/derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
    "2015": BASE / "private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": BASE / "private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
    "2020": BASE / "private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
}
DESIGNS = {wave: json.loads((BASE / "private" / f"design_{wave}.json").read_text(encoding="utf-8"))
           for wave in TABLES}


def roles(row: dict) -> set[str]:
    return {part.strip() for part in str(row.get("epcf", "")).split(",") if part.strip()}


def main(wave: str) -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    table = TABLES[wave]
    weight = DESIGNS[wave]["weight"]

    _, meta = pyreadstat.read_dta(table, metadataonly=True)
    present = set(meta.column_names)
    wanted = []
    for row in catalog:
        if wave not in str(row.get("waves", "")).split(","):
            continue
        if not ({"e", "p"} & roles(row)):
            continue
        if "DO NOT ANALYZE" in str(row.get("Review.Flag", "")) + str(row.get("value_labels", "")):
            continue
        variable = str(row.get("Variable.Name", "")).strip()
        if variable in present:
            wanted.append(variable)
    wanted = sorted(set(wanted))

    df, _ = pyreadstat.read_dta(table, usecols=["ID", weight] + wanted)
    values = df[wanted].replace("", np.nan)
    numeric = values.apply(pd.to_numeric, errors="coerce")
    weight_values = pd.to_numeric(df[weight].replace("", np.nan), errors="coerce")
    sample = weight_values.gt(0)

    result = {}
    for variable in wanted:
        total = int(numeric[variable].notna().sum())
        in_sample = int(numeric.loc[sample, variable].notna().sum())
        result[variable] = {"n": total, "n_sample": in_sample}

    out = BASE / "private" / "derived_wave_tables" / f"availability_{wave}.json"
    out.write_text(json.dumps({"wave": wave, "weight": weight, "rows": int(len(df)),
                               "variables": result}, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"wave": wave, "variables": len(result), "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
