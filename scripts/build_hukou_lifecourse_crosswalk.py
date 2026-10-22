"""Build an auditable, wave-specific hukou history exposure crosswalk."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUT = AUDIT / "hukou_lifecourse_exposure_crosswalk_v1.csv"
RAW = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

concepts = {
    "hukou_first_current_same": ("首个与当前户口是否相同", "Historical hukou status"),
    "intermediate_hukou_existence": ("首个与当前户口之间是否有其他户口", "Historical hukou transitions"),
    "hukou_type_place_change": ("首个户口以来户口类型/地点变化", "Historical hukou transitions"),
    "first_hukou_type": ("首个户口类型", "Historical hukou status"),
    "hukou_last_location_reason": ("户口所在地异于出生地的原因", "Historical hukou transitions"),
    "nonagricultural_hukou_reason": ("非农业户口原因", "Historical hukou transitions"),
    "agricultural_hukou_reason": ("农业户口原因", "Historical hukou transitions"),
    "hukou_status_before_unification": ("统一居民户口改革前户口类型", "Historical hukou status before local unification reform"),
    "unified_residence_hukou_adoption_date": ("取得统一居民户口时间", "Reported year/month of unified-residence-hukou adoption"),
    "current_hukou_acquisition_date": ("取得当前户口时间", "Reported year/month of current hukou acquisition"),
    "time_away_from_hukou_locality": ("离开户口登记县市时长", "Reported duration away from current hukou county/city"),
    "historical_nonagricultural_hukou_interval": ("曾持非农业户口年份区间", "Reported calendar-year interval with non-agricultural hukou"),
    "historical_agricultural_hukou_interval": ("曾持农业户口年份区间", "Reported calendar-year interval with agricultural hukou"),
}

rows = []
def add(concept, code, label, labels, construct, route):
    for wave in ("2011", "2013"):
        archive = "household_and_community_questionnaire_data.rar" if wave == "2011" else "CHARLS2013_Dataset.zip"
        questionnaire = ("sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011"
                         else "sources_official/CHARLS_2013_Questionnaire_extracted.txt")
        codebook = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        wave_labels = labels[wave]
        wave_caveat = (
            "Retrospective, conditional categorical history; not a time-varying exposure or geocoded migration measure. "
            "Value codes are wave-specific; harmonize labels, never numeric codes. " + route[wave]
        )
        rows.append({
            "wave": wave, "code": code, "concept_id": concept,
            "concept_label": concepts[concept][0], "domain": "social determinants",
            "module": "demographic_background" if wave == "2011" else "Demographic_Background",
            "source_label": label[wave], "value_labels": wave_labels,
            "value_label_status": "official wave codebook response labels reviewed; frequency counts omitted",
            "value_label_source": f"{codebook}; {questionnaire}",
            "mapping_status": "wave-specific historical exposure candidate; official item, answer codes, and route reviewed",
            "construct": construct, "value_semantics": "categorical retrospective self-report; no numeric dose implied",
            "caveat": wave_caveat, "source_archive": f"{archive}; {questionnaire}; {codebook}",
            "questionnaire_source": questionnaire,
        })

yesno = {"2011": "1=Yes; 2=No", "2013": "1=Yes; 2=No"}
change = {"2011": "1=Both type and place changed; 2=Only type changed; 3=Only place changed",
          "2013": "1=Both type and place changed; 2=Only type changed; 3=Only place changed"}
first_type = {"2011": "1=Agricultural hukou; 2=Non-agricultural hukou",
              "2013": "1=Agricultural hukou; 2=Non-agricultural hukou"}
reason_location = {"2011": "1=Marriage; 2=School; 3=Employment; 4=Retirement/revolutionary retirement; 5=Escape of famine; 6=Sent down to countryside; 7=Whole-village migration; 8=Other",
                   "2013": "1=Marriage; 2=School; 3=Employment; 6=Sent down to countryside; 8=Migration with parents; 9=Other"}
reason_nonag = {"2011": "1=Sent down 1967-1977, did not return to city; 2=Student; 3=Marriage; 4=Employment; 5=Whole-village migration; 6=Escape of famine; 7=Other",
                "2013": "1=Sent down 1967-1977, did not return to city; 2=Student; 4=Employment; 5=Whole-village migration; 6=Escape of famine; 7=Other"}
reason_ag = {"2011": "1=Sent down 1967-1977 then returned to city; 2=Rural before college; 3=Marriage; 4=Employment; 5=Land acquired by government; 6=Whole-village migration; 7=Escape of famine; 8=Other",
             "2013": "1=Sent down 1967-1977 then returned to city; 2=Born in rural areas; 3=Marriage; 4=Employment; 5=Escape of famine; 6=Other"}
route1 = {"2011": "The 2011 baseline questionnaire routes BC007=Yes directly to BD001; downstream history items are conditional.",
          "2013": "The 2013 follow-up questionnaire routes returning interviewees (XRType=REIW) around these history items; consult interview type and item-level missingness before defining denominator."}
route2 = {"2011": "Asked within the retrospective history section; questionnaire skips depend on preceding hukou responses.",
          "2013": "The questionnaire routes returning interviewees (XRType=REIW) around this history section; consult interview type and item-level missingness before defining denominator."}
route_reason = {"2011": "Asked only on questionnaire branches meeting BC008/BC009/BC011 conditions; not asked universally.",
                "2013": "Asked only on questionnaire branches meeting BC008/BC009/BC011 conditions; returning interviewees may skip the section."}
route_type = {"2011": "Asked only when BC009 indicates a type change (codes 1 or 2).",
              "2013": "Asked only when BC009 indicates a type change (codes 1 or 2); returning interviewees may skip the history section."}
route_nonag = {"2011": "Asked conditionally when first/current hukou type and change history meet the BC001/BC009 route.",
               "2013": "Asked conditionally when first/current hukou type and change history meet the BC001/BC009 route; returning interviewees may skip the history section."}
route_ag = {"2011": "Asked conditionally when first/current hukou type and change history meet the BC001/BC009 route.",
            "2013": "Asked conditionally when first/current hukou type and change history meet the BC001/BC009 route; returning interviewees may skip the history section."}

add("hukou_first_current_same", "bc007", {"2011":"Is Your First Hukou Same as Your Current Hukou", "2013":"Is Your First Hukou Same as Your Current Hukou"}, yesno, "Whether first and current hukou are the same", route1)
add("intermediate_hukou_existence", "bc008", {"2011":"Any other Hukou between Your First and Current Hukou", "2013":"Were There Any Other Hukou Between Your First and Current Hukou"}, yesno, "Any intervening hukou between first and current hukou", route2)
add("hukou_type_place_change", "bc009", {"2011":"Has Your Hukou Type or Place Ever Changed since Your First", "2013":"Has Your Hukou Type or Place Ever Changed"}, change, "Self-reported type/place change since first hukou", route2)
add("first_hukou_type", "bc010", {"2011":"What Was Your First Hukou Status", "2013":"What Was Your First Hukou Status"}, first_type, "Agricultural versus non-agricultural first hukou", route_type)
add("hukou_last_location_reason", "bc012", {"2011":"Why the Location of Last Hukou is Different from Your Birth Place", "2013":"Why the Location of Last Hukou Different From Your Birth Hukou Location"}, reason_location, "Categorical reason last/ current hukou location differs from birthplace", route_reason)
add("nonagricultural_hukou_reason", "bc015", {"2011":"The Reason of Non-Agricultural Hukou", "2013":"The Reason Of the Non-Agricultural Hukou"}, reason_nonag, "Categorical reason for non-agricultural hukou", route_nonag)
add("agricultural_hukou_reason", "bc017", {"2011":"The Reason of Agricultural Hukou", "2013":"Why You Had Agricultural Hukou Before"}, reason_ag, "Categorical reason for agricultural hukou", route_ag)

# Additional lifecycle measures explicitly located in the correct 2011
# baseline-household and 2013 follow-up questionnaires. Keep each component
# at its source precision; do not derive elapsed years from incomplete dates.
extra_specs = [
    ("hukou_status_before_unification", "bc002", "1=Agricultural Hukou; 2=Non-agricultural Hukou; 3=No Hukou", "categorical status", "Only asked for respondents currently classified as Unified Residence Hukou (BC001=3); historical pre-reform status, not current status.", "categorical; retain labels and wave-specific codes"),
    ("unified_residence_hukou_adoption_date", "bc003_1", "", "calendar year", "Only asked when current status is Unified Residence Hukou (BC001=3); questionnaire range is wave-specific.", "date component; do not infer month or calculate age without checking special codes"),
    ("unified_residence_hukou_adoption_date", "bc003_2", "", "calendar month (0–12 range in questionnaire)", "Only asked when current status is Unified Residence Hukou (BC001=3); month-0 meaning is not assumed unless confirmed in released-data documentation.", "date component; preserve month 0 without recoding"),
    ("current_hukou_acquisition_date", "bc004_1", "", "calendar year", "Asked on agricultural/non-agricultural current-hukou branches; year must not precede reported birth year.", "date component; preserve raw response"),
    ("current_hukou_acquisition_date", "bc004_2", "", "calendar month (0–12; 0=not remembered per 2011 questionnaire)", "Asked on agricultural/non-agricultural current-hukou branches; 2011 interviewer note explicitly uses 0 when month is not remembered.", "date component; month 0 is not January"),
    ("time_away_from_hukou_locality", "bc006_1", "", "years", "Conditional: 2011 asks when (BC005=1 and BB001 in 3/4/5) or BC005=4/5; 2013 asks when (BC005=2 and BB001=3/4) or BC005=4. Reported years cannot exceed age.", "reported duration component; not universal; do not treat structural skips as zero"),
    ("time_away_from_hukou_locality", "bc006_2", "", "months (0–12 range)", "Same wave-specific conditional routes as the years component; retain range and do not combine to total months without released-data missing-code review.", "reported duration component; not universal; do not treat structural skips as zero"),
    ("historical_nonagricultural_hukou_interval", "bc016_1", "", "calendar year (interval start)", "Conditional on current hukou type and historical-change route; asked with BC016_2 as a reported interval. Questionnaire does not establish repeated spells or complete coverage of every status period.", "reported interval component; do not derive duration unless endpoints and completeness are validated"),
    ("historical_nonagricultural_hukou_interval", "bc016_2", "", "calendar year (interval end)", "Conditional on current hukou type and historical-change route; asked with BC016_1 as a reported interval. Questionnaire does not establish repeated spells or complete coverage of every status period.", "reported interval component; do not derive duration unless endpoints and completeness are validated"),
    ("historical_agricultural_hukou_interval", "bc018_1", "", "calendar year (interval start)", "Conditional on current hukou type and historical-change route; asked with BC018_2 as a reported interval. Questionnaire does not establish repeated spells or complete coverage of every status period.", "reported interval component; do not derive duration unless endpoints and completeness are validated"),
    ("historical_agricultural_hukou_interval", "bc018_2", "", "calendar year (interval end)", "Conditional on current hukou type and historical-change route; asked with BC018_1 as a reported interval. Questionnaire does not establish repeated spells or complete coverage of every status period.", "reported interval component; do not derive duration unless endpoints and completeness are validated"),
]
for concept, code, labels, unit, caveat, semantics in extra_specs:
    for wave in ("2011", "2013"):
        rec = RAW[(RAW.wave.astype(str) == wave) & RAW.variable.str.lower().eq(code)]
        if len(rec) != 1:
            raise SystemExit(f"Expected one source row for {wave}/{code}, found {len(rec)}")
        source = rec.iloc[0]
        questionnaire = ("sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011"
                         else "sources_official/CHARLS_2013_Questionnaire_extracted.txt")
        codebook = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        # Several lifecycle components are not present in both waves. The raw
        # archive catalog is authoritative for actual wave availability.
        if not any(x[0] == wave and x[1].lower() == code.lower() for x in RAW[["wave", "variable"]].itertuples(index=False, name=None)):
            continue
        rows.append({
            "wave": wave, "code": code, "concept_id": concept,
            "concept_label": concepts[concept][0], "domain": "hukou history and social position",
            "module": str(source.module), "source_label": str(source.variable_label) or code,
            "unit": unit, "value_labels": labels,
            "value_label_status": "official wave codebook response labels reviewed; frequencies omitted" if labels else "continuous/date range reviewed from official questionnaire; value labels not applicable",
            "value_label_source": f"{questionnaire}; {codebook}",
            "mapping_status": "candidate; official wave question and routing reviewed; analysis eligibility pending",
            "construct": concepts[concept][1], "value_semantics": semantics,
            "caveat": caveat,
            "source_archive": str(source.source), "questionnaire_source": questionnaire,
        })

df = pd.DataFrame(rows)
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
for r in df.itertuples(index=False):
    if not ((raw.wave == r.wave) & (raw.variable.str.lower() == r.code.lower())).any():
        raise SystemExit(f"No source catalog match for {r.wave} {r.code}")
if df.duplicated(["wave", "code"]).any():
    raise SystemExit("Duplicate wave-code mappings")
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"Wrote {len(df)} wave-field mappings for {df.concept_id.nunique()} concepts: {OUT}")
