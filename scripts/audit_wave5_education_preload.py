"""Aggregate-only check of CHARLS 2020 education preload against Wave 4."""
from pathlib import Path
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR
import pandas as pd
import pyreadstat

ROOT=PRIVATE_ROOT

def main():
    prev,_=pyreadstat.read_dta(str(ROOT/"derived_covariates"/"education_hukou_candidate_2018.dta"),usecols=["ID","education_level_candidate"])
    cur,_=pyreadstat.read_dta(str(ROOT/"derived_wave_tables"/"CHARLS_wave2020_person_analytic.dta"),usecols=["ID","ba010","zredu"])
    j=cur.merge(prev,on="ID",how="left",validate="one_to_one")
    ba=pd.to_numeric(j.ba010,errors="coerce"); z=pd.to_numeric(j.zredu,errors="coerce"); old=pd.to_numeric(j.education_level_candidate,errors="coerce")
    both=ba.notna()&z.notna(); zold=z.notna()&old.notna(); baold=ba.notna()&old.notna()
    out=pd.DataFrame([{
      "wave":2020,"respondent_rows":len(j),"ba010_direct_n":int(ba.notna().sum()),"zredu_preload_n":int(z.notna().sum()),
      "ba010_zredu_overlap_n":int(both.sum()),"neither_n":int((ba.isna()&z.isna()).sum()),
      "zredu_linked_to_2018_education_n":int(zold.sum()),"zredu_equal_to_2018_n":int((zold&(z==old)).sum()),
      "zredu_different_from_2018_n":int((zold&(z!=old)).sum()),"zredu_without_2018_candidate_n":int((z.notna()&old.isna()).sum()),
      "ba010_linked_to_2018_candidate_n":int(baold.sum()),"ba010_without_2018_candidate_n":int((ba.notna()&old.isna()).sum()),
      "interpretation":"zredu and ba010 are disjoint; zredu exactly equals linked 2018 candidate. Aggregate QA only; no IDs or person records emitted."
    }])
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(QA_OUTPUT_DIR/"wave5_education_preload_qa_v1.csv",index=False,encoding="utf-8-sig")
    print(out.to_string(index=False))

if __name__=="__main__": main()
