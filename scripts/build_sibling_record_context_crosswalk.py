"""Map respondent- and spouse-sibling record context with module-qualified links."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"audit"
RAW=pd.read_csv(AUDIT/"raw_variable_catalog_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
LABELS={
"cc003_w3":"1=No formal education (illiterate); 2=Did not finish primary school; 3=Sishu/home school; 4=Elementary school; 5=Middle school; 6=High school; 7=Vocational school; 8=Two-/three-year college/associate degree; 9=Four-year college/bachelor's degree; 10=Master's degree; 11=Doctoral/PhD",
"cc005_w3":"1=Yes; 2=No",
"cc011_w3":"1=Married with spouse at present; 2=Married but not living with spouse temporarily; 3=Separated; 4=Divorced; 5=Widowed; 6=Never married; 7=Cohabitated",
}
DISPLAY={"cc003_w3":"Highest Level of Education","cc005_w3":"Ethnic Minority Status","cc011_w3":"Marital Status"}
CONSTRUCT={"cc003_w3":"reported highest education of one sibling record","cc005_w3":"reported ethnic-minority status of one sibling record","cc011_w3":"reported marital status of one sibling record"}
rows=[]
for module, prefix, relation in [("Sibling","respondent_sibling","respondent's sibling"),("Spousal_Sibling","spousal_sibling","spouse's sibling")]:
 for code in ["cc003_w3","cc005_w3","cc011_w3"]:
  found=RAW[(RAW.wave=="2015")&RAW.module.eq(module)&RAW.variable.str.lower().eq(code)]
  if found.empty: raise SystemExit(f"Missing official 2015 {module}/{code}")
  rec=found.iloc[0]; concept=f"{prefix}_{ {'cc003_w3':'education','cc005_w3':'ethnicity','cc011_w3':'marital_status'}[code]}_record_2015"
  label=("受访者兄弟姐妹" if module=="Sibling" else "配偶兄弟姐妹")+{"cc003_w3":"最高受教育程度","cc005_w3":"少数民族身份","cc011_w3":"婚姻状况"}[code]+"（记录级）"
  source_label=("Sibling's " if module=="Sibling" else "Spouse's sibling's ")+DISPLAY[code]
  rows.append({"wave":"2015","code":code,"concept_id":concept,"concept_label":label,"domain":"family and intergenerational context","subcategory":"sibling record context","module":module,"source_label":source_label,"mapping_status":"discovery candidate; official codebook reviewed; module and sibling record unit preserved; respondent-level aggregation not approved","unit":f"{relation} record; link by respondent ID and siblingID; source module={module}","value_labels":LABELS[code],"value_label_status":"official questionnaire/codebook categories reviewed; codebook frequencies omitted","value_label_source":"sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt","construct":f"{CONSTRUCT[code]} for {relation}; keep one record per linked sibling and retain source module.","value_semantics":"categorical record-level response; not a single respondent-level exposure until a prespecified sibling aggregation and relationship rule is defined","caveat":"Sibling and Spousal_Sibling are distinct modules using identical source codes. This mapping is module-qualified. Multiple sibling records may occur for one respondent; do not treat them as independent respondents or collapse without a prespecified estimand. Spousal-sibling items apply only on the spouse/family route. No sibling-level values or frequencies were read.","source_archive":f"{rec.source}; official questionnaire/codebook"})
out=pd.DataFrame(rows)
if out.duplicated(["wave","code","module"]).any(): raise SystemExit("Duplicate sibling wave/module/code")
out.to_csv(AUDIT/"sibling_record_context_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
print(f"sibling record context mappings={len(out)}; concepts={out.concept_id.nunique()}")
