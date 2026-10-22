"""Aggregate-only coverage and distributions for demographic covariate candidates."""
from pathlib import Path
from project_paths import QA_OUTPUT_DIR, WAVE_DATA_DIR
import pandas as pd
import pyreadstat

DATA=WAVE_DATA_DIR
WAVES=["2011","2013","2015","2018","2020"]
FIELDS={
 "age_reported_or_derived":{"2011":["ba004"],"2013":["ba004"],"2015":["ba002_1","iyear"],"2018":["ba002_1","iyear"],"2020":["xrage"]},
 "gender":{"2011":["rgender"],"2013":["xrgender"],"2015":["xrgender"],"2018":["xrgender"],"2020":["xrgender"]},
 "education_attainment":{"2011":["bd001"],"2013":["bd001"],"2015":["bd001_w2_4"],"2018":["bd001_w2_4"],"2020":["ba010"]},
 "education_prior_or_route":{"2011":[],"2013":["zbd001","bd001_w2_4"],"2015":["bd001_w2_4"],"2018":["bd001_w2_4"],"2020":["zredu"]},
 "marital_status":{"2011":["be001"],"2013":["be001"],"2015":["be001"],"2018":["be001"],"2020":["ba011"]},
 "hukou_type":{"2011":["bc001"],"2013":["bc001"],"2015":["bc002_w3_1"],"2018":["bc002_w3_1"],"2020":["ba009"]},
 "hukou_prior_or_change_route":{"2011":[],"2013":["zbc001","bc001_w2_1"],"2015":["bc001_w3_2","bc002_w3"],"2018":["bc001_w3_2","bc002_w3"],"2020":[]},
 "urbanicity_context":{"2011":["urban_nbs"],"2013":["urban_nbs"],"2015":["bb001_w3_2"],"2018":["bb001_w3_2"],"2020":["ba008"]},
}
NOTES={
 "age_reported_or_derived":"2011/2013 BA004 is a sparse fallback only (34/69 raw nonblank); 2015/2018 DOB-year fields are route-limited. Use interview/birth year+month with lunar-date processing or audited H-D RwAGEY; 2020 CHARLS-generated XRAge.",
 "gender":"CHARLS-generated/current respondent gender field; verify against interview confirmation and preserve gender-conflict flags.",
 "education_attainment":"2015/2018 field includes 'no change' code and must be recursively resolved using prior-wave attainment; 2020 question excludes adult education.",
 "education_prior_or_route":"Prior attainment preload and/or changed-this-wave response needed to reconstruct state; 2020 ZREdu is a released preload (17,687 rows), disjoint from current BA010 and exactly matches linked 2018 state in ID-level aggregate QA.",
 "marital_status":"Current status categories; 2020 wording and co-resident partner supplements may differ.",
 "hukou_type":"Current registration type; 2015/2018 asks value on change route, so combine with prior status when unchanged.",
 "hukou_prior_or_change_route":"Prior hukou and change-route fields support carry-forward; inspect status-specific codes and unresolved/refused values before using.",
 "urbanicity_context":"2011/2013 urban_nbs is NBS classification of sampled PSU/community, not a direct individual residence report; 2015/2018 bb001_w3_2 and 2020 ba008 describe respondent current residential location with non-identical category sets.",
}

def observed(x):
 return x.notna() & x.astype(str).str.strip().ne("")

def main():
 rows=[]; dist=[]
 for w in WAVES:
  p=DATA/f"CHARLS_wave{w}_person_analytic.dta"
  _,m=pyreadstat.read_dta(str(p),metadataonly=True); names=m.column_names
  needed=sorted({v for mp in FIELDS.values() for ww,vs in mp.items() if ww==w for v in vs if v in names})
  d,_=pyreadstat.read_dta(str(p),usecols=["ID"]+needed)
  for concept,wm in FIELDS.items():
   vs=wm.get(w,[]); present=[v for v in vs if v in d]
   if not present:
    rows.append({"wave":w,"concept_id":concept,"source_variables":"|".join(vs),"status":"not_available","respondent_n":len(d),"n_raw_available":None,"n_constructed_candidate":None,"candidate_min":None,"candidate_median":None,"candidate_max":None,"definition_note":NOTES[concept]}); continue
   if concept=="age_reported_or_derived" and len(present)==2 and "iyear" in present:
    yr=pd.to_numeric(d[present[0]],errors="coerce"); iy=pd.to_numeric(d["iyear"],errors="coerce"); val=iy-yr
    nraw=int((yr.notna()&iy.notna()).sum()); nconstruct=int(val.notna().sum()); lo=val.min(); med=val.median(); hi=val.max()
    rows.append({"wave":w,"concept_id":concept,"source_variables":"|".join(present),"status":"year_difference_candidate_not_final_age","respondent_n":len(d),"n_raw_available":nraw,"n_constructed_candidate":nconstruct,"candidate_min":float(lo) if pd.notna(lo) else None,"candidate_median":float(med) if pd.notna(med) else None,"candidate_max":float(hi) if pd.notna(hi) else None,"definition_note":NOTES[concept]})
   else:
    x=d[present[0]]; n=int(observed(x).sum()); numeric=pd.to_numeric(x,errors="coerce")
    rows.append({"wave":w,"concept_id":concept,"source_variables":"|".join(present),"status":"raw_field_candidate_not_harmonized","respondent_n":len(d),"n_raw_available":n,"n_constructed_candidate":None,"candidate_min":None,"candidate_median":None,"candidate_max":None,"definition_note":NOTES[concept]})
    if concept != "age_reported_or_derived":
     for rawvar in present:
      vals=pd.to_numeric(d[rawvar],errors="coerce")
      for value,count in vals[observed(d[rawvar])].value_counts(dropna=True).sort_index().items():
       if int(count)>=5: # suppress very small category counts in synced aggregate artifacts
        dist.append({"wave":w,"concept_id":concept,"raw_variable":rawvar,"raw_value":value,"n":int(count)})
 QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 pd.DataFrame(rows).to_csv(QA_OUTPUT_DIR/"covariate_candidate_availability_v1.csv",index=False,encoding="utf-8-sig")
 pd.DataFrame(dist).to_csv(QA_OUTPUT_DIR/"covariate_candidate_value_counts_v1.csv",index=False,encoding="utf-8-sig")
 print("availability rows",len(rows),"value count rows",len(dist))

if __name__=="__main__": main()
