"""Apply 2018 household property-count and per-property rent-status metadata."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
FIELDS={("2018","ha000_w4_0"):"count"}|{("2018",f"ha005_w4_{i}_"):"rent_status" for i in range(1,8)}
Q="CHARLS_2018_Questionnaire_extracted.txt"; CB="CHARLS_2018_Codebook_extracted.txt"


def apply(row,code):
    kind=FIELDS[("2018",code.lower())]
    source=f"sources_official/{Q}; sources_official/{CB}"
    if kind=="count":
        labels=""; unit="properties"; status="official 2018 questionnaire identifies a numeric count of house properties titled to the main respondent and spouse; route-specific household property count"
        detail="Counts houses for which the main respondent or spouse is named on the property-rights certificate. Questionnaire specifies 0 if no property; new-household route only, while previously interviewed households follow the prior-property loop. Household asset/resource context, not a measure of the current residence. Verify release-specific route, zero semantics, property linkage and missingness."
    else:
        labels="1=Yes; 2=No; 999=Refuse to answer"; unit=""
        status="official 2018 questionnaire/Codebook categories reviewed for the slot-specific house-for-rent item"
        detail="Indicates whether the indexed house property is for rent; 999 is an explicit refusal category and No/Refusal skip the rent amount follow-up. Keep each property slot separate; slot number is roster/order metadata, not a stable property identity. Household asset/income context, not current-home rental status. Verify slot routing and authorized-release special values before analysis."
    row.update({"Value.Labels":labels,"Value.Label.Source":source,"Value.Label.Review":status,"Concept.Unit.Candidates":unit,"Unit":unit,"Harmonization.Status":detail,
                "value_labels":labels,"value_label_source":source,"value_label_review":status,"candidate_concept_units":unit,"harmonization_status":detail})


def update_csv(path):
    df=pd.read_csv(path,dtype=str,encoding="utf-8-sig").fillna("")
    sel=df.apply(lambda r:(str(r["Source.Wave"]),str(r["Variable.Name"]).lower()) in FIELDS,axis=1)
    seen=set(zip(df.loc[sel,"Source.Wave"],df.loc[sel,"Variable.Name"].str.lower()))
    if seen!=set(FIELDS):raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
    for i in df.index[sel]:
        code=str(df.at[i,"Variable.Name"]).lower();row={};apply(row,code)
        for k in ("Value.Labels","Value.Label.Source","Value.Label.Review","Concept.Unit.Candidates","Unit","Harmonization.Status"):df.at[i,k]=row[k]
    df.to_csv(path,index=False,encoding="utf-8-sig");return int(sel.sum())


def update_json(path):
    rows=json.loads(path.read_text(encoding="utf-8"));sel=[r for r in rows if (str(r.get("Source.Wave","")),str(r.get("Variable.Name","")).lower()) in FIELDS]
    seen={(str(r["Source.Wave"]),str(r["Variable.Name"]).lower()) for r in sel}
    if not sel:return 0
    if seen!=set(FIELDS):raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
    for r in sel:
        row={};apply(row,str(r["Variable.Name"]).lower());r.update({k:v for k,v in row.items() if k in ("Value.Labels","Value.Label.Source","Value.Label.Review","Concept.Unit.Candidates","Unit","Harmonization.Status","value_labels","value_label_source","value_label_review","candidate_concept_units","harmonization_status")})
    path.write_text(json.dumps(rows,ensure_ascii=False,separators=(",",":")),encoding="utf-8");return len(sel)


def main():
    q=(ROOT/"sources_official"/Q).read_text(encoding="utf-8",errors="ignore").casefold(); cb=(ROOT/"sources_official"/CB).read_text(encoding="utf-8",errors="ignore").casefold()
    if "ha000_w4_0" not in q or "property right certificate" not in q or "ha005_w4" not in q or "999." not in q or "refuse to answer" not in q:raise ValueError("2018 official questionnaire wording check failed")
    if any(code not in cb for _,code in FIELDS):raise ValueError("2018 official Codebook field check failed")
    n=update_csv(ROOT/"audit/charls_atlas_candidate_fields_v0.csv")
    for path in (ROOT/"audit/charls_atlas_candidate_fields_v0.json",ROOT/"site-prototype/dist/catalog.json",ROOT/"site-prototype/dist/catalog_e.json"):n+=update_json(path)
    print(f"Applied 2018 property-count/rent-status metadata to {n} rows; no participant values or frequencies included.")


if __name__=="__main__":main()
