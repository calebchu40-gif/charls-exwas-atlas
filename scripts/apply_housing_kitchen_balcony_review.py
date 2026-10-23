"""Apply numeric household kitchen/balcony count measurement notes."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {(wave, code): label for wave in ("2011", "2013", "2015", "2018") for code, label in (("i012_4", "kitchen count"), ("i012_5", "balcony count"))}
Q = {"2011":"CHARLS_2011_Baseline_Questionnaire_official_extracted.txt","2013":"CHARLS_2013_Questionnaire_extracted.txt","2015":"CHARLS_2015_Questionnaire_extracted.txt","2018":"CHARLS_2018_Questionnaire_extracted.txt"}


def apply(row: dict, wave: str, code: str) -> None:
    measure = FIELDS[(wave, code.lower())]
    source = f"sources_official/{Q[wave]}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    status = f"official {wave} questionnaire identifies a numeric household-residence {measure}; continuous count, no discrete category labels"
    caveat = f"Counts the number of {measure.replace(' count','')} in the household residence. The questionnaire soft check (>20) is an interviewer prompt, not a validated analytic cutoff; Codebook extrema do not establish valid ranges. Household-level built-environment context, not an individual exposure dose. Confirm release-specific special values, household linkage and missingness before analysis; cross-wave equivalence remains unapproved."
    row.update({"Concept.Unit.Candidates":"count","Unit":"count","Value.Labels":"","Value.Label.Source":source,"Value.Label.Review":status,"Harmonization.Status":caveat,
                "candidate_concept_units":"count","value_labels":"","value_label_source":source,"value_label_review":status,"harmonization_status":caveat})


def update_csv(path: Path) -> int:
    df=pd.read_csv(path,dtype=str,encoding="utf-8-sig").fillna("")
    selected=df.apply(lambda r:(str(r["Source.Wave"]),str(r["Variable.Name"]).lower()) in FIELDS,axis=1)
    seen=set(zip(df.loc[selected,"Source.Wave"],df.loc[selected,"Variable.Name"].str.lower()))
    if seen!=set(FIELDS): raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
    for i in df.index[selected]:
        row={}; apply(row,str(df.at[i,"Source.Wave"]),str(df.at[i,"Variable.Name"]).lower())
        for k in ("Concept.Unit.Candidates","Unit","Value.Labels","Value.Label.Source","Value.Label.Review","Harmonization.Status"): df.at[i,k]=row[k]
    df.to_csv(path,index=False,encoding="utf-8-sig"); return int(selected.sum())


def update_json(path: Path, wk: str, ck: str) -> int:
    rows=json.loads(path.read_text(encoding="utf-8"))
    if rows and "source_fields" in rows[0]: fields=[f for c in rows for f in c["source_fields"]]
    else: fields=rows
    selected=[f for f in fields if (str(f.get(wk,"")),str(f.get(ck,"")).lower()) in FIELDS]
    seen={(str(f[wk]),str(f[ck]).lower()) for f in selected}
    if not selected:return 0
    if seen!=set(FIELDS):raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
    for f in selected:
        row={}; apply(row,str(f[wk]),str(f[ck]).lower())
        if "source_fields" in rows[0]: f.update({"unit":"count","value_labels":"","value_label_status":row["Value.Label.Review"],"value_label_source":row["Value.Label.Source"],"note":row["Harmonization.Status"]})
        else:
            f.update({k:v for k,v in row.items() if k in ("Concept.Unit.Candidates","Unit","Value.Labels","Value.Label.Source","Value.Label.Review","Harmonization.Status","candidate_concept_units","value_labels","value_label_source","value_label_review","harmonization_status")})
            if wk=="wave":f.update({"unit":"count","value_labels":"","value_label_status":row["Value.Label.Review"],"value_label_source":row["Value.Label.Source"],"mapping_status":row["Value.Label.Review"],"caveat":row["Harmonization.Status"]})
    path.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n" if wk=="wave" else json.dumps(rows,ensure_ascii=False,separators=(",",":")),encoding="utf-8"); return len(selected)


def main():
    for wave,codes in {w:["i012_4","i012_5"] for w in Q}.items():
        text=(ROOT/"sources_official"/Q[wave]).read_text(encoding="utf-8",errors="ignore").casefold()
        for code in codes:
            if code not in text: raise ValueError(f"questionnaire missing {wave} {code}")
    n=update_csv(ROOT/"audit/charls_atlas_candidate_fields_v0.csv")
    n+=update_json(ROOT/"audit/charls_atlas_candidate_fields_v0.json","Source.Wave","Variable.Name")
    n+=update_json(ROOT/"site-prototype/dist/catalog.json","Source.Wave","Variable.Name")
    n+=update_json(ROOT/"site-prototype/dist/catalog_e.json","Source.Wave","Variable.Name")
    n+=update_json(ROOT/"site-prototype/dist/food_environment_v1.json","wave","code")
    print(f"Applied kitchen/balcony count notes to {n} metadata field rows; no participant values or frequencies included.")


if __name__=="__main__":main()
