#!/usr/bin/env python3
"""Aggregate-only pairwise availability for candidate exposures x derived diseases."""
from __future__ import annotations
import argparse, os, runpy
from pathlib import Path
import pandas as pd
import pyreadstat

DISEASES = ["hypertension", "dyslipidemia", "diabetes", "chronic_lung_disease",
            "heart_disease", "stroke", "kidney_disease", "arthritis"]
WAVES = (2011, 2013, 2015, 2018, 2020)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, required=True)
    ap.add_argument("--status-dir", type=Path, required=True)
    ap.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    a=ap.parse_args()
    if "OneDrive" in str(a.status_dir.resolve()) or "Desktop" in str(a.status_dir.resolve()):
        raise ValueError("Personal-level status tables must remain outside synchronized paths")
    core=runpy.run_path(str(Path(__file__).with_name("build_core_concept_coverage.py")))
    exposure_rules=runpy.run_path(str(Path(__file__).with_name("summarize_core_exposure_validity.py")))
    mapping, roles, observed = core["MAP"], core["ROLE"], core["observed_mask"]
    exposures=[k for k,v in roles.items() if v=="exposure_proxy"]
    rows=[]
    for wave in WAVES:
        w=str(wave)
        source=a.data_dir/f"CHARLS_wave{wave}_person_analytic.dta"
        _,meta=pyreadstat.read_dta(str(source),metadataonly=True)
        cols=set(meta.column_names)
        expvars={e:mapping[e].get(w) for e in exposures}
        use=[v for v in expvars.values() if v and v in cols]
        expdata,_=pyreadstat.read_dta(str(source),usecols=["ID"]+use)
        status,_=pyreadstat.read_dta(str(a.status_dir/f"chronic_disease_status_{wave}.dta"))
        if len(expdata)!=len(status) or not expdata.ID.astype(str).equals(status.ID.astype(str)):
            raise ValueError(f"Respondent key/order mismatch in {wave}")
        for exp in exposures:
            ev=expvars[exp]
            for disease in DISEASES:
                outcome=status[f"{disease}_status"]
                if ev and ev in expdata:
                    valid=exposure_rules["valid_mask"](exp,w,expdata[ev]) & outcome.notna()
                    n=int(valid.sum())
                    n_conflict=int((valid & status[f"{disease}_conflict"].eq(1)).sum())
                    n_conflict_free=n-n_conflict
                    state="provisional_pair_complete_raw_exposure"
                else:
                    n=None; n_conflict=None; n_conflict_free=None; state="exposure_not_measured_or_field_missing"
                rows.append({"wave":wave,"exposure_concept":exp,"exposure_variable":ev or "",
                    "outcome_concept":disease+"_diagnosis","outcome_status_variable":disease+"_status",
                    "n_pair_complete_including_flagged":n,"n_pairs_with_outcome_conflict_flag":n_conflict,
                    "n_pair_complete_conflict_free":n_conflict_free,"status":state,
                    "sample_count_note":"codebook-valid exposure response × nonmissing provisional disease status; still excludes no design/weight/covariate/model restrictions"})
    out=a.project_dir/"audit"/"chronic_disease_pairwise_availability_v1.csv"
    out.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out,index=False,encoding="utf-8-sig")
    print(f"rows={len(rows)} exposures={len(exposures)} outcomes={len(DISEASES)} waves={len(WAVES)}")

if __name__=="__main__": main()
