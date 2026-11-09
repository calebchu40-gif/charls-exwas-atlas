"""Read-only probe: locate education, income, age and birth-date columns by label."""
import json

import pyreadstat

TABLES = {
    "2011": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta",
    "2013": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
    "2015": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
    "2020": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
}

NEEDLES = {
    "edu": ["educat", "education", "bd001", "bd002"],
    "income": ["income", "it0", "it1", "earn"],
    "age": ["age", "rage", "ba004"],
    "birth": ["birth", "ba002", "ba001"],
    "sex": ["gender", "sex", "ba000"],
}

for wave, path in TABLES.items():
    _, meta = pyreadstat.read_dta(path, metadataonly=True)
    labels = dict(zip(meta.column_names, meta.column_labels))
    found = {}
    for key, needles in NEEDLES.items():
        hits = []
        for col, label in labels.items():
            text = f"{col} {label or ''}".lower()
            if any(n in text for n in needles):
                hits.append((col, (label or "")[:40]))
        found[key] = hits[:6]
    print(wave, json.dumps(found, ensure_ascii=False))
