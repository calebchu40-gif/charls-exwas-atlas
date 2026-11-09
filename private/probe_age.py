"""Read-only probe: birth-year fields and derived age sanity check."""
import pyreadstat
import numpy as np

SPECS = {
    "2011": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta",
             ["ba002_1", "ba004"], 2011),
    "2013": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
             ["zba002_1", "ba002_1", "ba004"], 2013),
    "2015": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
             ["ba004_w3_1", "iyear"], 2015),
    "2018": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
             ["ba004_w3_1", "iyear"], 2018),
    "2020": ("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
             ["xrage", "ba003_1"], 2020),
}

for wave, (path, cols, survey_year) in SPECS.items():
    _, meta = pyreadstat.read_dta(path, metadataonly=True)
    present = [c for c in cols if c in meta.column_names]
    df, _ = pyreadstat.read_dta(path, usecols=present)
    print("==", wave, present)
    for col in present:
        values = df[col].replace("", np.nan).astype(float)
        print("  ", col, "nonmissing", int(values.notna().sum()),
              "min", values.min(), "max", values.max())
    if "xrage" in present:
        age = df["xrage"].replace("", np.nan).astype(float)
    elif "ba004" in present and df["ba004"].replace("", np.nan).notna().sum() > 1000:
        age = df["ba004"].replace("", np.nan).astype(float)
    elif "ba002_1" in present:
        age = survey_year - df["ba002_1"].replace("", np.nan).astype(float)
    elif "zba002_1" in present:
        age = survey_year - df["zba002_1"].replace("", np.nan).astype(float)
    elif "ba004_w3_1" in present and "iyear" in present:
        age = df["iyear"].replace("", np.nan).astype(float) - df["ba004_w3_1"].replace("", np.nan).astype(float)
    elif "ba003_1" in present:
        age = survey_year - df["ba003_1"].replace("", np.nan).astype(float)
    else:
        age = None
    if age is not None:
        age = age[(age >= 18) & (age <= 110)]
        print("   derived age: n", int(age.notna().sum()), "mean", round(float(age.mean()), 1),
              "median", round(float(age.median()), 1))
