"""Apply source-checked value labels to 2011–2020 education and hukou candidates."""
from pathlib import Path
import re
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/"audit/demographic_social_exposure_mapping_v1.csv"
Q={"2011":"CHARLS_2011_Baseline_Questionnaire_official_extracted.txt","2013":"CHARLS_2013_Questionnaire_extracted.txt","2015":"CHARLS_2015_Questionnaire_extracted.txt","2018":"CHARLS_2018_Questionnaire_extracted.txt","2020":"CHARLS_2020_Questionnaire_English_extracted.txt"}
HUKOU={
("2011","bc001"):"1=Agricultural Hukou; 2=Non-agricultural Hukou; 3=Unified Residence Hukou; 4=Do not have Hukou",
("2011","bc005"):"1=Same as birthplace; 2=This village/neighborhood; 3=Another village/neighborhood in this county/city; 4=Another county/city in this province; 5=Another province",
("2013","bc001"):"1=Agricultural Hukou; 2=Non-agricultural Hukou; 3=Unified Residence Hukou; 4=Do not have Hukou",
("2013","bc005"):"1=Permanent address; 2=Birthplace; 3=Another neighborhood in permanent county/city/district; 4=Other city/district within this province; 5=Other province/city/district",
("2015","bc002_w3_1"):"1=Agricultural Hukou; 2=Non-agricultural Hukou; 3=Unified Residence Hukou; 4=Do not have Hukou",
("2018","bc002_w3_1"):"1=Agricultural Hukou; 2=Non-agricultural Hukou; 3=Unified Residence Hukou; 4=Do not have Hukou",
("2018","bc002_w3_4"):"1=Current residential address; 2=Other; 3=Do not have Hukou",
("2020","ba009"):"1=Agricultural Hukou; 2=Non-agricultural Hukou; 3=Unified Residence Hukou; 4=Do not have Hukou",
}
EDU_BASE="1=No formal education (illiterate); 2=Did not finish primary school but can read/write; 3=Sishu/home school; 4=Elementary school; 5=Middle school; 6=High school; 7=Vocational school; 8=Two/three-year college/associate degree; 9=Four-year college/bachelor’s degree; 10=Master’s degree"
EDU={("2011","bd001"):EDU_BASE,("2013","bd001"):EDU_BASE,("2013","bd001_w2_4"):EDU_BASE+"; 12=No change",("2015","bd001_w2_4"):EDU_BASE+"; 12=No change",("2018","bd001_w2_4"):EDU_BASE+"; 11=Doctoral degree/Ph.D.",("2020","ba010"):EDU_BASE+"; 11=Doctoral degree/Ph.D."}
ALIASES={("2013","bc001"):"zbc001",("2013","bc005"):"zbc005",("2013","bd001"):"zbd001"}
def compact(s):return re.sub(r"[^a-z0-9]","",s.lower())
def main():
 d=pd.read_csv(MAP,dtype=str,encoding="utf-8-sig").fillna(""); targets={**HUKOU,**EDU}; done=0
 for (w,c),labels in targets.items():
  mask=d.wave.eq(w)&d.code.str.lower().eq(c.lower())
  if mask.sum()!=1: raise SystemExit(f"Expected one mapping row {w}/{c}, got {mask.sum()}")
  qpath=ROOT/"sources_official"/Q[w]; cbpath=ROOT/"sources_official"/f"CHARLS_{w}_Codebook_extracted.txt"
  qt=qpath.read_text(encoding="utf8",errors="replace"); ct=cbpath.read_text(encoding="utf8",errors="replace")
  if compact(c) not in compact(qt): raise SystemExit(f"Official questionnaire field missing {w}/{c}")
  source_code=ALIASES.get((w,c),c)
  if compact(source_code) not in compact(ct): raise SystemExit(f"Official Codebook field/alias missing {w}/{c}: {source_code}")
  if w=="2013" and c in {"bc001","bc005","bd001"}:
   caveat="The 2013 Codebook uses the Z-prefixed alias for this questionnaire field; preserve the exact release variable name and verify the alias in the authorized dataset before analysis."
  else: caveat="These are wave-specific categorical codes. Preserve conditional routing, special/missing values and source wording; this review does not establish analytic eligibility or cross-wave equivalence."
  status="official questionnaire and codebook response labels reviewed; frequencies omitted; verify routed denominator and authorized-release special codes"
  d.loc[mask,"value_labels"]=labels;d.loc[mask,"value_label_status"]=status;d.loc[mask,"value_label_source"]=f"sources_official/{qpath.name}; sources_official/{cbpath.name}";d.loc[mask,"mapping_status"]=status
  old=d.loc[mask,"caveat"].iloc[0].strip(" ;")
  if caveat not in old:old+="; "+caveat
  d.loc[mask,"caveat"]=old;done+=1
 d.to_csv(MAP,index=False,encoding="utf-8-sig");print(f"Reviewed {done} education/hukou fields; wave-specific categories retained; no frequencies copied.")
if __name__=="__main__":main()
