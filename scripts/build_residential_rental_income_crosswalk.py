"""Map monthly housing-rental amounts and preserve applicability selectors."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"audit"
raw=pd.read_csv(AUDIT/"raw_variable_catalog_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
def source(wave,code):
 r=raw[(raw.wave==wave)&raw.variable.str.lower().eq(code.lower())]
 if len(r)!=1: raise ValueError(f"Expected unique source {wave}/{code}, got {len(r)}")
 return r.iloc[0]
rows=[]
def add(wave,code,cid,label,semantics,caveat,doc):
 r=source(wave,code)
 rows.append({"wave":wave,"code":code,"concept_id":cid,"concept_label":label,"domain":"housing and household economic resources","module":r.module,"source_label":r.variable_label,"unit":"Yuan/month","value_semantics":semantics,"mapping_status":"official questionnaire and Codebook item matched; candidate concept; preserve household ownership level and applicability route","caveat":caveat,"source_archive":r.source,"source_document":doc})
main="Household-level monthly rent from currently leased houses/rooms owned by the main respondent or spouse. HA052=1 opens amount response; 2=Not applicable. Do not infer zero from skips or nonresponse; do not annualize or interpret as personal rental income/current-home value."
other="Household-level monthly rent from currently leased houses/rooms owned by other household members. HA053=1 opens amount response; 2=Not applicable. Do not infer zero from skips or nonresponse; do not annualize or attribute it to the respondent/spouse."
for wave in ("2011","2013","2015"):
 doc=("sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt" if wave=="2011" else f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt")
 add(wave,"ha052_1","respondent_spouse_owned_house_monthly_rental_income","主要受访者/配偶所拥有房屋的月租收入","currently rented housing owned by respondent/spouse; household level",main,doc)
for wave in ("2011","2013"):
 doc=("sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt" if wave=="2011" else f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt")
 add(wave,"ha053_1","other_household_member_owned_house_monthly_rental_income","其他家户成员所拥有房屋的月租收入","currently rented housing owned by another household member; household level",other,doc)
out=pd.DataFrame(rows)
out.to_csv(AUDIT/"residential_rental_income_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
items=[]
for cid,g in out.groupby("concept_id",sort=False):
 r=g.iloc[0]
 items.append({"concept_id":cid,"label":r.concept_label,"domain":r.domain,"caveat":r.caveat,"source_fields":[{"wave":x.wave,"code":x.code,"module":x.module,"source_label":x.source_label,"unit":x.unit,"source_document":x.source_document,"mapping_status":x.mapping_status} for _,x in g.iterrows()]})
(ROOT/"site-prototype"/"dist"/"residential_rental_income_v1.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"residential rental amount mappings={len(out)}; concepts={out.concept_id.nunique()}; waves={sorted(out.wave.unique())}")
