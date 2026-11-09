"""Read-only probe: identifier and education columns per wave."""
import pyreadstat

TABLES = {
    "2015": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
    "2020": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
}

for wave, path in TABLES.items():
    _, meta = pyreadstat.read_dta(path, metadataonly=True)
    labels = dict(zip(meta.column_names, meta.column_labels))
    print("==", wave)
    ids = [c for c in meta.column_names if c.lower() in {"id", "pid", "hhid", "householdid", "personid", "idauniq"}]
    print("  ids:", ids)
    bd = [c for c in meta.column_names if c.startswith("bd001") or c.startswith("zbd001") or c == "ba010"]
    for c in bd:
        print("  ", c, "|", (labels.get(c) or "")[:60])
