"""Summarize household expenditure candidate coverage without person records."""
from pathlib import Path
from project_paths import WAVE_DATA_DIR
import pandas as pd
import pyreadstat

DATA=WAVE_DATA_DIR
PROJECT=Path(__file__).resolve().parents[1]
# Periods verified against the CHARLS wave questionnaires. Monetary values are
# left on their original scale; this script only audits metadata and coverage.
FIELDS={
 2011:{"ge006":("weekly_component","past week"),"ge007":("weekly_component","past week"),"ge008":("weekly_component","past week"),
       **{f"ge009_{i}":("monthly_component","past month") for i in range(1,4)},
       **{f"ge010_{i}":("monthly_component","past month") for i in range(1,15)}},
 2013:{"ge006":("weekly_component","past week"),"ge007":("weekly_component","past week"),"ge008":("weekly_component","past week"),
       "ge006_w2":("self_production_indicator","current questionnaire route"),"ge006_w2_1":("self_produced_food_value","past week market value"),
       **{f"ge009_{i}":("monthly_component","past month") for i in range(1,4)},
       **{f"ge010_{i}":("monthly_component","past month") for i in range(1,14)}},
 2015:{"ge006":("weekly_component","past week"),"ge007":("weekly_component","past week"),"ge008":("weekly_component","past week"),
       "ge006_w2":("self_production_indicator","current questionnaire route"),"ge006_w2_1":("self_produced_food_value","past week market value"),
       **{f"ge009_{i}":("monthly_component","past month") for i in range(1,4)},
       **{f"ge010_{i}":("monthly_component","past month") for i in range(1,14)}},
 2018:{"ge000_w4":("monthly_total","monthly"),"ge006_w4":("weekly_component","past week"),"ge007_w4":("weekly_component","past week"),"ge008":("weekly_component","past week"),
       "ge006_w2":("self_production_indicator","current questionnaire route"),"ge006_w2_1":("self_produced_food_value","past week market value"),
       **{f"ge009_{i}":("monthly_component","past month") for i in range(1,4)},
       **{f"ge010_{i}":("monthly_component","past month") for i in range(1,16)}},
 2020:{"gf001":("monthly_total","monthly"),"gf006":("weekly_component","past week"),"gf009":("weekly_component","past week"),"gf010":("weekly_component","past week"),
       "gf007":("self_production_indicator","current questionnaire route"),"gf008":("self_produced_food_value","past week market value"),
       **{f"gf013_{i}":("monthly_component","past month") for i in range(1,17)}},
}

def main():
 rows=[]
 for w,field_meta in FIELDS.items():
  fields=list(field_meta)
  p=DATA/f"CHARLS_wave{w}_person_analytic.dta"
  _,meta=pyreadstat.read_dta(str(p),metadataonly=True)
  use=["ID","householdID"]+[f for f in fields if f in meta.column_names]
  d,_=pyreadstat.read_dta(str(p),usecols=use)
  for f in fields:
   if f not in d: continue
   numeric=pd.to_numeric(d[f],errors="coerce")
   # Some Wave 5 expenditure values are strings; blank strings are missing.
   present=d[f].notna()
   if pd.api.types.is_object_dtype(d[f].dtype) or pd.api.types.is_string_dtype(d[f].dtype):
    present=present & d[f].astype("string").str.strip().ne("")
   role,period=field_meta[f]
   rows.append({"wave":w,"variable":f,"label":meta.column_labels[meta.column_names.index(f)],"candidate_role":role,"reference_period":period,
                "respondent_rows":len(d),"respondents_raw_nonmissing_n":int(present.sum()),
                "households_raw_nonmissing_n":int(d.loc[present,"householdID"].nunique()),
                "negative_value_n":int((numeric<0).sum()),
                "scope_note":"Raw nonmissing/negative count only; household values may repeat across respondents. Components are not summed and no inflation, household-size or special-code adjustment is applied."})
 out=pd.DataFrame(rows)
 out.to_csv(PROJECT/"audit"/"household_ses_field_coverage_v1.csv",index=False,encoding="utf-8-sig")
 print(out[["wave","candidate_role","variable","respondents_raw_nonmissing_n","households_raw_nonmissing_n","negative_value_n"]].to_string(index=False))

if __name__=="__main__":main()
