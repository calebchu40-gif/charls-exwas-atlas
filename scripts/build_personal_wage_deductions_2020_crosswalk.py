"""Map the 2020 salary-deduction unit selector and numeric responses."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
doc = "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt (category labels only; frequency tables not used)"
common = "2020 asks about the total of insurance, income tax, public housing funds and other fees excluded from reported wage. Keep the response format selected in GA004 and its corresponding value field together. Do not calculate net wage or combine nominal yuan and percentage; validate route, special missing values and denominator in approved data."
specs = [
    ("ga004_1", "personal_wage_deduction_total_monthly", "个人工资扣款总额（月金额，2020）", "e", "Yuan per month", "Conditional numeric response when GA004 selects Yuan/Month.", ""),
    ("ga004_2", "personal_wage_deduction_total_annual", "个人工资扣款总额（年金额，2020）", "e", "Yuan per year", "Conditional numeric response when GA004 selects Yuan/Year.", ""),
    ("ga004_3", "personal_wage_deduction_total_percentage", "个人工资扣款总额（工资百分比，2020）", "e", "Percent of reported wage", "Conditional numeric response when GA004 selects Percentage of Wage. The denominator is the respondent's reported wage; preserve as a percentage, not a yuan amount.", ""),
    ("ga004", "personal_wage_deduction_response_unit_selector_2020", "个人工资扣款金额形式选择器（2020）", "c", "1=Yuan/Month; 2=Yuan/Year; 3=Percentage of Wage; 4=No", "Measurement-protocol metadata selecting the corresponding amount or no-deduction response; do not enter the association matrix as an exposure.", "C-only: unit/applicability selector, not an exposure"),
]
rows=[]
for code,cid,label,role,unit,note,status in specs:
    hit=raw[(raw.wave=="2020")&raw.variable.str.lower().str.strip().eq(code)]
    if len(hit)!=1: raise ValueError(f"Expected one 2020 raw catalog row for {code}; got {len(hit)}")
    src=hit.iloc[0]
    rows.append({"wave":"2020","code":code,"concept_id":cid,"concept_label":label,"role":role,
        "domain":"personal income and economic resources" if role=="e" else "measurement metadata",
        "module":src.module,"source_label":src.variable_label,"unit":unit,
        "construct":"respondent-level wage deduction response" if role=="e" else "response-unit and applicability selector",
        "value_labels":"1=Yuan/Month; 2=Yuan/Year; 3=Percentage of Wage; 4=No" if role=="c" else "",
        "mapping_status":status or "official 2020 questionnaire unit and numeric fields reviewed; special response values and denominator require validation in approved data",
        "caveat":common+" "+note,"source_archive":src.source,"source_document":doc})
out=pd.DataFrame(rows)
for role,name in [("e","personal_wage_deductions_2020_crosswalk_v1.csv"),("c","personal_wage_deduction_2020_selector_metadata_v1.csv")]:
    out[out.role==role].drop(columns="role").to_csv(AUDIT/name,index=False,encoding="utf-8-sig")
print(f"2020 personal wage-deduction mappings={sum(1 for x in specs if x[3]=='e')}; selectors={sum(1 for x in specs if x[3]=='c')}")
