"""Read-only probe: distributions of education/urban/age candidates."""
import pyreadstat

SPECS = {
    "2011": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta",
             ["bd001", "urban_nbs", "ba004", "rgender"]),
    "2013": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
             ["zbd001", "bd001", "urban_nbs", "ba004", "xrgender"]),
    "2015": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
             ["bd001_w2_4", "bd001_w2_1", "bb001_w3_2", "ba004_w3_1", "iyear", "xrgender"]),
    "2018": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
             ["bd001_w2_4", "bb001_w3_2", "ba004_w3_1", "iyear", "xrgender"]),
    "2020": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
             ["ba010", "ba008", "xrage", "xrgender"]),
}

for wave, (path, cols) in SPECS.items():
    kwargs = dict(metadataonly=True)
    _, meta = pyreadstat.read_dta(path, **kwargs)
    present = [c for c in cols if c in meta.column_names]
    print("==", wave, "present:", present)
    if not present:
        continue
    df, _ = pyreadstat.read_dta(path, usecols=present)
    for col in present:
        counts = df[col].value_counts(dropna=False).head(12)
        print("  ", col, dict(counts))
