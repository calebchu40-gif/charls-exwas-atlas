"""Map parent-level hukou context as gated exploratory exposure candidates."""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"audit"
RAW=pd.read_csv(AUDIT/"raw_variable_catalog_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
GATE=("Parent-module records are not respondent-level rows. Link by respondent ID and parentID; in 2013 additionally restrict parent type ca003 to biological parent; in 2015 parentID codes 1/2 identify biological father/mother. Keep father and mother records distinct and exclude in-laws, spouse's parents, step/adoptive/foster parents, and other relatives. A respondent-level derivation and estimand must be prespecified before analysis; current catalog entry is discovery-only and not approved for an association model.")
SPECS=[
("2013","ca018","parent_hukou_residence_concordance","父母户口与现居住地是否一致（亲属记录）","Is Parent's Hukou the Same Place as His Current Residence","1=Yes; 2=No; 3=Does not have hukou","Asked conditionally for linked parent record; preserve no-hukou as its own response category, not missing or no.","social determinants","family residential context"),
("2015","ca018","parent_hukou_residence_concordance","父母户口与现居住地是否一致（亲属记录）","Parent's Hukou Is in The Same Place As Current Residence","1=Yes; 2=No; 3=Does not have hukou where listed","Question is asked only on applicable parent record route; preserve the official category set and structural skip.","social determinants","family residential context"),
("2013","ca019","parent_current_hukou_location_relation","父母当前户口登记地关系（亲属记录）","Location of Parent's Current Hukou","1=Parent's birthplace; 2=Respondent's birthplace; 3=Respondent's permanent-address village/neighborhood; 4=Another village/neighborhood in respondent's permanent-address city/county; 5=Other; 6=Abroad","Keep only coded relation response. Geographic detail fields are excluded; category meanings are relative to respondent and should not be read as coordinates or distance.","social determinants","family residential context"),
("2015","ca019","parent_current_hukou_location_relation","父母当前户口登记地关系（亲属记录）","Location Of Parent's Current Hukou","1=Parent's birthplace; 2=Respondent's birthplace; 3=Respondent's permanent-address village/neighborhood; 4=Another village/neighborhood in respondent's permanent-address county/city/district; 5=Other; 6=Abroad","Keep only coded relation response. Geographic detail fields are excluded; category meanings are relative to respondent and should not be read as coordinates or distance.","social determinants","family residential context"),
("2013","ca020","parent_current_hukou_type","父母当前户口类别（亲属记录）","Parent's Current Hukou Status","1=Agricultural hukou; 2=Non-agricultural hukou; 3=Unified residency hukou","2013 categories do not list the later no-hukou code; do not infer equivalence or recode skips.","social determinants","family social position"),
("2015","ca020","parent_current_hukou_type","父母当前户口类别（亲属记录）","Current Hukou Status","1=Agricultural hukou; 2=Non-agricultural hukou; 3=Unified residency hukou; 4=Does not have hukou","Keep 2015's explicit no-hukou category; do not force same numeric code sets across waves.","social determinants","family social position"),
]
rows=[]
for wave,code,cid,label,source_label,labels,note,domain,subcat in SPECS:
    found=RAW[(RAW.wave==wave)&RAW.module.str.lower().eq("parent")&RAW.variable.str.lower().eq(code)]
    if found.empty: raise SystemExit(f"Missing Parent-module source: {wave}/{code}")
    rec=found.iloc[0]
    questionnaire=f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt"
    codebook=f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    rows.append({"wave":wave,"code":code,"concept_id":cid,"concept_label":label,"domain":domain,"subcategory":subcat,"module":rec.module,"source_label":source_label,"mapping_status":"discovery candidate only; official question and codebook reviewed; respondent-level parent linkage/aggregation required before analysis","unit":"parent record; respondent ID + parentID linkage required","value_labels":labels,"value_label_status":"official questionnaire and codebook categories reviewed; frequencies omitted","value_label_source":f"{questionnaire}; {codebook}","construct":f"Parent-record context: {label}; retain parent relationship and respondent linkage.","value_semantics":"categorical, parent-record-level response; preserve wave-specific categories and skips; no automatic aggregation across parents","caveat":note+" "+GATE,"source_archive":f"{rec.source}; {questionnaire}; {codebook}"})
out=pd.DataFrame(rows)
if out.duplicated(["wave","code"]).any(): raise SystemExit("Duplicate parent context wave/code")
out.to_csv(AUDIT/"parent_roster_context_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
print(f"parent roster context mappings={len(out)}; concepts={out.concept_id.nunique()}")
