"""Build private age candidate files and aggregate QA.

For 2011-2018, the candidate uses Harmonized CHARLS D respondent age as a
third-party derived reference. It is NOT labeled as a CHARLS official variable
or accepted as the final harmonized age until its source algorithm is audited.
For 2020, it uses the CHARLS-released xrage field, pending official definition
verification. Individual-level outputs stay in LOCALAPPDATA.
"""
from pathlib import Path
import os
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path
import pandas as pd
import pyreadstat

DATA = WAVE_DATA_DIR
PRIVATE = PRIVATE_ROOT / "age_candidates"
HARM = require_private_path(Path(os.environ.get("CHARLS_HARMONIZED_D_PATH", str(PRIVATE_ROOT / "references" / "H_CHARLS_D_Data.dta"))))

def norm(x):
    if pd.isna(x): return None
    s = str(x).strip()
    if s.endswith(".0") and s[:-2].isdigit(): s = s[:-2]
    return s or None

def harmonized_key(x, wave):
    s = norm(x)
    if s and wave == 2011 and len(s) == 11 and s.isdigit():
        return s[:9] + "0" + s[9:]
    return s

def main():
    PRIVATE.mkdir(parents=True, exist_ok=True)
    _, hm = pyreadstat.read_dta(str(HARM), metadataonly=True)
    hcols = ["ID"] + [f"r{i}agey" for i in range(1, 5) if f"r{i}agey" in hm.column_names]
    h, _ = pyreadstat.read_dta(str(HARM), usecols=hcols)
    h["_key"] = h.ID.map(norm)
    h = h.dropna(subset=["_key"]).drop_duplicates("_key")
    summary = []
    for i, wave in enumerate([2011, 2013, 2015, 2018], 1):
        p = DATA / f"CHARLS_wave{wave}_person_analytic.dta"
        d, _ = pyreadstat.read_dta(str(p), usecols=["ID"])
        d["_key"] = d.ID.map(lambda x: harmonized_key(x, wave))
        j = d.merge(h[["_key", f"r{i}agey"]], on="_key", how="left", validate="one_to_one")
        age = pd.to_numeric(j[f"r{i}agey"], errors="coerce")
        out = pd.DataFrame({"ID": j.ID, "age_years_candidate": age, "age_source": "Harmonized CHARLS D respondent age (third-party derived reference)", "age_provisional": 1})
        out_path = PRIVATE / f"age_candidate_{wave}.dta"
        pyreadstat.write_dta(out, str(out_path), version=14)
        summary.append({"wave": wave, "rows": len(out), "age_nonmissing": int(age.notna().sum()), "age_45plus": int((age >= 45).sum()), "age_under45": int((age < 45).sum()), "age_invalid_outside_18_120": int((age.notna() & ~age.between(18,120)).sum()), "source": "third-party Harmonized CHARLS D; provisional only"})
    p = DATA / "CHARLS_wave2020_person_analytic.dta"
    d, _ = pyreadstat.read_dta(str(p), usecols=["ID", "xrage"])
    age = pd.to_numeric(d.xrage, errors="coerce")
    out = pd.DataFrame({"ID": d.ID, "age_years_candidate": age, "age_source": "CHARLS 2020 released xrage; definition verification pending", "age_provisional": 1})
    pyreadstat.write_dta(out, str(PRIVATE / "age_candidate_2020.dta"), version=14)
    summary.append({"wave": 2020, "rows": len(out), "age_nonmissing": int(age.notna().sum()), "age_45plus": int((age >= 45).sum()), "age_under45": int((age < 45).sum()), "age_invalid_outside_18_120": int((age.notna() & ~age.between(18,120)).sum()), "source": "CHARLS released xrage; provisional only"})
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summary).to_csv(QA_OUTPUT_DIR / "age_candidate_aggregate_qa_v1.csv", index=False, encoding="utf-8-sig")
    print(pd.DataFrame(summary).to_string(index=False))
    print(f"Private individual-level candidates: {PRIVATE}")

if __name__ == "__main__": main()
