"""Aggregate-only audit of CHARLS weight, sample, and cluster fields.

Reads only design-related columns from the private wave tables; never reads or
exports respondent IDs/rows. Small categorical cells are suppressed.
"""
from pathlib import Path
from project_paths import QA_OUTPUT_DIR, WAVE_DATA_DIR
import pandas as pd
import pyreadstat

DATA=WAVE_DATA_DIR
WAVES=["2011","2013","2015","2018","2020"]

def main():
    rows=[]
    for wave in WAVES:
        p=DATA/f"CHARLS_wave{wave}_person_analytic.dta"
        _,meta=pyreadstat.read_dta(str(p),metadataonly=True)
        names=meta.column_names
        design_ids={"crosssection","longitudinal","died","communityid","province","city","urban_nbs","areatype"}
        selected=[c for c in names if "weight" in c.lower() or c.lower() in design_ids or "psu" in c.lower() or "strat" in c.lower()]
        d,_=pyreadstat.read_dta(str(p),usecols=selected)
        for var in selected:
            x=d[var]
            label=meta.column_labels[names.index(var)] if var in names and meta.column_labels else ""
            if "weight" in var.lower():
                num=pd.to_numeric(x,errors="coerce")
                rows.append({"wave":wave,"variable":var,"variable_label":label,"field_type":"weight",
                    "n_nonmissing":int(num.notna().sum()),"n_positive":int(num.gt(0).sum()),
                    "n_zero_or_negative":int((num.notna()&num.le(0)).sum()),"n_unique_nonmissing":int(num.nunique()),
                    "n_community_clusters":None,"scope_note":"Weight availability only; choose by target population and module/response sample."})
            elif var.lower()=="communityid":
                rows.append({"wave":wave,"variable":var,"variable_label":label,"field_type":"psu_identifier",
                    "n_nonmissing":int(x.notna().sum()),"n_positive":None,"n_zero_or_negative":None,"n_unique_nonmissing":int(x.nunique(dropna=True)),
                    "n_community_clusters":int(x.nunique(dropna=True)) if var.lower()=="communityid" else None,
                    "scope_note":"Village/urban community is the CHARLS PSU in the official sample design; the 2013 PSU map contains 450 community IDs, and 2018/2020 guides state PSU information is unchanged. This confirms the cluster ID, not the released variance-stratum specification."})
            elif var.lower() in {"province","city","urban_nbs","areatype"}:
                rows.append({"wave":wave,"variable":var,"variable_label":label,"field_type":"geography_or_stratification_context",
                    "n_nonmissing":int(x.notna().sum()),"n_positive":None,"n_zero_or_negative":None,"n_unique_nonmissing":int(x.nunique(dropna=True)),
                    "n_community_clusters":None,
                    "scope_note":"Geographic/sampling context only. The released fields are not an explicit variance-stratum ID; do not synthesize strata from them."})
            else:
                vals=pd.to_numeric(x,errors="coerce")
                vc=vals.value_counts(dropna=True).to_dict()
                visible={str(k):int(v) for k,v in vc.items() if pd.notna(k) and int(v)>=10}
                rows.append({"wave":wave,"variable":var,"variable_label":label,"field_type":"sample_flag",
                    "n_nonmissing":int(vals.notna().sum()),"n_positive":None,"n_zero_or_negative":None,"n_unique_nonmissing":int(vals.nunique()),
                    "n_community_clusters":None,"scope_note":"Aggregate code counts with cells <10 suppressed: "+str(visible or "all suppressed/no observed category")})
        rows.append({"wave":wave,"variable":"explicit_variance_stratum_id","variable_label":"Not located in released analytic/PSU files",
            "field_type":"design_component_gap","n_nonmissing":None,"n_positive":None,"n_zero_or_negative":None,
            "n_unique_nonmissing":None,"n_community_clusters":None,
            "scope_note":"Sampling was implicitly stratified, but no explicit variance-stratum variable was found in available public files. Do not substitute province, city, urban_nbs or area type without official analytic guidance."})
    out=pd.DataFrame(rows)
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(QA_OUTPUT_DIR/"survey_design_field_coverage_v1.csv",index=False,encoding="utf-8-sig")
    print(out.groupby(["wave","field_type"]).size().to_string())
    print("rows",len(out))

if __name__=="__main__":main()
