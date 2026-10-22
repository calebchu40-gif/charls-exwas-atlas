"""Aggregate QA for CHARLS age candidates against Harmonized CHARLS D.

This is an external harmonization reference, not a gold standard. The 2011 ID
adjustment follows the official Wave 2 release note; IDs never leave memory.
"""
from pathlib import Path
import os
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path
import pandas as pd
import pyreadstat

DATA=WAVE_DATA_DIR
HARM=require_private_path(Path(os.environ.get("CHARLS_HARMONIZED_D_PATH", str(PRIVATE_ROOT / "references" / "H_CHARLS_D_Data.dta"))))
WAVES=[2011,2013,2015,2018]

def norm(x):
 if pd.isna(x): return None
 s=str(x).strip()
 return s[:-2] if s.endswith('.0') and s[:-2].isdigit() else (s or None)

def age_ref_id(x,w):
 s=norm(x)
 if not s: return None
 # CHARLS 2013 Wave 2 release note: add a zero to the 9-digit baseline
 # household ID before appending the last two individual-ID digits.
 if w==2011 and len(s)==11 and s.isdigit(): return s[:9]+'0'+s[9:]
 return s

def main():
 _,hm=pyreadstat.read_dta(str(HARM),metadataonly=True)
 hcols=['ID']+[f'r{i}agey' for i in range(1,5) if f'r{i}agey' in hm.column_names]
 h,_=pyreadstat.read_dta(str(HARM),usecols=hcols); h['_join']=h.ID.map(norm); h=h.dropna(subset=['_join']).drop_duplicates('_join')
 result=[]
 for i,w in enumerate(WAVES,1):
  path=DATA/f'CHARLS_wave{w}_person_analytic.dta'; _,m=pyreadstat.read_dta(str(path),metadataonly=True)
  candidates=['ID','ba004','ba002_1','ba002_2','ba003','iyear','imonth']
  d,_=pyreadstat.read_dta(str(path),usecols=[x for x in candidates if x in m.column_names]); d['_join']=d.ID.map(lambda x:age_ref_id(x,w))
  j=d.merge(h[['_join',f'r{i}agey']],on='_join',how='left',validate='one_to_one')
  ref=pd.to_numeric(j[f'r{i}agey'],errors='coerce'); matched=ref.notna()
  raw_age=pd.to_numeric(j['ba004'],errors='coerce') if 'ba004' in j else pd.Series(float('nan'),index=j.index)
  raw_year=pd.to_numeric(j['ba002_1'],errors='coerce') if 'ba002_1' in j else pd.Series(float('nan'),index=j.index)
  interview_year=pd.to_numeric(j['iyear'],errors='coerce') if 'iyear' in j else pd.Series(float('nan'),index=j.index)
  approx=interview_year-raw_year
  direct=raw_age.notna()&matched
  approx_overlap=approx.notna()&matched
  result.append({"wave":w,"respondent_rows":len(j),"id_rows_with_reference_age":int(matched.sum()),
   "reference_age_valid_45plus":int((matched&ref.ge(45)).sum()),"reference_age_min":float(ref[matched].min()) if matched.any() else None,
   "reference_age_median":float(ref[matched].median()) if matched.any() else None,"reference_age_max":float(ref[matched].max()) if matched.any() else None,
   "direct_age_reference_overlap_n":int(direct.sum()),"direct_age_exact_match_n":int((direct&(raw_age==ref)).sum()),
   "direct_age_within_1year_n":int((direct&((raw_age-ref).abs()<=1)).sum()),
   "birthyear_approx_reference_overlap_n":int(approx_overlap.sum()),
   "birthyear_approx_within_1year_n":int((approx_overlap&((approx-ref).abs()<=1)).sum()),
   "id_rule":"2011 baseline ID adjusted per official 2013 release note" if w==2011 else "normalized exact respondent ID",
   "interpretation":"Harmonized CHARLS D age is an external reference; use only after source/version and ID crosswalk QA."})
 QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 pd.DataFrame(result).to_csv(QA_OUTPUT_DIR/'harmonized_age_reference_qa_v1.csv',index=False,encoding='utf-8-sig')
 print(pd.DataFrame(result)[['wave','id_rows_with_reference_age','reference_age_valid_45plus','direct_age_reference_overlap_n','birthyear_approx_reference_overlap_n','birthyear_approx_within_1year_n']].to_string(index=False))

if __name__=='__main__':main()
