"""Read-only readiness probe: list weight/PSU/covariate columns in each analytic table."""
import json
import sys

import pyreadstat

TABLES = {
    "2011": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta",
    "2013": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
    "2015": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
    "2020": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
}

KEYS = ["weight", "psu", "community", "age", "sex", "gender", "edu", "income", "urban",
        "birth", "fast", "stratum", "strata", "indv", "blood"]

out = {}
for wave, path in TABLES.items():
    try:
        _, meta = pyreadstat.read_dta(path, metadataonly=True)
    except Exception as exc:  # pragma: no cover - readiness probe
        out[wave] = {"error": str(exc)}
        continue
    cols = list(meta.column_names)
    hits = sorted({c for c in cols if any(k in c.lower() for k in KEYS)})
    out[wave] = {"rows": meta.number_rows, "columns": meta.number_columns, "candidates": hits[:40]}

for wave, info in out.items():
    if "error" in info:
        print(wave, "ERROR", info["error"]); continue
    cols = [c.lower() for c in info["candidates"]]
    def has(*needles):
        return any(any(n in c for n in needles) for c in cols)
    print(wave, "rows", info["rows"], "cols", info["columns"],
          "| weight", has("weight"), "| psu", has("community"), "| sex", has("gender", "rgender"),
          "| urban", has("urban"), "| edu", has("edu"), "| income", has("income"),
          "| birth", has("birth"))
