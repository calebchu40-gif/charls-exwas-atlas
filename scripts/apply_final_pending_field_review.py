"""Resolve the final generic E review statuses without removing analysis locks."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"sources_official"
def read_csv(name): return pd.read_csv(ROOT/"audit"/name,dtype=str,encoding="utf-8-sig").fillna("")
def write_csv(name,d): d.to_csv(ROOT/"audit"/name,index=False,encoding="utf-8-sig")
def compact(x): return "".join(ch.lower() for ch in x if ch.isalnum())
def main():
 # 2011 monthly household expenditure: continuous amounts, no answer categories.
 p="household_economic_exposure_mapping_v1.csv"; d=read_csv(p)
 for code,label in {"ge010_4":"Furniture and Consumption of Durable Goods","ge010_6":"Medical Expenditure","ge010_7":"Fitness Expenditure"}.items():
  m=d.wave.eq("2011")&d.code.str.lower().eq(code)
  if m.sum()!=1: raise SystemExit(f"Missing household expenditure row 2011/{code}")
  q=(SRC/"CHARLS_2011_Baseline_Questionnaire_official_extracted.txt").read_text(encoding="utf8",errors="replace")
  cb=(SRC/"CHARLS_2011_Codebook_extracted.txt").read_text(encoding="utf8",errors="replace")
  if compact(code) not in compact(q) or compact(code) not in compact(cb): raise SystemExit(f"Source entry missing 2011/{code}")
  sem=f"Household-level {label.lower()} expenditure reported for the past month, in Yuan. Continuous amount; no categorical response labels. Preserve the household respondent, reference period, wave-specific item list and source route; Codebook descriptive summaries are not valid ranges or analysis cutoffs."
  d.loc[m,"unit"]="Yuan (past month)";d.loc[m,"value_label_status"]="official Codebook lists numeric summary; no categorical response menu in this entry";d.loc[m,"value_label_source"]="sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt";d.loc[m,"value_semantics"]=sem
 write_csv(p,d)
 # Keep the no-category status discoverable in the catalogue review layer.
 p="household_income_numeric_status_v1.csv";d=read_csv(p)
 for code,label in {"ge010_4":"Furniture and Consumption of Durable Goods","ge010_6":"Medical Expenditure","ge010_7":"Fitness Expenditure"}.items():
  if not ((d.wave=="2011")&(d.code.str.lower()==code)).any():
   d.loc[len(d)]={"wave":"2011","code":code,"official_codebook_label":label,"value_label_status":"official Codebook lists numeric summary; no categorical response menu in this entry","value_label_source":"sources_official/CHARLS_2011_Codebook_extracted.txt","review_scope":"Continuous past-month household expenditure in Yuan; source location only; preserve route/denominator/special-code review."}
 write_csv(p,d)
 # Continuous count of other jobs in the interwave window.
 p="interwave_other_job_crosswalk_v1.csv";d=read_csv(p);m=d.wave.eq("2013")&d.code.str.lower().eq("fa006_w2_5")
 if m.sum()!=1: raise SystemExit("Missing 2013/fa006_w2_5")
 d["value_label_status"]=d.get("value_label_status","");d["value_label_source"]=d.get("value_label_source","")
 d.loc[m,"value_label_status"]="official Codebook field located; continuous job count; no categorical response labels; interwave route retained";d.loc[m,"value_label_source"]="sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt"
 write_csv(p,d)
 # Personal wage-change direction in 2020; the amount fields remain distinct.
 p="personal_income_exposure_mapping_v1.csv";d=read_csv(p);m=d.wave.eq("2020")&d.code.str.lower().eq("ga006")
 if m.sum()!=1: raise SystemExit("Missing 2020/ga006")
 q=(SRC/"CHARLS_2020_Questionnaire_English_extracted.txt").read_text(encoding="utf8",errors="replace");cb=(SRC/"CHARLS_2020_Codebook_extracted.txt").read_text(encoding="utf8",errors="replace")
 if "GA006" not in q.upper() or "ga006:" not in cb.lower(): raise SystemExit("2020 GA006 questionnaire/Codebook entry missing")
 d.loc[m,"value_labels"]="1=Decreased; 2=Increased; 3=Unaffected";d.loc[m,"value_label_status"]="official questionnaire/codebook response labels reviewed; frequencies omitted; COVID period and route retained";d.loc[m,"value_label_source"]="sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt";d.loc[m,"value_semantics"]="Retrospective respondent-reported wage direction from Chinese New Year to interview attributed to COVID-19; distinct from the conditional amount fields ga006_1 and ga006_2. Single-wave item; not a causal effect estimate.";d.loc[m,"mapping_status"]="official questionnaire/codebook response labels reviewed; frequencies omitted; COVID period and route retained"
 write_csv(p,d)
 # Official asset-rental status items, wave-specific source labels and codes.
 p="household_other_asset_rental_income_status_crosswalk_v1.csv";d=read_csv(p);
 if "value_label_status" not in d:d["value_label_status"]=""
 if "value_label_source" not in d:d["value_label_source"]=""
 for w,c in [("2018","ha064"),("2020","ge014")]:
  m=d.wave.eq(w)&d.code.str.lower().eq(c)
  if m.sum()!=1: raise SystemExit(f"Missing rental status {w}/{c}")
  source=f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt" if w=="2018" else "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt"
  d.loc[m,"value_labels"]="1=Yes; 2=No; 997=Don’t know; 999=Refused to answer";d.loc[m,"value_label_status"]="official questionnaire and Codebook response labels reviewed; frequencies omitted; household route and denominator require validation";d.loc[m,"value_label_source"]=source
 write_csv(p,d)
 # Preserve the existing questionnaire/Codebook conflict lock for the 2020 coping options.
 p="household_covid_economic_crosswalk_v1.csv";d=read_csv(p)
 for col in ["value_label_status","value_label_source"]:
  if col not in d:d[col]=""
 m=d.wave.eq("2020")&d.code.str.lower().eq("gf015_s4")
 if m.sum()!=1:raise SystemExit("Missing 2020/gf015_s4")
 d.loc[m,"value_labels"]="0=No; 4=Yes";d.loc[m,"value_label_status"]="official Codebook response labels transcribed; frequencies omitted; retain DO NOT ANALYZE lock pending none-option validation";d.loc[m,"value_label_source"]="sources_official/CHARLS_2020_Codebook_extracted.txt"
 m=d.wave.eq("2020")&d.code.str.lower().eq("gf016_s8")
 if m.sum()!=1:raise SystemExit("Missing 2020/gf016_s8")
 d.loc[m,"value_labels"]="";d.loc[m,"value_label_status"]="questionnaire/Codebook option identity conflict; DO NOT ANALYZE; no response-value labels assigned";d.loc[m,"value_label_source"]="sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt"
 # Keep original DO NOT ANALYZE mapping_status and caveats untouched.
 write_csv(p,d)
 # Preserve occupation code semantics: code families are not answer categories.
 p="work_exposure_value_labels_v1.csv";d=read_csv(p)
 for code in ["fh015_gb","fh015_isco"]:
  m=d.wave.eq("2011")&d.code.str.lower().eq(code)
  if m.sum()!=1:raise SystemExit(f"Missing occupation mapping 2011/{code}")
  d.loc[m,"value_label_status"]="occupation classification code; Codebook frequency distribution omitted; classification definitions are not response labels; unpaid family-business route retained";d.loc[m,"value_label_source"]="sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt"
 # 2020 fa019 has categories, but its explicit analysis lock remains.
 m=d.wave.eq("2020")&d.code.str.lower().eq("fa019")
 if m.sum()!=1:raise SystemExit("Missing 2020/fa019")
 d.loc[m,"value_label_status"]="official 2020 questionnaire response categories; frequencies omitted; conditional prior-status correction route; DO NOT ANALYZE pending route and released-data reconciliation"
 write_csv(p,d)
 print("Reviewed all 12 remaining generic-pending E fields: continuous amounts/counts, sourced categories, and unresolved conflicts/analysis locks retained.")
if __name__=="__main__":main()
