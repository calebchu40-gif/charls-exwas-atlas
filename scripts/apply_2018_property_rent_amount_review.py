"""Apply 2018 actual and market monthly-rent measurement metadata by property slot."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
FIELDS={("2018",f"ha006_w4_{i}_"):"actual" for i in (1,2,3,4,5,7)}|{("2018",f"ha007_w4_{i}_"):"market" for i in range(1,8)}
Q="CHARLS_2018_Questionnaire_extracted.txt";CB="CHARLS_2018_Codebook_extracted.txt"


def apply(row,code):
    kind=FIELDS[("2018",code.lower())]; actual=kind=="actual"
    measure="actual monthly rent" if actual else "estimated market rent per month"
    status=f"official 2018 questionnaire identifies {measure} for an indexed house property; continuous Yuan/month amount, no discrete labels"
    detail=("Actual rent is routed after HA005=Yes; No/refusal skips the amount, so an absent amount must not automatically be recoded as zero. Zero triggers bracket follow-up per questionnaire. " if actual else "Market rent is a separate estimated amount for the indexed property and must not be substituted for actual rent. Zero triggers bracket follow-up per questionnaire. ")
    caveat=detail+"Amounts are per property slot, not summed household rent or property value. Keep the seven slot identities separate and retain current-ownership route; slots are not stable cross-person property IDs. Confirm special values, brackets, eligible denominator and linkage in authorized-release QA before modeling."
    source=f"sources_official/{Q}; sources_official/{CB}"
    row.update({"Concept.Unit.Candidates":"Yuan/month","Unit":"Yuan/month","Value.Labels":"","Value.Label.Source":source,"Value.Label.Review":status,"Harmonization.Status":caveat,
                "candidate_concept_units":"Yuan/month","value_labels":"","value_label_source":source,"value_label_review":status,"harmonization_status":caveat})


def update_csv(path):
    df=pd.read_csv(path,dtype=str,encoding="utf-8-sig").fillna("");sel=df.apply(lambda r:(str(r["Source.Wave"]),str(r["Variable.Name"]).lower()) in FIELDS,axis=1)
    seen=set(zip(df.loc[sel,"Source.Wave"],df.loc[sel,"Variable.Name"].str.lower()))
    if seen!=set(FIELDS):raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
    for i in df.index[sel]:
        row={};apply(row,str(df.at[i,"Variable.Name"]).lower())
        for k in ("Concept.Unit.Candidates","Unit","Value.Labels","Value.Label.Source","Value.Label.Review","Harmonization.Status"):df.at[i,k]=row[k]
    df.to_csv(path,index=False,encoding="utf-8-sig");return int(sel.sum())


def update_json(path):
    rows=json.loads(path.read_text(encoding="utf-8"));sel=[r for r in rows if (str(r.get("Source.Wave","")),str(r.get("Variable.Name","")).lower()) in FIELDS]
    seen={(str(r["Source.Wave"]),str(r["Variable.Name"]).lower()) for r in sel}
    if not sel:return 0
    if seen!=set(FIELDS):raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
    for r in sel:
        row={};apply(row,str(r["Variable.Name"]).lower());r.update({k:v for k,v in row.items() if k in ("Concept.Unit.Candidates","Unit","Value.Labels","Value.Label.Source","Value.Label.Review","Harmonization.Status","candidate_concept_units","value_labels","value_label_source","value_label_review","harmonization_status")})
    path.write_text(json.dumps(rows,ensure_ascii=False,separators=(",",":")),encoding="utf-8");return len(sel)


def main():
    q=(ROOT/"sources_official"/Q).read_text(encoding="utf-8",errors="ignore").casefold();cb=(ROOT/"sources_official"/CB).read_text(encoding="utf-8",errors="ignore").casefold()
    for code,phrase in (("ha006_w4","yuan/month"),("ha007_w4","yuan/month")):
        if code not in q or phrase not in q or code not in cb:raise ValueError(f"official source verification failed for {code}")
    n=update_csv(ROOT/"audit/charls_atlas_candidate_fields_v0.csv")
    for p in (ROOT/"audit/charls_atlas_candidate_fields_v0.json",ROOT/"site-prototype/dist/catalog.json",ROOT/"site-prototype/dist/catalog_e.json"):n+=update_json(p)
    print(f"Applied 2018 per-property rent amount metadata to {n} rows; no participant values or frequencies included.")


if __name__=="__main__":main()
