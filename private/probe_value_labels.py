"""Read-only probe: value labels for education and urban variables by wave."""
import pyreadstat

TABLES = {
    "2011": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta",
             ["bd001", "urban_nbs"]),
    "2013": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
             ["zbd001", "bd001", "urban_nbs"]),
    "2015": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
             ["bd001_w2_4", "bb001_w3_2", "bb000_w3_2"]),
    "2018": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
             ["bd001_w2_4", "bb001_w3_2"]),
    "2020": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
             ["ba010", "ba008"]),
}

for wave, (path, cols) in TABLES.items():
    _, meta = pyreadstat.read_dta(path, metadataonly=True)
    print("==", wave)
    for col in cols:
        if col not in meta.column_names:
            continue
        vl = meta.variable_value_labels.get(col)
        vls = meta.variable_to_label.get(col)
        print("  ", col, "|", (dict(zip(meta.column_names, meta.column_labels)).get(col) or "")[:50])
        if vl:
            print("      codes:", sorted(vl.items())[:14])
