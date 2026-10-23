"""Apply source-backed wave-specific review to individual income candidates."""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/"audit/personal_income_exposure_mapping_v1.csv"
QUESTIONNAIRE={"2011":"CHARLS_2011_Baseline_Questionnaire_official_extracted.txt","2013":"CHARLS_2013_Questionnaire_extracted.txt","2015":"CHARLS_2015_Questionnaire_extracted.txt","2018":"CHARLS_2018_Questionnaire_extracted.txt","2020":"CHARLS_2020_Questionnaire_English_extracted.txt"}
BINARY={"2011":{"hc004","hc007","hc010","hc015","hc027","hc030","hc036"},"2013":{"hc007","hc010","hc015","hc027","hc030","hc036"},"2015":{"hc007","hc010","hc015","hc027","hc030","hc036","hc039_w3","hd005_w3"},"2018":{"hc007","hc010","hc015","hc027","hc030","hc039_w3"}}
CHECKBOX={"2011":{"hd008s1","hd008s2","hd008s3","hd008s4","hd008s5"},"2013":{"hd008s1","hd008s2","hd008s3","hd008s4","hd008s5"}}
NUMERIC={"2011":{"ga002":"Yuan/year; alternative field ga002_1 is Yuan/month","ga002_1":"Yuan/month; alternative to annual field ga002"},"2013":{"ga002_1":"Yuan/year"},"2015":{"ga002":"Yuan/year"},"2018":{"ga002":"Yuan/year","hd005_w4_0":"event count; number of lifetime fraud experiences with property loss"},"2020":{"ga002":"Yuan/year","ga006_1":"Yuan; COVID-period wage decrease amount, conditional on decrease","ga006_2":"Yuan; COVID-period wage increase amount, conditional on increase"}}
def compact(x): return re.sub(r"[^a-z0-9]", "", x.lower())
def main():
 d=pd.read_csv(MAP,dtype=str,encoding="utf-8-sig").fillna("")
 targets=d[d["value_label_status"].eq("")].copy(); n=0
 for i,r in targets.iterrows():
  w,c=r.wave,r.code.lower(); q=ROOT/"sources_official"/QUESTIONNAIRE[w]; cb=ROOT/"sources_official"/f"CHARLS_{w}_Codebook_extracted.txt"
  qt=q.read_text(encoding="utf-8",errors="replace"); ct=cb.read_text(encoding="utf-8",errors="replace")
  if c in BINARY.get(w,set()):
   if c not in qt.lower(): raise SystemExit(f"Questionnaire entry missing: {w}/{c}")
   labels="1=Yes; 2=No" if w!="2018" else "1=Yes; 2=No; 999=Refused to answer"
   status="official questionnaire response categories transcribed; Codebook frequencies omitted; validate authorized-release coding and eligible denominator"
   semantic="Binary respondent-level item. Categories follow the wave-specific official questionnaire; 2018 additionally identifies 999=refusal. Preserve routing and special/missing values; do not pool as comparable until wording and reference period are harmonized."
  elif c in CHECKBOX.get(w,set()):
   if c not in ct.lower() or "check all that apply" not in qt.lower(): raise SystemExit(f"Checkbox evidence missing: {w}/{c}")
   labels=""; status="official Codebook identifies affirmative inheritance-source option; unselected storage and denominator unresolved; no response-value labels assigned"
   semantic="Nonexclusive inheritance-source checkbox option. The official Codebook's affirmative option code identifies the selected source; it does not establish the unselected value or eligible denominator. Do not infer No from blank/missing. No frequencies copied."
  elif c in NUMERIC.get(w,{}):
   if compact(c) not in compact(qt) or compact(c) not in compact(ct): raise SystemExit(f"Questionnaire/Codebook field missing: {w}/{c}")
   labels=""; status="official questionnaire/Codebook field reviewed; continuous amount/count, no categorical response labels; preserve unit and route"
   semantic=NUMERIC[w][c]+" Continuous measurement; Codebook descriptive summaries are not respondent-level data or analytic cutoffs. Preserve source scale, special values, missingness, and conditional route."
  elif w=="2020" and c=="ga003":
   labels="1=Yes; 2=No; 997=Do not know; 999=Refused to answer"
   status="official questionnaire/Codebook response labels reviewed; frequencies omitted; preserve special codes"
   semantic="Indicates whether reported wage excludes insurance, income tax, public housing fund, and other fees; this is a scope/measurement flag, not an exposure amount. Preserve 997/999 and routed follow-up."
  else: continue
  src=f"sources_official/{q.name}; sources_official/{cb.name}"
  r["value_labels"]=labels; r["value_label_status"]=status; r["value_label_source"]=src; r["value_semantics"]=semantic; r["mapping_status"]=status
  caveat=r["caveat"].strip(" ;")
  if semantic not in caveat: caveat+= "; "+semantic
  r["caveat"]=caveat; d.loc[i,r.index]=r; n+=1
 d.to_csv(MAP,index=False,encoding="utf-8-sig")
 print(f"Reviewed {n} individual income/wage fields; source-specific categories, units, routes, and checkbox uncertainty retained; no frequencies copied.")
if __name__=="__main__": main()
