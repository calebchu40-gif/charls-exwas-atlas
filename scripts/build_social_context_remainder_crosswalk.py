"""Map reviewed historical hukou relations and address-type context items."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
RAW = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

ROWS = [
    ("2011", "bc011", "last_hukou_location_relation_2011", "上一次户口登记地相对出生地关系（2011）", "Where Was Your Last Hukou",
     "1=Same as birthplace; 2=Another village/neighborhood in this county/city; 3=Another county/city in this province; 4=Another province",
     "Asked only on the retrospective hukou-history route (BC008=1 and BC009=1 or 3). Categories capture broad relation/distance; the city/county/province detail fields are excluded.", "social determinants", "historical hukou context"),
    ("2013", "bc011", "last_hukou_location_relation_2013", "上一次户口登记地相对出生地/常住地关系（2013）", "Where Was Your Last Hukou Location",
     "1=Birthplace; 2=Permanent address; 3=Another village/neighborhood in permanent-address county/city/district; 4=Other county/city/district",
     "Asked only when the retrospective-history route applies (BC008=1 and BC009=1 or 3). The 2013 reference categories differ from 2011; geographic text/detail child fields are not part of this concept.", "social determinants", "historical hukou context"),
    ("2011", "bc013", "first_hukou_location_relation_2011", "首次户口登记地关系（2011）", "What Was the Location of Your First Hukou",
     "1=Same as birthplace; 2=Same as current hukou; 3=This village/neighborhood; 4=Another village/neighborhood in this county/city; 5=Another county/city in this province; 6=Another province",
     "Retrospective first-hukou location relation; only asked on the BC009=1/3 route. Preserve the 2011 reference categories; exclude detailed geography fields.", "social determinants", "historical hukou context"),
    ("2013", "bc013", "first_hukou_location_relation_2013", "首次户口登记地关系（2013）", "What Was the Location of Your First Hukou",
     "1=Birthplace; 2=Same as current hukou; 3=Permanent address; 4=Another village/neighborhood in permanent-address county/city/district; 5=Other county/city/district",
     "Retrospective first-hukou location relation; only asked when BC009=1 or 3. The 2013 response categories differ from 2011; do not harmonize raw codes or include geographic text/detail child fields.", "social determinants", "historical hukou context"),
    ("2011", "bc014", "reason_current_hukou_location_differs_first_2011", "当前户口登记地与首次户口登记地不同的原因（2011）", "Why the Location of Current Hukou Is Different from Your First Hukou",
     "1=Marriage; 2=Go to school; 3=Employment; 4=Retirement/revolutionary retirement; 5=Sent down to countryside; 6=Migration; 7=Whole-village migration; 8=Escape of famine; 9=Other",
     "Asked only for specified combinations of retrospective first-hukou relation and current hukou location (BC009/BC013/BC005 route). Treat as conditional reason, not an all-person migration measure; open other text is excluded.", "social determinants", "historical hukou transitions"),
    ("2015", "bc001_w3_2", "prior_interview_hukou_type_2015_2018", "上一轮访谈时户口类别", "What's Your Hukou Type in Last Interview",
     "1=Agricultural hukou; 2=Non-agricultural hukou; 3=Unified residence hukou; 4=No hukou",
     "Asked only when the preloaded prior-wave hukou-type record was rejected in the returner route. It describes the previous interview, not current hukou type; structural skips are not a hukou category.", "social determinants", "historical hukou context"),
    ("2018", "bc001_w3_2", "prior_interview_hukou_type_2015_2018", "上一轮访谈时户口类别", "What Was Your Hukou Type in [ZIWTime]",
     "1=Agricultural hukou; 2=Non-agricultural hukou; 3=Unified residence hukou; 4=No hukou",
     "Asked on the reinterview route only when the preloaded previous-interview hukou type was rejected. This is a historical status, distinct from current hukou and from hukou-location relation.", "social determinants", "historical hukou context"),
    ("2018", "bb000_w3_1", "prior_wave_residential_address_type_2018", "上一轮访问时居住地址类型（2018回顾）", "Type of Residential Address at [ZIWTime]",
     "1=Family housing; 2=Nursing home; 3=Hospital; 4=Other",
     "Describes dwelling type at the prior interview's address (ZIWTime), not the 2018 current address. Preserve the 2018 historical time reference.", "housing and built environment", "residential setting"),
    ("2018", "bb000_w3_2", "prior_wave_residential_settlement_type_2018", "上一轮访问时居住地址城乡/聚落类别（2018回顾）", "Was Address BB000_W3 in the Village or City/Town",
     "1=City/town center; 2=Combination zone between urban and rural areas; 3=Village; 4=Special area",
     "Settlement context of the address at the prior interview's time point. Keep distinct from the current 2018 address BB001_W3 and from 2015/2018 new-interview current-settlement questions.", "social determinants", "historical residential settlement context"),
    ("2018", "bb001_w3_1", "current_residential_address_type", "当前居住地址类型", "Type of Current Residential Address",
     "1=Family housing; 2=Nursing home; 3=Hospital; 4=Other",
     "The 2018 questionnaire asks BB001-BB005 only on the new-interview route (XRType=2); returners skip this block. This is dwelling type, not exact address or neighborhood exposure.", "housing and built environment", "residential setting"),
    ("2020", "ba007", "current_residential_address_type", "当前居住地址类型", "Type of Residential Address",
     "1=Family housing; 2=Nursing home; 3=Hospital; 4=Other",
     "Asked for the named household roster member (XRName); preserve the person-level roster unit and link to respondent outcomes only for the intended person. It is not an exact-address exposure.", "housing and built environment", "residential setting"),
]

rows = []
for wave, code, concept, label, source_label, labels, caveat, domain, _subcategory in ROWS:
    found = RAW[(RAW.wave == wave) & RAW.variable.str.lower().eq(code.lower())]
    if found.empty:
        raise SystemExit(f"Missing official source field: {wave}/{code}")
    rec = found.iloc[0]
    if wave == "2011":
        questionnaire = "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"
    else:
        questionnaire = f"sources_official/CHARLS_{wave}_Questionnaire" + ("_English" if wave == "2020" else "") + "_extracted.txt"
    codebook = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    rows.append({
        "wave": wave, "code": code, "concept_id": concept, "concept_label": label,
        "domain": domain, "subcategory": _subcategory, "module": rec.module, "source_label": source_label,
        "mapping_status": "candidate historical/social residential-context exposure; wave-specific item, response categories, and routing reviewed",
        "unit": "", "value_labels": labels,
        "value_label_status": "official questionnaire and codebook categories reviewed; frequency counts omitted",
        "value_label_source": f"{questionnaire}; {codebook}",
        "construct": f"{label}; wave-specific and conditional; preserve source time point and respondent/roster relation",
        "value_semantics": "categorical nominal response; preserve wave-specific categories and do not infer missing/skip as a substantive category",
        "caveat": caveat,
        "source_archive": f"{rec.source}; {questionnaire}; {codebook}",
    })

out = pd.DataFrame(rows)
if out.duplicated(["wave", "code"]).any():
    raise SystemExit("Duplicate wave/code in social-context remainder crosswalk")
out.to_csv(AUDIT / "social_context_remainder_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"social-context remainder mappings={len(out)}; concepts={out.concept_id.nunique()}")
