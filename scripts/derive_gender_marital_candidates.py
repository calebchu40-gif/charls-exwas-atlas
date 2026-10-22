"""Create provisional gender/marital candidates and aggregate route QA."""
from pathlib import Path
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, WAVE_DATA_DIR
import pandas as pd
import pyreadstat

DATA=WAVE_DATA_DIR
OUT=PRIVATE_ROOT / "derived_covariates"
MAP={
 2011:{"gender":"rgender","marital":"be001"},
 2013:{"gender":"xrgender","marital":"be001"},
 2015:{"gender":"xrgender","marital":"be001"},
 2018:{"gender":"xrgender","marital":"be001"},
 2020:{"gender":"xrgender","marital":"ba011","current_gender_record":"ba001","gender_confirmation":"ba002","partner_cohabiting":"ba012"},
}

def valid(x, allowed):
    n=pd.to_numeric(x,errors="coerce")
    return n.where(n.isin(allowed))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    qa=[]; dist=[]
    for wave,mapping in MAP.items():
        p=DATA/f"CHARLS_wave{wave}_person_analytic.dta"
        _,meta=pyreadstat.read_dta(str(p),metadataonly=True)
        fields=["ID"]+[v for v in mapping.values() if v in meta.column_names]
        d,_=pyreadstat.read_dta(str(p),usecols=fields)
        gender=valid(d[mapping["gender"]],{1,2})
        marital=valid(d[mapping["marital"]],set(range(1,8)))
        out=pd.DataFrame({"ID":d.ID,"gender_candidate":gender,"marital_status_candidate":marital,"candidate_provisional":1})
        if wave==2020:
            out["current_gender_record"]=valid(d[mapping["current_gender_record"]],{1,2})
            out["gender_confirmation"]=valid(d[mapping["gender_confirmation"]],{1,2})
            out["gender_conflict_flag"]=((out.current_gender_record.notna())&(out.gender_candidate.notna())&(out.current_gender_record!=out.gender_candidate)).astype(int)
            out["partner_cohabiting_candidate"]=valid(d[mapping["partner_cohabiting"]],{1,2})
        else:
            out["gender_conflict_flag"]=0
        if out.ID.isna().any() or out.ID.duplicated().any() or not out.ID.equals(d.ID):
            raise ValueError(f"{wave}: candidate IDs or row count differ from respondent base")
        pyreadstat.write_dta(out,str(OUT/f"gender_marital_candidate_{wave}.dta"),version=14)
        # Readback checks ensure the private Stata artifact can be consumed.
        check,_=pyreadstat.read_dta(str(OUT/f"gender_marital_candidate_{wave}.dta"),usecols=["ID","gender_candidate","marital_status_candidate"])
        if len(check)!=len(d) or check.ID.isna().any() or check.ID.duplicated().any():
            raise ValueError(f"{wave}: private candidate readback validation failed")
        for concept,series in [("gender",gender),("marital_status",marital)]:
            qa.append({"wave":wave,"concept":concept,"rows":len(d),"valid_n":int(series.notna().sum()),"invalid_or_missing_n":int(series.isna().sum())})
            for code,n in series.value_counts().sort_index().items():
                if int(n)>=5: dist.append({"wave":wave,"concept":concept,"code":int(code),"n":int(n)})
        if wave==2020:
            qa.append({"wave":wave,"concept":"gender_conflict_vs_interviewer_record","rows":len(d),"valid_n":int(out.gender_conflict_flag.sum()),"invalid_or_missing_n":int(out.gender_candidate.isna().sum())})
            qa.append({"wave":wave,"concept":"partner_cohabiting","rows":len(d),"valid_n":int(out.partner_cohabiting_candidate.notna().sum()),"invalid_or_missing_n":int(out.partner_cohabiting_candidate.isna().sum())})
        print(wave,"gender",int(gender.notna().sum()),"marital",int(marital.notna().sum()),"gender conflict",int(out.gender_conflict_flag.sum()))
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(qa).to_csv(QA_OUTPUT_DIR/"gender_marital_candidate_aggregate_v1.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(dist).to_csv(QA_OUTPUT_DIR/"gender_marital_value_aggregate_v1.csv",index=False,encoding="utf-8-sig")

def _test():
    s=pd.Series([1,2,3,None])
    assert valid(s,{1,2}).notna().sum()==2

if __name__=="__main__":
    _test(); main()
