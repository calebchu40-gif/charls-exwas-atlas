"""Write per-wave column inventories for registry construction (read-only)."""
import json

import pyreadstat

TABLES = {
    "2011": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta",
    "2013": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
    "2015": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
    "2020": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
}

out = {}
for wave, path in TABLES.items():
    _, meta = pyreadstat.read_dta(path, metadataonly=True)
    out[wave] = {
        "rows": meta.number_rows,
        "columns": list(meta.column_names),
        "labels": {c: (l or "") for c, l in zip(meta.column_names, meta.column_labels)},
    }

with open("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/column_inventory.json", "w", encoding="utf-8") as handle:
    json.dump(out, handle, ensure_ascii=False)
print({wave: len(info["columns"]) for wave, info in out.items()})
