"""Map household donations and compensation amounts by wave."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/"audit"
raw=pd.read_csv(AUDIT/"raw_variable_catalog_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
specs={
 "gd003_1":("household_societal_donation_value_2011_2015","Household value of societal donations (2011-2015)","Donations from society, including cash and in-kind food/clothing; reported Yuan value.","household donation value in past year; household-level; conditional on source selection; do not treat in-kind valuation as cash receipts."),
 "gd003_2":("household_land_seizure_compensation_2011_2015","Household land-seizure compensation (2011-2015)","Reported Yuan compensation for land seizure.","Household-level compensation amount under the parent past-year income-source question; preserve land-seizure route and do not combine with house-demolition compensation or land-sale proceeds."),
 "gd003_3":("household_house_demolition_compensation_2011_2015","Household compensation for house/apartment demolition (2011-2015)","Reported Yuan compensation for pulling down a household house or apartment.","Household-level compensation amount under the parent past-year income-source question; preserve the conditional source route and do not combine with land-seizure compensation or housing-sale proceeds."),
}
rows=[]
for code,(cid,label,unit,caveat) in specs.items():
 for wave in ["2011","2013","2015"]:
  hit=raw[(raw.wave==wave)&raw.variable.str.lower().eq(code)]
  if len(hit)!=1:raise ValueError(f"Expected one {wave} {code}, got {len(hit)}")
  r=hit.iloc[0]
  questionnaire=("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave=="2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt")
  rows.append({"wave":wave,"code":code,"concept_id":cid,"concept_label":label,"domain":"household transfers and compensation","module":r.module,"source_label":r.variable_label,"unit":unit,"construct":"conditional household-level transfer/compensation amount","mapping_status":"2011/2013/2015 candidate; official questionnaire and Codebook identify the amount field; source route and special values must be verified in authorized data","caveat":caveat+" Do not interpret skipped or structurally absent amounts as zero; no individual-level attribution.","source_archive":r.source,"source_document":f"sources_official/{questionnaire}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"})
out=pd.DataFrame(rows);out.to_csv(AUDIT/"household_transfer_compensation_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
items=[{"concept_id":r.concept_id,"label":r.concept_label,"domain":r.domain,"caveat":r.caveat,"source_fields":[{"wave":r.wave,"code":r.code,"module":r.module,"source_label":r.source_label,"unit":r.unit,"source_document":r.source_document,"mapping_status":r.mapping_status}]} for r in out.itertuples(index=False)]
(ROOT/"site-prototype"/"dist"/"household_transfer_compensation_v1.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"household transfer/compensation amount mappings={len(out)}; concepts={out.concept_id.nunique()}")
