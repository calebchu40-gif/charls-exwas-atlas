"""Derive provisional education and hukou states across CHARLS waves.

Person-level output is restricted to LOCALAPPDATA. The code preserves route
and conflict status instead of treating structural skips as ordinary missing.
These are research candidates, not CHARLS-endorsed harmonized variables.
"""
from pathlib import Path
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, WAVE_DATA_DIR
import pandas as pd
import pyreadstat

DATA = WAVE_DATA_DIR
OUT = PRIVATE_ROOT / "derived_covariates"
WAVES = [2011, 2013, 2015, 2018, 2020]

FIELDS = {
 2011: ["ID", "bd001", "bc001"],
 2013: ["ID", "xrtype", "bd001", "zbd001", "bd001_w2_1", "bd001_w2_3", "bd001_w2_4", "bc001", "zbc001", "bc001_w2_1"],
 2015: ["ID", "xrtype", "bd001_w2_4", "bc001_w3_1", "bc001_w3_2", "bc002_w3", "bc002_w3_1"],
 2018: ["ID", "xrtype", "bd001_w2_4", "bc001_w3_1", "bc001_w3_2", "bc002_w3", "bc002_w3_1"],
 2020: ["ID", "xrtype", "ba010", "zredu", "ba009"],
}

def num(x):
    try:
        v = float(x)
        return int(v) if v.is_integer() else None
    except (TypeError, ValueError):
        return None

def key(x, wave):
    if pd.isna(x): return None
    s = str(x).strip()
    if s.endswith(".0") and s[:-2].isdigit(): s = s[:-2]
    if not s: return None
    # Official CHARLS Wave 2 release note: adjust the 11-digit baseline ID.
    if wave == 2011 and len(s) == 11 and s.isdigit(): return s[:9] + "0" + s[9:]
    return s

def in_codes(x, allowed):
    v = num(x)
    return v if v in allowed else None

def get(row, name):
    return row.get(name, None)

def education_state(wave, row, previous):
    rt = num(get(row, "xrtype"))
    prior = previous.get("education") if previous else None
    if wave == 2011:
        v = in_codes(get(row,"bd001"), range(1,12))
        return v, "baseline_direct" if v is not None else "baseline_missing", 0
    if wave == 2013:
        # In W2: XRType 1=NEWIW, 2=REIW. Returning interviews have a
        # correction check and a changed/no-change item.
        if rt == 1:
            v = in_codes(get(row,"bd001"), range(1,12))
            return v, "new_interview_direct" if v is not None else "new_interview_missing", 0
        if rt == 2:
            z = in_codes(get(row,"zbd001"), range(1,12))
            if z is None: z = prior
            corrected = in_codes(get(row,"bd001_w2_3"), range(1,12)) if num(get(row,"bd001_w2_1")) == 2 else None
            if corrected is not None: z = corrected
            upd = num(get(row,"bd001_w2_4"))
            if upd in range(1,12): return upd, "returner_current_update", int(corrected is not None)
            if upd == 12 and z is not None: return z, "returner_no_change_carry", int(corrected is not None)
            return None, "returner_route_or_prior_unresolved", int(corrected is not None)
        return None, "interview_type_unresolved", 0
    if wave in (2015,2018):
        upd = num(get(row,"bd001_w2_4"))
        if upd in range(1,12): return upd, "current_update", 0
        if upd == 12 and prior is not None: return prior, "explicit_no_change_carry", 0
        if upd == 12: return None, "no_change_without_prior", 0
        return None, "route_or_value_unresolved", 0
    # W5 education is sparse and there is no validated questionnaire route
    # marker for non-response versus structural skip in the prepared source.
    upd = in_codes(get(row,"ba010"), range(1,12))
    if upd is not None: return upd, "current_direct_response", 0
    preload = in_codes(get(row,"zredu"), range(1,12))
    if preload is not None: return preload, "official_education_preload", 0
    if prior is not None:
        return prior, "last_observed_carry_unverified", 0
    return None, "no_current_response_unresolved", 0

