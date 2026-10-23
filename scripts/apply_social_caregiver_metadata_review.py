"""Review source-coded formal caregiver options and helper-days measure."""
from pathlib import Path
import re
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/"audit/social_exposure_crosswalk_v1.csv"
Q={"2011":"CHARLS_2011_Baseline_Questionnaire_official_extracted.txt","2013":"CHARLS_2013_Questionnaire_extracted.txt"}
TARGET={"2011":{"db022s38":("38","functional difficulty helper option"),"db031s37":("37","anticipated future helper option"),"db023_38_":("","days per week a volunteer/facility helper provides assistance")},"2013":{"db022_w2_1_1_s64":("64","current helper for dressing/bathing item"),"db022_w2_1_2_s64":("64","current helper for item 2"),"db022_w2_1_3_s64":("64","current helper for item 3"),"db022_w2_5_1_s64":("64","current helper for shopping item"),"db022_w2_5_2_s64":("64","current helper for item 2"),"db022_w2_5_3_s64":("64","current helper for item 3"),"db022_w2_5_4_s64":("64","current helper for item 4"),"db022_w2_5_5_s64":("64","current helper for item 5"),"db022_w2_9_1_s64":("64","current helper for money-management item"),"db022_w2_9_2_s64":("64","current helper for item 2"),"db031s37":("37","anticipated future helper option")}}
def compact(x): return re.sub(r"[^a-z0-9]", "", x.lower())
def main():
 d=pd.read_csv(MAP,dtype=str,encoding="utf-8-sig").fillna(""); n=0
 for (w,c), (option,meaning) in [((w,c),v) for w,items in TARGET.items() for c,v in items.items()]:
  hit=d.wave.eq(w)&d.code.str.lower().eq(c);
  if hit.sum()!=1: raise SystemExit(f"Expected one crosswalk row {w}/{c}, found {hit.sum()}")
  qi=ROOT/"sources_official"/Q[w]; cb=ROOT/"sources_official"/f"CHARLS_{w}_Codebook_extracted.txt"
  qt=qi.read_text(encoding="utf8",errors="replace"); ct=cb.read_text(encoding="utf8",errors="replace")
  if "volunteer or employee" not in qt.lower(): raise SystemExit(f"Questionnaire helper option missing: {w}/{c}")
  normalized=compact(ct); normalized_code=compact(c)
  at=normalized.find(normalized_code)
  if at<0: raise SystemExit(f"Codebook field missing: {w}/{c}")
  local=normalized[max(0,at-90):at+220]
  if c!="db023_38_" and ("volunteer" not in local or compact(option) not in local): raise SystemExit(f"Affirmative option identity not located near Codebook field: {w}/{c}")
  semantic=("Continuous count; "+meaning+". Preserve conditional helper/item routing and wave-specific measurement; Codebook summaries are not analytic cutoffs." if c=="db023_38_" else f"The Codebook identifies option {option} as volunteer/facility help for this routed helper field. The public questionnaire describes a helper-selection item (multiple helpers may be selected). Participant-level unselected coding and the eligible denominator are unresolved; do not infer No from blank/missing and do not treat Codebook frequencies as respondent-level data.")
  if c=="db023_38_" and "db023 38" not in ct.lower() and "db023_38_" not in ct.lower(): raise SystemExit("Official Codebook helper-days field missing")
  status=("Codebook summary reports one observation; continuous count, no categorical labels; days measure and route retained" if c=="db023_38_" else ("official questionnaire identifies caregiver option; Codebook reports no observations; unselected coding and eligible denominator unresolved; no response-value labels assigned" if w=="2011" and c=="db022s38" else ("future-helper route and category reviewed; unselected coding and eligible denominator unresolved; no response-value labels assigned" if w=="2011" and c=="db031s37" else "official Codebook identifies affirmative caregiver-option code; unselected coding and eligible denominator unresolved; no response-value labels assigned")))
  d.loc[hit,"mapping_status"]=status; d.loc[hit,"value_label_status"]=status; d.loc[hit,"value_label_source"]=f"sources_official/{qi.name}; sources_official/{cb.name}"; d.loc[hit,"value_labels"]=""; d.loc[hit,"value_semantics"]=semantic
  caveat=d.loc[hit,"caveat"].iloc[0].strip(" ;")
  if semantic not in caveat: caveat+="; "+semantic
  d.loc[hit,"caveat"]=caveat; n+=1
 d.to_csv(MAP,index=False,encoding="utf-8-sig"); print(f"Reviewed {n} social-care fields; caregiver option absence remains unresolved; no categories or frequencies inferred.")
if __name__=="__main__": main()
