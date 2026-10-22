"""Link gated Parent long-table education records to existing father/mother concepts."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"audit"
RAW=pd.read_csv(AUDIT/"raw_variable_catalog_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
LABELS=("1=No formal education (illiterate); 2=Did not finish primary school; 3=Sishu/home school; 4=Elementary; 5=Middle; 6=High; 7=Vocational; 8=Two-/three-year college/associate degree; 9=Four-year college/bachelor's; 10=Master's; 11=Doctoral/PhD (where offered)")
GATE=("Parent-module rows must be linked to respondent ID and filtered by parentID. 2013 father=parentID 1, mother=2, and ca003 must equal 1 (biological parent). 2015 parentID 1=biological father and 2=biological mother. Keep father/mother separate; exclude in-laws, spouse's parents, step/adoptive/foster parents and other relatives. Long-table record counts are not respondent sample sizes; this source is a candidate only and requires route/missingness verification before analysis.")
SPECS=[
("2013","respondent_biological_fathers_education","Respondent's biological father's highest education","parentID=1 (Father), ca003=1 (Biological Parent)"),
("2013","respondent_biological_mothers_education","Respondent's biological mother's highest education","parentID=2 (Mother), ca003=1 (Biological Parent)"),
("2015","respondent_biological_fathers_education","Respondent's biological father's highest education","parentID=1 (Biological Father)"),
("2015","respondent_biological_mothers_education","Respondent's biological mother's highest education","parentID=2 (Biological Mother)"),
]
rows=[]
for wave,cid,source_label,gate in SPECS:
 found=RAW[(RAW.wave==wave)&RAW.module.str.lower().eq("parent")&RAW.variable.str.lower().eq("ca009")]
 if found.empty: raise SystemExit(f"Missing Parent module {wave}/ca009")
 rec=found.iloc[0]
 rows.append({"wave":wave,"code":"ca009","concept_id":cid,"concept_label":"父亲最高受教育程度" if "fathers" in cid else "母亲最高受教育程度","domain":"early-life and family socioeconomic context","module":"Parent","source_label":source_label,"mapping_status":"candidate early-life family-context exposure; parentID and biological-parent gate reviewed; parent long-table unit retained","unit":"parent record; respondent ID + parentID linkage required","value_labels":LABELS,"value_label_status":"official wave questionnaire and Codebook response categories reviewed; frequency counts omitted","value_label_source":f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt","construct":source_label+" in Parent module; relation filter: "+gate,"value_semantics":"categorical education attainment; retain wave-specific source code and do not combine parent rows","caveat":GATE+" Do not double count this as an independent source if the matching fixed Family_Information parent-education field is also selected; choose one source or prespecify reconciliation.","source_archive":f"{rec.source}; official wave questionnaire/codebook"})
out=pd.DataFrame(rows)
if out.duplicated(["wave","code","concept_id"]).any(): raise SystemExit("Duplicate parent education mapping")
out.to_csv(AUDIT/"parent_roster_education_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
print(f"parent roster education mappings={len(out)}; concepts={out.concept_id.nunique()}")
