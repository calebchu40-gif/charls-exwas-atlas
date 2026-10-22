"""Generate C-only mappings for 2011 hypothetical health anchoring vignettes."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/"audit"
raw=pd.read_csv(AUDIT/"raw_variable_catalog_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
domains={"de007":"pain","de008":"pain","de009":"pain","de010":"sleep","de011":"sleep","de012":"sleep","de013":"mobility","de014":"mobility","de015":"mobility","de016":"cognition","de017":"cognition","de018":"cognition"}
rows=[]
for code,domain in domains.items():
 hit=raw[(raw.wave=="2011")&raw.variable.str.lower().eq(code)]
 if len(hit)!=1:raise ValueError(f"Expected one 2011 {code}; found {len(hit)}")
 r=hit.iloc[0];cid=f"hypothetical_{domain}_health_anchoring_vignette_metadata"
 rows.append({"wave":"2011","code":code,"concept_id":cid,"concept_label":f"Hypothetical {domain} health vignette rating (2011)","domain":"measurement metadata","module":r.module,"source_label":r.variable_label,"value_labels":"1=None; 2=Mild; 3=Moderate; 4=Severe; 5=Extreme","value_semantics":"Rating of a hypothetical person with the same age/background; not the respondent's own health status.","mapping_status":"official 2011 questionnaire explicitly identifies a hypothetical vignette; C-only anchoring/response-scale metadata","caveat":"Exclude from E/P association matrix and personal health outcomes. The questionnaire randomly selects name gender within household and the vignette domain is administered as a hypothetical scenario.","source_document":"sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt","source_archive":r.source})
out=pd.DataFrame(rows);out.to_csv(AUDIT/"health_anchoring_vignette_metadata_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
print(f"health anchoring-vignette metadata fields={len(out)}; domains={out.concept_id.nunique()}")
