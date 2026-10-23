"""Apply questionnaire-backed homestead area units and applicability notes."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
WAVES={"2011":"CHARLS_2011_Baseline_Questionnaire_official_extracted.txt","2013":"CHARLS_2013_Questionnaire_extracted.txt","2015":"CHARLS_2015_Questionnaire_extracted.txt","2018":"CHARLS_2018_Questionnaire_extracted.txt"}
FIELDS={(wave,"i002") for wave in WAVES}


def apply(row,wave):
    source=f"sources_official/{WAVES[wave]}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    status=f"official {wave} questionnaire identifies current-residence homestead land area in square meters; numeric continuous measure with no discrete value labels"
    caveat="Homestead land area associated with the current residence; the questionnaire defines homestead as land allocated by rural collective organizations for housing/small garden. Not a universal residential lot-area measure. Questionnaire directs no-entry/not-applicable cases to 0 in relevant waves; treat zero as potentially structural/nonapplicable until authorized-release coding and eligibility are verified. Soft checks (<10 or >1000 m²) are interviewer prompts, not validated analytic bounds; Codebook extrema are not cutoffs. Verify route, special values, residence linkage and missingness before modeling; cross-wave equivalence is not established."
    row.update({"Concept.Unit.Candidates":"m²","Unit":"m²","Value.Labels":"","Value.Label.Source":source,"Value.Label.Review":status,"Harmonization.Status":caveat,
                "candidate_concept_units":"m²","value_labels":"","value_label_source":source,"value_label_review":status,"harmonization_status":caveat})


def csv_update(path):
    df=pd.read_csv(path,dtype=str,encoding="utf-8-sig").fillna("")
    sel=df.apply(lambda r:(str(r["Source.Wave"]),str(r["Variable.Name"]).lower()) in FIELDS,axis=1)
    seen=set(zip(df.loc[sel,"Source.Wave"],df.loc[sel,"Variable.Name"].str.lower()))
    if seen!=FIELDS:raise ValueError(f"{path}: missing {sorted(FIELDS-seen)}")
    for i in df.index[sel]:
        row={};apply(row,str(df.at[i,"Source.Wave"]))
        for k in ("Concept.Unit.Candidates","Unit","Value.Labels","Value.Label.Source","Value.Label.Review","Harmonization.Status"):df.at[i,k]=row[k]
    df.to_csv(path,index=False,encoding="utf-8-sig");return int(sel.sum())


def json_update(path,wk,ck):
    rows=json.loads(path.read_text(encoding="utf-8")); fields=[f for x in rows for f in x["source_fields"]] if rows and "source_fields" in rows[0] else rows
    sel=[r for r in fields if (str(r.get(wk,"")),str(r.get(ck,"")).lower()) in FIELDS]
    seen={(str(r[wk]),str(r[ck]).lower()) for r in sel}
    if not sel:return 0
    if seen!=FIELDS:raise ValueError(f"{path}: missing {sorted(FIELDS-seen)}")
    for r in sel:
        row={};apply(row,str(r[wk]))
        if rows and "source_fields" in rows[0]:r.update({"unit":"m²","value_labels":"","value_label_status":row["Value.Label.Review"],"value_label_source":row["Value.Label.Source"],"note":row["Harmonization.Status"]})
        else:
            r.update({k:v for k,v in row.items() if k in ("Concept.Unit.Candidates","Unit","Value.Labels","Value.Label.Source","Value.Label.Review","Harmonization.Status","candidate_concept_units","value_labels","value_label_source","value_label_review","harmonization_status")})
            if wk=="wave":r.update({"unit":"m²","value_labels":"","value_label_status":row["Value.Label.Review"],"value_label_source":row["Value.Label.Source"],"mapping_status":row["Value.Label.Review"],"caveat":row["Harmonization.Status"]})
    path.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n" if wk=="wave" else json.dumps(rows,ensure_ascii=False,separators=(",",":")),encoding="utf-8");return len(sel)


def main():
    for wave,file in WAVES.items():
        text=(ROOT/"sources_official"/file).read_text(encoding="utf-8",errors="ignore").casefold()
        if "i002" not in text or not any(unit in text for unit in ("m2", "m²", "𝑚")):raise ValueError(f"questionnaire lacks homestead area/unit in {wave}")
    n=csv_update(ROOT/"audit/charls_atlas_candidate_fields_v0.csv")
    n+=json_update(ROOT/"audit/charls_atlas_candidate_fields_v0.json","Source.Wave","Variable.Name")
    n+=json_update(ROOT/"site-prototype/dist/catalog.json","Source.Wave","Variable.Name")
    n+=json_update(ROOT/"site-prototype/dist/catalog_e.json","Source.Wave","Variable.Name")
    n+=json_update(ROOT/"site-prototype/dist/food_environment_v1.json","wave","code")
    print(f"Applied homestead land-area notes to {n} metadata rows; no participant values or extrema used.")


if __name__=="__main__":main()
