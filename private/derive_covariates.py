"""Derive harmonised covariates for every wave (private, read-only inputs).

Outputs (private/derived_wave_tables/covariates_wave{YYYY}.csv):
    ID, age, female, edu4, urban, iyear

Rules
-----
age    : 2011 = 2011 - ba002_1; 2013 = 2013 - zba002_1; 2015/2018 = iyear - ba004_w3_1;
         2020 = xrage
female : 1 when the gender code is 2 (CHARLS codes 1=male, 2=female)
edu4   : 1 below primary (codes 1-3), 2 primary (4), 3 middle (5), 4 high school+ (>=6)
         2015 bd001_w2_4 == 12 means "unchanged": carry the 2013 level by ID
         2020 ba010 is sparse: carry the 2018 level by ID when missing
urban  : 2011/2013 urban_nbs; 2015/2018 bb001_w3_2 in {1,2}; 2020 ba008 in {1,2}
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pyreadstat

BASE = "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/derived_wave_tables"
TABLES = {
    "2011": f"{BASE}/CHARLS_wave2011_person_analytic.dta",
    "2013": f"{BASE}/CHARLS_wave2013_person_analytic.dta",
    "2015": f"{BASE}/CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": f"{BASE}/CHARLS_wave2018_person_analytic.dta",
    "2020": f"{BASE}/CHARLS_wave2020_person_analytic.dta",
}
SURVEY_YEAR = {"2011": 2011, "2013": 2013, "2015": 2015, "2018": 2018, "2020": 2020}


def num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace("", np.nan), errors="coerce")


def edu4_from_codes(values: pd.Series) -> pd.Series:
    v = num(values)
    out = pd.Series(np.nan, index=v.index)
    out[v.isin([1, 2, 3])] = 1
    out[v == 4] = 2
    out[v == 5] = 3
    out[v >= 6] = 4
    return out


def main() -> None:
    frames: dict[str, pd.DataFrame] = {}
    for wave, path in TABLES.items():
        cols = ["ID", "rgender", "xrgender", "ba004", "ba002_1", "zba002_1",
                "ba004_w3_1", "iyear", "xrage", "bd001", "zbd001", "bd001_w2_4",
                "urban_nbs", "bb001_w3_2", "ba008", "ba010"]
        _, meta = pyreadstat.read_dta(path, metadataonly=True)
        use = [c for c in cols if c in meta.column_names]
        df, _ = pyreadstat.read_dta(path, usecols=use)
        frame = pd.DataFrame({"ID": df["ID"].astype(str).str.strip()})

        # age
        if wave == "2011":
            frame["age"] = SURVEY_YEAR[wave] - num(df["ba002_1"])
        elif wave == "2013":
            frame["age"] = SURVEY_YEAR[wave] - num(df["zba002_1"])
        elif wave in {"2015", "2018"}:
            frame["age"] = num(df["iyear"]) - num(df["ba004_w3_1"])
        else:
            frame["age"] = num(df["xrage"])
        frame.loc[(frame["age"] < 18) | (frame["age"] > 110), "age"] = np.nan

        # sex
        sex = num(df["xrgender"]) if "xrgender" in df else num(df["rgender"])
        frame["female"] = np.where(sex == 2, 1, np.where(sex == 1, 0, np.nan))

        # education
        if wave == "2011":
            frame["edu4"] = edu4_from_codes(df["bd001"])
        elif wave == "2013":
            frame["edu4"] = edu4_from_codes(df["zbd001"])
        elif wave == "2015":
            changed = num(df["bd001_w2_4"])
            explicit = edu4_from_codes(df["bd001_w2_4"])
            frame["edu4"] = explicit
            frame["_needs_carry"] = changed == 12
        elif wave == "2018":
            frame["edu4"] = edu4_from_codes(df["bd001_w2_4"])
        else:
            frame["edu4"] = edu4_from_codes(df["ba010"])

        # urban
        if "urban_nbs" in df:
            frame["urban"] = num(df["urban_nbs"])
        elif "bb001_w3_2" in df:
            v = num(df["bb001_w3_2"])
            frame["urban"] = np.where(v.isin([1, 2]), 1, np.where(v.isin([3, 4, 5, 6, 7, 8]), 0, np.nan))
        elif "ba008" in df:
            v = num(df["ba008"])
            frame["urban"] = np.where(v.isin([1, 2]), 1, np.where(v.isin([3, 4]), 0, np.nan))

        frame["iyear"] = num(df["iyear"]) if "iyear" in df else SURVEY_YEAR[wave]
        frames[wave] = frame
        print(wave, "rows", len(frame), "age", int(frame["age"].notna().sum()),
              "female", int(frame["female"].notna().sum()),
              "edu4", int(frame["edu4"].notna().sum()),
              "urban", int(frame["urban"].notna().sum()))

    # carry education forward where the wave records "unchanged"
    edu13 = frames["2013"].set_index("ID")["edu4"]
    needs = frames["2015"]["_needs_carry"].fillna(False)
    carried = frames["2015"]["ID"].map(edu13)
    frames["2015"].loc[needs, "edu4"] = carried[needs]
    print("2015 carry from 2013:", int(needs.sum()), "filled",
          int(frames["2015"].loc[needs, "edu4"].notna().sum()))

    edu18 = frames["2018"].set_index("ID")["edu4"]
    missing20 = frames["2020"]["edu4"].isna()
    carried20 = frames["2020"]["ID"].map(edu18)
    frames["2020"].loc[missing20, "edu4"] = carried20[missing20]
    print("2020 carry from 2018:", int(missing20.sum()), "filled",
          int(frames["2020"].loc[missing20, "edu4"].notna().sum()))

    for wave, frame in frames.items():
        out = frame[["ID", "age", "female", "edu4", "urban", "iyear"]].copy()
        path = f"{BASE}/covariates_wave{wave}.csv"
        out.to_csv(path, index=False)
        print("wrote", path, len(out))


if __name__ == "__main__":
    main()
