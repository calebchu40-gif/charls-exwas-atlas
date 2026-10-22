"""Map verified household house-decoration/renovation expenses by wave."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"audit"
raw=pd.read_csv(AUDIT/"raw_variable_catalog_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
specs={
 "2011":("household_house_decoration_renovation_expense_2011_2013","Household expenditure on decorating or renovating houses (past year, 2011/2013)","sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"),
 "2013":("household_house_decoration_renovation_expense_2011_2013","Household expenditure on decorating or renovating houses (past year, 2011/2013)","sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt"),
}
rows=[]
for wave,(cid,label,doc) in specs.items():
 code="ha025"; hit=raw[(raw.wave==wave)&raw.variable.str.lower().eq(code)]
 if len(hit)!=1: raise ValueError(f"Expected exactly one {wave} {code} row, got {len(hit)}")
 r=hit.iloc[0]
 rows.append({"wave":wave,"code":code,"concept_id":cid,"concept_label":label,"domain":"household economic resources and housing investment","module":r.module,"source_label":r.variable_label,"unit":"nominal Yuan spent in the past year","construct":"household-level expenditure; past-year house decorating/renovating (furniture excluded)","mapping_status":"candidate; official questionnaire and Codebook identify field; verify response routing and special codes in authorized data","caveat":"Household-level reported expenditure, not individual income, house value, maintenance quality, or total housing investment. Do not combine with remodeling/rebuilding questions that explicitly exclude decoration. Keep nominal amounts wave-specific unless a price-adjustment protocol is prespecified. 2015 Codebook lists ha025 as No Observations, so 2015 is deliberately not mapped as observed.","source_archive":r.source,"source_document":doc})
out=pd.DataFrame(rows);out.to_csv(AUDIT/"household_renovation_expenditure_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
items=[{"concept_id":r.concept_id,"label":r.concept_label,"domain":r.domain,"caveat":r.caveat,"source_fields":[{"wave":r.wave,"code":r.code,"module":r.module,"source_label":r.source_label,"unit":r.unit,"source_document":r.source_document,"mapping_status":r.mapping_status}]} for r in out.itertuples(index=False)]
(ROOT/"site-prototype"/"dist"/"household_renovation_expenditure_v1.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"household renovation expenditure mappings={len(out)}; concepts={out.concept_id.nunique()}; 2015 excluded")
