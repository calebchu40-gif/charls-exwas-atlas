"""Read-only probe: list education/age/urban candidate columns with labels by wave."""
import pyreadstat

TABLES = {
    "2011": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta",
    "2013": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
    "2015": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
    "2020": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
}

PATTERNS = ["education", "school", "literate", "highest level", "birth", "age",
            "village", "city", "urban", "interview year", "interview date"]

for wave, path in TABLES.items():
    _, meta = pyreadstat.read_dta(path, metadataonly=True)
    labels = dict(zip(meta.column_names, meta.column_labels))
    print("==", wave)
    shown = 0
    for col, label in labels.items():
        text = f"{col} {label or ''}".lower()
        if any(p in text for p in PATTERNS):
            print("  ", col, "|", (label or "")[:64])
            shown += 1
            if shown >= 18:
                print("   ...")
                break
