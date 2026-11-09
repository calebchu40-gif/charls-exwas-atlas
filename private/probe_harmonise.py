"""Read-only probe: check harmonisation candidates for age, sex, education, urban."""
import pyreadstat

TABLES = {
    "2011": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta",
    "2013": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
    "2015": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
    "2020": "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
}

CANDIDATES = ["xrage", "rage", "ba004", "ba004_w3", "ba004_w3_1", "ba003_1",
              "rgender", "xrgender", "zrgender", "xr20gender", "ba000_w2_3",
              "bd001", "zbd001", "bd001_w2_4", "ba010", "bd002_w3",
              "urban_nbs", "bb001_w3_2", "ba008", "bb000_w3_2",
              "ga001", "it001", "it002", "hh_income"]

for wave, path in TABLES.items():
    _, meta = pyreadstat.read_dta(path, metadataonly=True)
    cols = set(meta.column_names)
    labels = dict(zip(meta.column_names, meta.column_labels))
    hits = [(c, (labels.get(c) or "")[:44]) for c in CANDIDATES if c in cols]
    print(wave, "|", "; ".join(f"{c}:{l}" for c, l in hits))