def hukou_state(wave, row, previous):
    rt = num(get(row,"xrtype"))
    prior = previous.get("hukou") if previous else None
    if wave == 2011:
        v = in_codes(get(row,"bc001"), range(1,5))
        return v, "baseline_direct" if v is not None else "baseline_missing", 0
    if wave == 2013:
        # W2 direct current status is present for most rows. The change check
        # validates whether it differs from the prior preload.
        upd = in_codes(get(row,"bc001"), range(1,5))
        old = in_codes(get(row,"zbc001"), range(1,5)) or prior
        changed = num(get(row,"bc001_w2_1"))
        if rt == 1:
            return upd, "new_interview_direct" if upd is not None else "new_interview_missing", 0
        if rt == 2:
            if changed == 1 and upd is not None: return upd, "returner_changed_direct", 0
            if changed == 2 and old is not None:
                return old, "returner_no_change_carry_conflict" if upd is not None and upd != old else "returner_no_change_carry", 0
            if upd is not None and old is not None:
                if upd == old: return old, "returner_preload_matches_prior", 0
                return old, "returner_route_missing_conflict_carry_prior", 0
            if upd is not None: return upd, "returner_direct_without_prior", 0
            return None, "returner_route_or_prior_unresolved", 0
        return upd, "direct_interview_type_unresolved" if upd is not None else "interview_type_unresolved", 0
    if wave in (2015,2018):
        change = num(get(row,"bc002_w3"))
        current = in_codes(get(row,"bc002_w3_1"), range(1,5))
        # W3 encodes NEWIW=1/REIW=2; W4 encodes REIW=1/NEWIW=2.
        is_new = (wave == 2015 and rt == 1) or (wave == 2018 and rt == 2)
        is_returner = (wave == 2015 and rt == 2) or (wave == 2018 and rt == 1)
        if is_new:
            return current, "new_interview_direct" if current is not None else "new_interview_missing", 0
        if is_returner:
            old = prior
            corrected = in_codes(get(row,"bc001_w3_2"), range(1,5)) if num(get(row,"bc001_w3_1")) == 2 else None
            if corrected is not None: old = corrected
            if change in (1,3):
                return current, "returner_type_changed" if current is not None else "changed_type_missing", int(corrected is not None)
            if change in (2,4) and old is not None:
                return old, "returner_type_unchanged_carry", int(corrected is not None)
            return None, "returner_change_or_prior_unresolved", int(corrected is not None)
        return None, "interview_type_unresolved", 0
    current = in_codes(get(row,"ba009"), range(1,5))
    return current, "current_direct" if current is not None else "current_missing", 0

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Keep the latest valid state for each person across all earlier waves.
    # A respondent may miss an interview and return later; replacing this map
    # with only the immediately previous wave would lose their last known state.
    prior_by_key = {}
    agg=[]; values=[]
    for wave in WAVES:
        p = DATA / f"CHARLS_wave{wave}_person_analytic.dta"
        _, meta = pyreadstat.read_dta(str(p), metadataonly=True)
        use = [v for v in FIELDS[wave] if v in meta.column_names]
        d, _ = pyreadstat.read_dta(str(p), usecols=use)
        rows=[]
        for _, rr in d.iterrows():
            r=rr.to_dict(); k=key(r["ID"],wave); prev=prior_by_key.get(k)
            edu, es, ec = education_state(wave,r,prev)
            huk, hs, hc = hukou_state(wave,r,prev)
            rows.append({"ID":r["ID"],"education_level_candidate":edu,"education_status":es,"education_prior_corrected":ec,
                         "hukou_type_candidate":huk,"hukou_status":hs,"hukou_prior_corrected":hc,
                         "hukou_conflict_flag":int("conflict" in hs),"candidate_provisional":1})
        out=pd.DataFrame(rows)
        if out.ID.isna().any() or out.ID.duplicated().any() or len(out) != len(d) or not out.ID.equals(d.ID):
            raise ValueError(f"{wave}: candidate output does not preserve unique respondent IDs/row count")
        if not set(pd.to_numeric(out.education_level_candidate, errors="coerce").dropna().astype(int)).issubset(set(range(1,12))):
            raise ValueError(f"{wave}: education code outside documented category domain")
        if not set(pd.to_numeric(out.hukou_type_candidate, errors="coerce").dropna().astype(int)).issubset(set(range(1,5))):
            raise ValueError(f"{wave}: hukou code outside documented category domain")
        pyreadstat.write_dta(out,str(OUT/f"education_hukou_candidate_{wave}.dta"),version=14)
        # Retain only harmonized state values in memory for next-wave carry.
        for r in rows:
            k = key(r["ID"],wave)
            if not k: continue
            old = prior_by_key.get(k, {})
            if r["education_level_candidate"] is not None: old["education"] = r["education_level_candidate"]
            if r["hukou_type_candidate"] is not None: old["hukou"] = r["hukou_type_candidate"]
            prior_by_key[k] = old
        for concept, field, statusfield in [("education","education_level_candidate","education_status"),("hukou","hukou_type_candidate","hukou_status")]:
            x=pd.to_numeric(out[field],errors="coerce"); st=out[statusfield].fillna("unknown")
            for status,n in st.value_counts().items():
                if int(n) >= 5: agg.append({"wave":wave,"concept":concept,"status":status,"n":int(n)})
            for value,n in x.value_counts().sort_index().items():
                if int(n) >= 5: values.append({"wave":wave,"concept":concept,"candidate_code":int(value),"n":int(n)})
        print(wave, "rows",len(out),"education nonmissing",out.education_level_candidate.notna().sum(),"hukou nonmissing",out.hukou_type_candidate.notna().sum())
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(agg).to_csv(QA_OUTPUT_DIR/"education_hukou_candidate_status_aggregate_v1.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(values).to_csv(QA_OUTPUT_DIR/"education_hukou_candidate_value_aggregate_v1.csv",index=False,encoding="utf-8-sig")
    print("Private outputs:",OUT)

def _self_test():
    assert education_state(2015,{"bd001_w2_4":12},{"education":5})[0] == 5
    assert education_state(2015,{"bd001_w2_4":6},{"education":5})[0] == 6
    assert education_state(2015,{"bd001_w2_4":12},None)[0] is None
    assert education_state(2020,{"ba010":None},{"education":7}) == (7,"last_observed_carry_unverified",0)
    assert education_state(2020,{"ba010":None,"zredu":5},{"education":7}) == (5,"official_education_preload",0)
    assert hukou_state(2015,{"xrtype":2,"bc002_w3":4},{"hukou":1})[0] == 1
    assert hukou_state(2015,{"xrtype":2,"bc002_w3":2},{"hukou":2})[0] == 2
    assert hukou_state(2015,{"xrtype":2,"bc002_w3":1,"bc002_w3_1":3},{"hukou":1})[0] == 3
    assert hukou_state(2020,{"ba009":4},None)[0] == 4
    # Historical valid information remains available after a missed wave.
    assert education_state(2015,{"bd001_w2_4":12},{"education":8})[0] == 8

if __name__ == "__main__":
    _self_test(); main()
