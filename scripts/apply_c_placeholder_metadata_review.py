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
}
def compact(value): return re.sub(r"[^a-z0-9]", "", value.lower())
def propagate():
    review = pd.read_csv(OUTPUT, dtype=str, encoding="utf-8-sig").fillna("")
    targets = {(r.wave, r.code.lower()): r for r in review.itertuples(index=False)}
    for path in [ROOT/"audit/charls_atlas_candidate_fields_v0.csv", ROOT/"audit/charls_atlas_candidate_fields_v0.json", ROOT/"site-prototype/dist/catalog.json"]:
        if path.suffix == ".csv":
            data = pd.read_csv(path,dtype=str,encoding="utf-8-sig").fillna("");n=0
            for (wave,code),item in targets.items():
                m=data["Source.Wave"].eq(wave)&data["Variable.Name"].str.lower().eq(code)&data["epcf"].str.lower().eq("c")
                if m.any():
                    data.loc[m,"Value.Label.Review"]=item.review_status;data.loc[m,"Value.Label.Source"]=item.official_source;data.loc[m,"Value.Labels"]="";data.loc[m,"Review.Flag"]=item.catalog_note;data.loc[m,"Harmonization.Status"]=item.catalog_note;n+=int(m.sum())
            if n!=len(targets): raise SystemExit(f"Expected {len(targets)} C rows in {path}; updated {n}")
            data.to_csv(path,index=False,encoding="utf-8-sig")
        else:
            data=json.loads(path.read_text(encoding="utf-8"));n=0
            for row in data:
                key=(str(row.get("Source.Wave","")),str(row.get("Variable.Name","")).lower());item=targets.get(key)
                if item and str(row.get("epcf","")).lower()=="c":
                    row.update({"Value.Label.Review":item.review_status,"Value.Label.Source":item.official_source,"Value.Labels":"","Review.Flag":item.catalog_note,"Harmonization.Status":item.catalog_note,"value_label_review":item.review_status,"value_label_source":item.official_source,"value_labels":"","harmonization_status":item.catalog_note});n+=1
            if n!=len(targets): raise SystemExit(f"Expected {len(targets)} C rows in {path}; updated {n}")
            path.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
        print(f"Propagated {len(targets)} C metadata rows into {path.relative_to(ROOT)}")
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--propagate",action="store_true");args=parser.parse_args()
    if args.propagate: propagate();return
    rows=json.loads(CATALOG.read_text(encoding="utf-8"))
    targets=[r for r in rows if r.get("subcategory") in FAMILIES and r.get("Value.Label.Review","").strip().lower()=="not yet reviewed"]
    counts={family:sum(r["subcategory"]==family for r in targets) for family in FAMILIES}
    if counts!=FAMILIES: raise SystemExit(f"Unexpected C placeholder family counts: {counts}")
    audit=[]
    for r in targets:
        wave=str(r["Source.Wave"]);code=str(r["Variable.Name"]);source=f"sources_official/CHARLS_{wave}_Codebook_extracted.txt";path=ROOT/source
        if not path.exists() or compact(code) not in compact(path.read_text(encoding="utf-8",errors="replace")):
            raise SystemExit(f"Codebook field not confirmed: {wave}/{code}")
        if r["subcategory"]=="unsupported prior-wave disease-awareness slots":
            note="Unsupported prior-wave disease-slot placeholder; no disease identity or complete response set is established. Do not infer No from a blank slot; exclude from analysis."
        elif r["subcategory"]=="unlisted chronic-disease index placeholder":
            note="Unlisted disease-index placeholder; source field exists but no standardized condition identity is established. Do not infer a phenotype or harmonize."
        else:
            note="Inactive 2015 household lending/debt legacy field; official Codebook supplies no observed response categories or amount. Retain as source metadata only."
        audit.append({"wave":wave,"code":code,"metadata_family":r["subcategory"],"official_source":source,"source_field_label":r.get("Variable.Description",""),"review_status":"official wave Codebook field checked; unresolved/legacy C metadata only; no response-value categories assigned","value_labels":"","catalog_note":note})
    pd.DataFrame(audit).sort_values(["wave","metadata_family","code"]).to_csv(OUTPUT,index=False,encoding="utf-8-sig")
    print(f"Audited {len(audit)} C placeholder/legacy fields across official Codebooks; no categories inferred.")
if __name__=="__main__":main()
