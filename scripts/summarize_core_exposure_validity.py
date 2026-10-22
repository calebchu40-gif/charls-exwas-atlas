"""Codebook-aware, aggregate-only validity audit for core exposure proxies.

Individual records are read only from the private LocalAppData directory. The
outputs are local aggregate counts and value distributions in the private QA directory.
"""
from pathlib import Path
from project_paths import QA_OUTPUT_DIR, WAVE_DATA_DIR
import pandas as pd
import pyreadstat

DATA = WAVE_DATA_DIR
WAVES = ["2011", "2013", "2015", "2018", "2020"]
FIELDS = {
    "smoke_ever": {"2011":"da059","2013":"da059","2015":"da059","2018":"da059","2020":"da046"},
    "still_smoking_among_ever_smokers": {"2011":"da061","2013":"da061","2015":"da061","2018":"da061","2020":"da047"},
    "alcohol_past_year": {"2011":"da067","2013":"da067","2015":"da067","2018":"da067","2020":"da051"},
    "sleep_hours": {"2011":"da049","2013":"da049","2015":"da049","2018":"da049","2020":"da030"},
    "sleep_restless": {"2011":"dc015","2013":"dc015","2015":"dc015","2018":"dc015","2020":"dc022"},
    "vigorous_activity_10min": {"2011":"da051_1_","2013":"da051_1_","2015":"da051_1_","2018":"da051_1_","2020":"da032_1_"},
    "moderate_activity_10min": {"2011":"da051_2_","2013":"da051_2_","2015":"da051_2_","2018":"da051_2_","2020":"da032_2_"},
    "cooking_fuel_main": {"2011":"i022","2013":"i022","2015":"i022","2018":"i022_w4","2020":"i021"},
    "running_water_at_residence": {"2011":"i017","2013":"i017","2015":"i017","2018":"i017"},
}
# Valid semantic ranges confirmed against wave codebooks. Fuel remains nominal;
# categories are counted without asserting cross-wave equivalence.
ALLOWED = {
    "smoke_ever": {w:{1,2} for w in WAVES},
    "still_smoking_among_ever_smokers": {w:{1,2} for w in WAVES}, # 2020 value 3=never smoked, excluded
    "alcohol_past_year": {w:{1,2,3} for w in WAVES},
    "sleep_hours": {w:set(range(0,25)) for w in WAVES},
    "sleep_restless": {w:{1,2,3,4} for w in WAVES},
    "vigorous_activity_10min": {w:{1,2} for w in WAVES},
    "moderate_activity_10min": {w:{1,2} for w in WAVES},
    "cooking_fuel_main": {"2011":set(range(1,8)),"2013":set(range(1,8)),"2015":set(range(1,8)),"2018":set(range(1,9)),"2020":set(range(1,10))},
    "running_water_at_residence": {w:{1,2} for w in WAVES if w != "2020"},
}
LABEL = {
    "smoke_ever":"1=yes; 2=no", "still_smoking_among_ever_smokers":"1=still smoke; 2=quit; 2020 3=never smoked (excluded)",
    "alcohol_past_year":"1=more than once/month; 2=less than once/month; 3=none of these",
    "sleep_hours":"numeric hours; retain 0–24; review extremes; 2020 -1=don't know",
    "sleep_restless":"1–4 CES-D frequency categories; non-1..4 values treated missing",
    "vigorous_activity_10min":"1=yes; 2=no; 2013/2015 are selected-half household modules",
    "moderate_activity_10min":"1=yes; 2=no; 2013/2015 are selected-half household modules",
    "cooking_fuel_main":"wave-specific nominal categories; no numeric trend implied",
    "running_water_at_residence":"1=yes; 2=no; not comparable to 2020 i017 (indoor shower)",
}

def numeric(s):
    return pd.to_numeric(s, errors="coerce")

def valid_mask(concept, wave, series):
    x = numeric(series)
    if concept == "sleep_hours":
        return x.between(0, 24, inclusive="both")
    return x.isin(ALLOWED[concept][str(wave)])

def main():
    summary, values = [], []
    for wave in WAVES:
        path = DATA / f"CHARLS_wave{wave}_person_analytic.dta"
        _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
        available = set(meta.column_names)
        vars_ = sorted({v for c, m in FIELDS.items() for w,v in m.items() if w == wave and v in available})
        df, _ = pyreadstat.read_dta(str(path), usecols=["ID"] + vars_)
        for concept, wave_fields in FIELDS.items():
            var = wave_fields.get(wave, "")
            if not var or var not in available:
                summary.append({"wave":wave,"concept_id":concept,"raw_variable":var,"status":"not_measured","respondent_rows":len(df),"n_nonmissing":None,"n_valid":None,"n_invalid_or_special":None,"valid_pct_of_respondents":None,"codebook_rule":LABEL[concept]})
                continue
            x = numeric(df[var]); nonmissing = x.notna()
            # Fractional sleep hours occur in the released data (for example 6.5).
            valid = nonmissing & valid_mask(concept, wave, df[var])
            summary.append({"wave":wave,"concept_id":concept,"raw_variable":var,"status":"measured","respondent_rows":len(df),"n_nonmissing":int(nonmissing.sum()),"n_valid":int(valid.sum()),"n_invalid_or_special":int((nonmissing & ~valid).sum()),"valid_pct_of_respondents":round(valid.mean()*100,2),"codebook_rule":LABEL[concept]})
            for value, n in x[nonmissing].value_counts().sort_index().items():
                is_valid = (0 <= value <= 24) if concept == "sleep_hours" else (value in ALLOWED[concept][wave])
                values.append({"wave":wave,"concept_id":concept,"raw_variable":var,"raw_value":value,"n":int(n),"valid_under_current_rule":bool(is_valid)})
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summary).to_csv(QA_OUTPUT_DIR/"core_exposure_validity_v1.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(values).to_csv(QA_OUTPUT_DIR/"core_exposure_value_counts_v1.csv",index=False,encoding="utf-8-sig")
    print(pd.DataFrame(summary).groupby(["wave","status"]).size().to_string())
    print(f"rows={len(summary)} value_rows={len(values)}")

if __name__ == "__main__": main()
