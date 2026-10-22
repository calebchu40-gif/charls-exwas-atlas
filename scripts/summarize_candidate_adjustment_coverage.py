"""Aggregate complete-case coverage for provisional demographic adjustment sets."""
from pathlib import Path
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR
import pandas as pd
import pyreadstat

ROOT=PRIVATE_ROOT
WAVES=[2011,2013,2015,2018,2020]

def read(path,cols): return pyreadstat.read_dta(str(path),usecols=cols)[0]

def main():
    rows=[]
    for w in WAVES:
        base=read(ROOT/"derived_wave_tables"/f"CHARLS_wave{w}_person_analytic.dta",["ID"]+(["ind_weight_ad2"] if w==2011 else ["INDV_weight_ad2"]))
        age=read(ROOT/"age_candidates"/f"age_candidate_{w}.dta",["ID","age_years_candidate"])
        gm=read(ROOT/"derived_covariates"/f"gender_marital_candidate_{w}.dta",["ID","gender_candidate","marital_status_candidate"])
        eh=read(ROOT/"derived_covariates"/f"education_hukou_candidate_{w}.dta",["ID","education_level_candidate","education_status","hukou_type_candidate"])
        d=base.merge(age,on="ID",validate="one_to_one").merge(gm,on="ID",validate="one_to_one").merge(eh,on="ID",validate="one_to_one")
        wcol="ind_weight_ad2" if w==2011 else "INDV_weight_ad2"
        positive_weight=pd.to_numeric(d[wcol],errors="coerce").gt(0)
        m1=d[["age_years_candidate","gender_candidate"]].notna().all(axis=1)
        m2=d[["age_years_candidate","gender_candidate","education_level_candidate","marital_status_candidate","hukou_type_candidate"]].notna().all(axis=1)
        strict_edu=~d.education_status.eq("last_observed_carry_unverified")
        m2_strict=m2&strict_edu
        rows.append({"wave":w,"respondent_rows":len(d),"age_available_n":int(d.age_years_candidate.notna().sum()),
                     "gender_available_n":int(d.gender_candidate.notna().sum()),"education_candidate_n":int(d.education_level_candidate.notna().sum()),
                     "education_direct_or_route_verified_n":int((d.education_level_candidate.notna()&strict_edu).sum()),
                     "marital_available_n":int(d.marital_status_candidate.notna().sum()),"hukou_available_n":int(d.hukou_type_candidate.notna().sum()),
                     "M1_age_sex_complete_n":int(m1.sum()),"M1_with_positive_person_weight_n":int((m1&positive_weight).sum()),
                     "M2_complete_candidate_n":int(m2.sum()),"M2_with_positive_person_weight_n":int((m2&positive_weight).sum()),
                     "M2_strict_education_n":int(m2_strict.sum()),"M2_strict_with_positive_person_weight_n":int((m2_strict&positive_weight).sum()),
                     "weight_field":wcol,"weight_scope_note":"positive individual weight intersection only; does not establish correct target-population weight or full design variance."})
        if len(d)!=len(base) or d.ID.isna().any() or d.ID.duplicated().any(): raise ValueError(f"{w}: join QA failed")
    out=pd.DataFrame(rows)
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(QA_OUTPUT_DIR/"candidate_adjustment_coverage_v1.csv",index=False,encoding="utf-8-sig")
    print(out[["wave","respondent_rows","M1_age_sex_complete_n","M1_with_positive_person_weight_n","M2_complete_candidate_n","M2_with_positive_person_weight_n","M2_strict_education_n","M2_strict_with_positive_person_weight_n"]].to_string(index=False))

if __name__=="__main__": main()
