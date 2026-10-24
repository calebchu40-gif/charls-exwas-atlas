"""Audit unsupported/legacy disease and household fields retained as C metadata."""
import argparse
import json
import re
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "site-prototype/dist/catalog_c.json"
OUTPUT = ROOT / "audit/c_placeholder_metadata_review_v1.csv"
FAMILIES = {
    "unsupported prior-wave disease-awareness slots": 15,
    "unlisted chronic-disease index placeholder": 5,
    "inactive household lending and debt legacy fields": 4,
    "household debt unfolding-bracket response metadata": 8,
    "personal wage deduction scope and response-unit selectors": 3,
    "household income response-format selectors": 3,
    "chair setup for repeated chair-stand test": 4,
    "household financial respondent source": 2,
    "inactive fixed-capital legacy/format fields": 2,
    "2020 pandemic work-module selection flag": 1,
    "unresolved questionnaire and Codebook field identity conflict": 1,
    "2013 money-management helper relationship option slots": 62,
}
def compact(value): return re.sub(r"[^a-z0-9]", "", value.lower())
def propagate():
    review = pd.read_csv(OUTPUT, dtype=str, encoding="utf-8-sig").fillna("")
    targets = {(r.wave, r.code.lower()): r for r in review.itertuples(index=False)}
    for path in [ROOT/"audit/charls_atlas_candidate_fields_v0.csv", ROOT/"audit/charls_atlas_candidate_fields_v0.json", ROOT/"audit/charls_atlas_candidate_series_v0.csv", ROOT/"audit/charls_atlas_candidate_series_v0.json", ROOT/"site-prototype/dist/catalog.json"]:
        if path.suffix == ".csv":
            data = pd.read_csv(path,dtype=str,encoding="utf-8-sig").fillna("");n=0
            for (wave,code),item in targets.items():
                if "candidate_series_v0" in path.name:
                    m=data["waves"].str.split(";").apply(lambda values: wave in values)&data["Variable.Name"].str.lower().eq(code)&data["epcf"].str.lower().eq("c")
                    if m.any():
                        data.loc[m,"value_label_review"]=item.review_status;data.loc[m,"value_label_source"]=item.official_source;data.loc[m,"value_labels"]=getattr(item,"value_labels","");data.loc[m,"harmonization_status"]=item.catalog_note;n+=int(m.sum())
                        if item.metadata_family == "2013 money-management helper relationship option slots":
                            data.loc[m,"category"]="source-detail metadata";data.loc[m,"subcategory"]="money-management helper relationship option slots"
                    continue
                m=data["Source.Wave"].eq(wave)&data["Variable.Name"].str.lower().eq(code)&data["epcf"].str.lower().eq("c")
                if m.any():
                    data.loc[m,"Value.Label.Review"]=item.review_status;data.loc[m,"Value.Label.Source"]=item.official_source;data.loc[m,"Value.Labels"]=getattr(item,"value_labels","");data.loc[m,"Review.Flag"]=item.catalog_note;data.loc[m,"Harmonization.Status"]=item.catalog_note;n+=int(m.sum())
                    if item.metadata_family == "2013 money-management helper relationship option slots":
                        data.loc[m,"Candidate.Status"]="C source-detail metadata; helper relationship option slot; not a standalone exposure or phenotype"
                        data.loc[m,"category"]="source-detail metadata"
                        data.loc[m,"subcategory"]="money-management helper relationship option slots"
            expected=len(targets)
            if "candidate_series_v0" in path.name:
                expected=sum(any(str(row.get("Variable.Name","" )).lower()==code and wave in str(row.get("waves","" )).split(";") for (wave,code) in targets) for row in data.to_dict("records"))
            if n!=expected: raise SystemExit(f"Expected {expected} C series rows in {path}; updated {n}")
            data.to_csv(path,index=False,encoding="utf-8-sig")
        else:
            data=json.loads(path.read_text(encoding="utf-8"));n=0
            for row in data:
                if "candidate_series_v0" in path.name:
                    for (wave,code),item in targets.items():
                        if str(row.get("epcf","" )).lower()=="c" and str(row.get("Variable.Name","" )).lower()==code and wave in str(row.get("waves","" )).split(";"):
                            row.update({"value_label_review":item.review_status,"value_label_source":item.official_source,"value_labels":getattr(item,"value_labels",""),"harmonization_status":item.catalog_note});n+=1
                            if item.metadata_family == "2013 money-management helper relationship option slots":
                                row.update({"category":"source-detail metadata","subcategory":"money-management helper relationship option slots"})
                    continue
                key=(str(row.get("Source.Wave","")),str(row.get("Variable.Name","")).lower());item=targets.get(key)
                if item and str(row.get("epcf","")).lower()=="c":
                    row.update({"Value.Label.Review":item.review_status,"Value.Label.Source":item.official_source,"Value.Labels":getattr(item,"value_labels",""),"Review.Flag":item.catalog_note,"Harmonization.Status":item.catalog_note,"value_label_review":item.review_status,"value_label_source":item.official_source,"value_labels":getattr(item,"value_labels",""),"harmonization_status":item.catalog_note});n+=1
                    if item.metadata_family == "2013 money-management helper relationship option slots":
                        row.update({"Candidate.Status":"C source-detail metadata; helper relationship option slot; not a standalone exposure or phenotype","category":"source-detail metadata","subcategory":"money-management helper relationship option slots"})
            expected=len(targets)
            if "candidate_series_v0" in path.name:
                expected=sum(any(str(row.get("Variable.Name","" )).lower()==code and wave in str(row.get("waves","" )).split(";") for (wave,code) in targets) for row in data)
            if n!=expected: raise SystemExit(f"Expected {expected} C series rows in {path}; updated {n}")
            path.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
        print(f"Propagated {len(targets)} C metadata rows into {path.relative_to(ROOT)}")
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--propagate",action="store_true");args=parser.parse_args()
    if args.propagate: propagate();return
    rows=json.loads(CATALOG.read_text(encoding="utf-8"))
    current=[r for r in rows if (r.get("subcategory") in FAMILIES or (r.get("Source.Wave")=="2013" and re.fullmatch(r"db022_w2_9_[12]_s\d+",str(r.get("Variable.Name","")),re.I))) and r.get("Value.Label.Review","").strip().lower()=="not yet reviewed"]
    prior_keys=set()
    if OUTPUT.exists():
        prior=pd.read_csv(OUTPUT,dtype=str,encoding="utf-8-sig").fillna("")
        prior_keys={(str(r.wave),str(r.code).lower()) for r in prior.itertuples(index=False)}
    current_keys={(str(r["Source.Wave"]),str(r["Variable.Name"]).lower()) for r in current}
    target_keys=prior_keys|current_keys
    targets=[r for r in rows if (str(r.get("Source.Wave","")),str(r.get("Variable.Name"," ")).lower()) in target_keys and str(r.get("epcf"," ")).lower()=="c"]
    counts={family:sum(bool((family=="2013 money-management helper relationship option slots" and r.get("Source.Wave")=="2013" and re.fullmatch(r"db022_w2_9_[12]_s\d+",str(r.get("Variable.Name","")),re.I)) or (family!="2013 money-management helper relationship option slots" and r.get("subcategory")==family)) for r in targets) for family in FAMILIES}
    if counts!=FAMILIES: raise SystemExit(f"Unexpected C metadata family counts: {counts}")
    audit=[]
    for r in targets:
        wave=str(r["Source.Wave"]);code=str(r["Variable.Name"]);source=f"sources_official/CHARLS_{wave}_Codebook_extracted.txt";path=ROOT/source
        if not path.exists() or compact(code) not in compact(path.read_text(encoding="utf-8",errors="replace")):
            raise SystemExit(f"Codebook field not confirmed: {wave}/{code}")
        family=r["subcategory"]
        if wave=="2013" and re.fullmatch(r"db022_w2_9_[12]_s\d+",code,re.I):
            family="2013 money-management helper relationship option slots"
        notes={
          "unsupported prior-wave disease-awareness slots":"Unsupported prior-wave disease-slot placeholder; no disease identity or complete response set is established. Do not infer No from a blank slot; exclude from analysis.",
          "unlisted chronic-disease index placeholder":"Unlisted disease-index placeholder; source field exists but no standardized condition identity is established. Do not infer a phenotype or harmonize.",
          "inactive household lending and debt legacy fields":"Inactive 2015 household lending/debt legacy field; official Codebook supplies no observed response categories or amount. Retain as source metadata only.",
          "household debt unfolding-bracket response metadata":"Conditional fallback debt-bracket protocol after the exact amount is not supplied; bounds are not an exact debt amount. Do not calculate a midpoint or treat components as independent exposures.",
          "personal wage deduction scope and response-unit selectors":"Interview assistance/proxy or response-scope metadata only; not a respondent exposure, phenotype, or routine covariate.",
          "household income response-format selectors":"Pre-2018 household rental-income response-format metadata; distinguish amount/not-applicable routing from later Yes/No status items. Do not treat as a household income measure.",
          "chair setup for repeated chair-stand test":"Chair height/setup protocol metadata for the repeated chair-stand assessment; not a participant phenotype. Preserve instrument setup when interpreting the linked performance measure.",
          "household financial respondent source":"Identifies the informant selected for the household financial module; not a respondent trait or independent exposure. Retain only for source/response context.",
          "inactive fixed-capital legacy/format fields":"2015 inactive or unresolved fixed-capital legacy/format field; do not infer a current asset value or response category from the field label.",
          "2020 pandemic work-module selection flag":"CAPI work-module selection/eligibility flag; not a pandemic exposure or work outcome. Preserve selection route and do not substitute it for respondent eligibility without release validation.",
          "unresolved questionnaire and Codebook field identity conflict":"Questionnaire/Codebook field-identity conflict. Keep response labels blank and retain DO NOT ANALYZE until the official field mapping and released-data coding are reconciled.",
          "2013 money-management helper relationship option slots":"2013 DB022_W2_9 helper-relationship choice slot in a loop allowing up to two helpers. Each field is one relationship option, not an independent yes/no social exposure or outcome; preserve slot and routing, do not infer non-selection from blanks, and do not count the 64 options as separate constructs. Codebook frequencies are omitted.",
        }
        note=notes[family]
        source_files=source
        review_status="official wave Codebook field checked; measurement/routing metadata only; no response-value categories assigned"
        if family=="2013 money-management helper relationship option slots":
            questionnaire="sources_official/CHARLS_2013_Questionnaire_extracted.txt"
            if not (ROOT/questionnaire).exists(): raise SystemExit(f"Official questionnaire missing: {questionnaire}")
            source_files=f"{questionnaire}; {source}"
            review_status="official 2013 questionnaire and Codebook reviewed; relationship option slots retained as source detail; no cross-wave construct or response denominator inferred"
        audit.append({"wave":wave,"code":code,"metadata_family":family,"official_source":source_files,"source_field_label":r.get("Variable.Description",""),"review_status":review_status,"value_labels":"","catalog_note":note})
    pd.DataFrame(audit).sort_values(["wave","metadata_family","code"]).to_csv(OUTPUT,index=False,encoding="utf-8-sig")
    print(f"Audited {len(audit)} C placeholder/legacy fields across official Codebooks; no categories inferred.")
if __name__=="__main__":main()
