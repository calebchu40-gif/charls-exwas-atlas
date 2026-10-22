"""Map disease-specific screening and counselling outcomes from official CHARLS metadata.

This creates candidate, conditional phenotypes only. It reads the public raw
variable inventory, not respondent-level records or codebook frequencies.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
raw["key"] = raw.wave.astype(str) + "::" + raw.variable.str.lower()
lookup = {r.key: r for r in raw.itertuples(index=False)}

routes = ("These questions are conditional disease-management modules for respondents routed by the wave-specific hypertension/diabetes diagnosis or self-awareness items. Structural skips and unasked fields are not No; do not use the module as an unrestricted whole-cohort outcome. Preserve the disease-specific denominator and wave/interview type.")
sources = {
    "2011": "sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Codebook_extracted.txt; sources_official/CHARLS_2013_Questionnaire_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Codebook_extracted.txt; sources_official/CHARLS_2015_Questionnaire_extracted.txt",
    "2018": "sources_official/CHARLS_2018_Codebook_extracted.txt; sources_official/CHARLS_2018_Questionnaire_extracted.txt",
}
rows = []

def add(wave, code, cid, label, construct, subtype, value_labels="", unit="", caveat=""):
    rec = lookup.get(f"{wave}::{code.lower()}")
    assert rec is not None, (wave, code)
    rows.append({
        "wave": wave, "code": code, "concept_id": cid, "concept_label": label,
        "domain": "chronic disease management phenotype", "module": rec.module,
        "source_label": rec.variable_label, "construct": construct, "subtype": subtype,
        "unit": unit, "value_labels": value_labels,
        "value_label_status": "official wave codebook/questionnaire response semantics reviewed; frequencies excluded" if value_labels else "continuous count field; questionnaire unit reviewed; special missing/range checks remain",
        "value_label_source": sources[wave], "source_archive": rec.source,
        "mapping_status": "official wave field mapped; conditional candidate phenotype; not derived or analysis-frozen",
        "caveat": routes + (" " + caveat if caveat else ""),
    })

# Annual count of blood-pressure examinations, retained as a repeated-measure
# outcome within the hypertension management route.
for wave in ("2011", "2013", "2015", "2018"):
    add(wave, "da012", "hypertension_bp_exam_count", "高血压管理：过去12个月血压检查次数",
        "hypertension management", "annual number of blood-pressure examinations",
        unit="count in prior 12 months",
        caveat="Numeric count ranges and extreme values require wave-specific validation before modeling.")

# Ever/since-last-interview blood-pressure-check status.
for wave, code, subtype in [
    ("2013", "da011_w2_1", "ever checked"), ("2015", "da011_w2_1", "ever checked"),
    ("2018", "da011_w2_1", "ever checked"), ("2018", "da011_w4_1", "checked since prior interview"),
]:
    add(wave, code, "hypertension_bp_check_status", "高血压管理：血压检查经历",
        "hypertension management", subtype, "1=Yes; 2=No",
        caveat="The 2018 returner item refers to the interval since the prior interview; it is not the same recall period as the ever-checked item.")

# Community/village-doctor screening, frequency, cost and regularity.
bp_freq_2015 = "1=Once a week; 2=Twice a month; 3=Once a month; 4=Once every two months; 5=Once every season; 6=Once every half-year; 7=Once a year"
bp_freq_2018 = "1=Once a week; 2=Once half a month; 3=Once a month; 4=Once every two months; 5=Once every three months; 6=Once half a year; 7=Once a year"
community_bp = [
    ("2015", "da012_w3", "community/village doctor usually comes", "1=Yes; 2=No"),
    ("2015", "da012_w3_1", "community blood-pressure check frequency", bp_freq_2015),
    ("2015", "da012_w3_2", "payment for community blood-pressure check", "1=Yes; 2=No"),
    ("2018", "da012_w3_1", "community blood-pressure check frequency", bp_freq_2018),
    ("2018", "da012_w3_2", "payment for community blood-pressure check", "1=Yes; 2=No"),
    ("2018", "da012_w4", "regular blood-pressure check in prior year", "1=Yes; 2=No"),
]
for wave, code, subtype, labels in community_bp:
    add(wave, code, "hypertension_community_screening", "高血压管理：社区血压筛查服务",
        "hypertension management", subtype, labels,
        caveat="2015 and 2018 questions differ in wording and route; response labels remain wave-specific.")

# Provider health advice. In 2011/2013/2015 the split option fields store the
# selected option code; absence is not recoded as No. 2018 explicitly adds 0=No.
advice_items = {
    "hypertension": {
        "prefix": "da013", "label": "高血压管理：医护人员健康建议",
        "options": {1:"Weight control", 2:"Exercise", 3:"Diet", 4:"Smoking control", 5:"None of the above"},
        "waves": ("2011", "2013", "2015", "2018"),
    },
    "diabetes": {
        "prefix": "da016", "label": "糖尿病管理：医护人员健康建议",
        "options": {1:"Weight control", 2:"Exercise", 3:"Diet", 4:"Smoking control", 5:"Foot self-care", 6:"None of the above"},
        "waves": ("2011", "2013", "2015", "2018"),
    },
}
for disease, spec in advice_items.items():
    cid = f"{disease}_provider_health_advice"
    for wave in spec["waves"]:
        for idx, option in spec["options"].items():
            code = f"{spec['prefix']}_s{idx}" if wave == "2018" else f"{spec['prefix']}s{idx}"
            if f"{wave}::{code}" not in lookup:
                continue
            labels = (f"0=No; {idx}={option}" if wave == "2018" else f"{idx}={option}")
            add(wave, code, cid, spec["label"], f"{disease} management", f"provider advice option: {option}", labels,
                caveat="Older-wave split option fields store option-specific selections; do not interpret absent fields as No without confirming eligible denominator. The 2018 wave has explicit 0=No plus the option-specific code.")

# Diabetes examination counts by test; 2011 appends _a to the numeric fields.
tests = {
    1: ("blood_glucose_test_count", "糖尿病管理：血糖检测次数", "Blood glucose test"),
    2: ("urine_glucose_test_count", "糖尿病管理：尿糖检测次数", "Urine glucose test"),
    3: ("fundus_exam_count", "糖尿病管理：眼底检查次数", "Fundus examination"),
    4: ("microalbuminuria_test_count", "糖尿病管理：微量白蛋白尿检查次数", "Micro-albuminuria test"),
}
for wave in ("2011", "2013", "2015", "2018"):
    for idx, (cid, label, test_name) in tests.items():
        code = f"da015_{idx}_a" if wave == "2011" else f"da015_{idx}"
        if f"{wave}::{code}" not in lookup:
            continue
        add(wave, code, cid, label, "diabetes management", f"annual count: {test_name}",
            unit=f"number of {test_name.lower()} in prior 12 months",
            caveat="Numeric count ranges, valid zeros and wave-specific extreme values require review before modeling.")

# Community/village-doctor diabetes screening. 2015 asks whether community
# doctors usually come and test blood glucose; 2018 asks whether a regular
# diabetes examination occurred in the prior 12 months. Keep route and wording
# differences explicit even where the field components align.
diabetes_screening = [
    ("2015", "da016_w3", "diabetes_community_exam_status", "1=Yes; 2=No",
     "2015 asks whether community/village doctors usually come and perform a blood-glucose test; not identical to 2018 regular-examination wording."),
    ("2018", "da016_w4", "diabetes_community_exam_status", "1=Yes; 2=No",
     "2018 asks whether community/village doctors regularly performed a diabetes exam during the prior 12 months; preserve distinct wording from 2015."),
    ("2015", "da016_w3_1", "diabetes_community_exam_frequency", "1=Once a week; 2=Twice a month; 3=Once a month; 4=Once every two months; 5=Once every season; 6=Once a half-year; 7=Once a year",
     "Asked after a Yes to 2015 DA016_W3; 'once every season' wording is not relabeled as an exact three-month interval."),
    ("2018", "da016_w3_1", "diabetes_community_exam_frequency", "1=Once a week; 2=Once half a month; 3=Once a month; 4=Once every two months; 5=Once every three months; 6=Once half a year; 7=Once a year",
     "Asked after a Yes to 2018 DA016_W4; frequency category 5 differs from the 2015 wording."),
    ("2015", "da016_w3_2", "diabetes_community_exam_payment", "1=Yes; 2=No",
     "Whether the community/village blood-glucose examination required payment; asked only after the relevant screening route."),
    ("2018", "da016_w3_2", "diabetes_community_exam_payment", "1=Yes; 2=No",
     "Whether the community/village diabetes examination required payment; asked only after the relevant screening route."),
]
labels = {
    "diabetes_community_exam_status": "糖尿病管理：社区/村医检查经历",
    "diabetes_community_exam_frequency": "糖尿病管理：社区/村医检查频次",
    "diabetes_community_exam_payment": "糖尿病管理：社区/村医检查是否付费",
}
for wave, code, cid, value_labels, detail in diabetes_screening:
    add(wave, code, cid, labels[cid], "diabetes community screening", detail,
        value_labels=value_labels,
        caveat="Condition-specific diabetes-management outcome. Preserve prior diagnosis/self-awareness route; frequency and payment are asked only after a positive screening route. Never treat structurally unasked fields as No.")

# Diabetes test types selected in the previous 12 months. The codebook lists
# option-specific positive selections; absence of a checkbox value is not
# converted to a negative response. The explicit "None of the above" option
# remains its own selection.
diabetes_test_options = {
    1: "Blood glucose test", 2: "Urine glucose test", 3: "Fundus examination",
    4: "Micro-albuminuria test", 5: "None of the above",
}
for wave in ("2013", "2015"):
    for idx, option in diabetes_test_options.items():
        code = f"da015s{idx}"
        if f"{wave}::{code}" not in lookup:
            continue
        detail = ("Diabetes test option selected in the prior 12 months; positive option-code field; "
                  "nonselection is not inferred as No. The explicit none-of-the-above option is retained.")
        add(wave, code, "diabetes_test_type_past_year", "糖尿病管理：过去12个月检查项目选择",
            "diabetes annual testing", f"selected option: {option}",
            value_labels=f"{idx}={option} (selected option; nonselection code not inferred)",
            caveat=detail)

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
assert len(out) == 90, len(out)
assert out.concept_id.nunique() == 13
assert not out.duplicated(["wave", "code", "concept_id"]).any()
out.to_csv(AUDIT / "chronic_disease_management_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
summary = (out.groupby(["concept_id", "concept_label", "construct", "subtype"], dropna=False)
           .agg(waves=("wave", lambda x: ",".join(sorted(set(x)))), source_fields=("code", "size"),
                source_codes=("code", lambda x: ";".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "chronic_disease_management_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"management mappings={len(out)}; concepts={out.concept_id.nunique()}; fields with reviewed response labels={(out.value_labels!='').sum()}")
