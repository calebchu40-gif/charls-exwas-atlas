"""Add directly supported CHARLS healthcare value labels and measurement semantics.

Uses only public codebook/questionnaire text already distributed with this project.
It does not read respondent-level data.
"""
from pathlib import Path
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
csv_path = ROOT / "audit/healthcare_access_crosswalk_v1.csv"
json_path = ROOT / "site-prototype/dist/healthcare_access_v1.json"
df = pd.read_csv(csv_path, dtype=str).fillna("")

def enrich(row):
    w, code, cid = row.wave, row.code.lower(), row.concept_id
    labels = ""
    status = "连续值/字段结构；代码本未提供离散值标签" if cid in {
        "healthcare_cost_annual_premium", "healthcare_cost_outpatient_total", "healthcare_cost_outpatient_oop",
        "healthcare_cost_outpatient_medicine_oop", "healthcare_cost_inpatient_total",
        "healthcare_cost_inpatient_annual_oop", "healthcare_cost_inpatient_last_stay_total",
        "healthcare_cost_inpatient_annual_oop", "healthcare_cost_inpatient_last_stay_total",
                 "healthcare_cost_inpatient_last_stay_oop", "healthcare_cost_inpatient_medicine_oop",
        "healthcare_cost_inpatient_nonmedical", "healthcare_cost_outpatient_transport",
        "outpatient_visits_by_facility", "inpatient_count_past_year", "hospital_nights_last_stay"
    } else "逐字段值标签待核"
    semantics = row.value_semantics
    source = f"sources_official/CHARLS_{w}_Codebook_extracted.txt"
    mapping_status = row.mapping_status

    if cid == "health_insurance_type_status":
        if w == "2015":
            labels = "1=Yes; 2=No"
            status = "代码本逐值标签已核"
        elif w == "2018":
            match = re.search(r"_s(\d+)$", code)
            if match:
                labels = f"0=No; {match.group(1)}=Yes (plan category matches field suffix)"
                status = "代码本逐字段值标签已核"
        elif w == "2020":
            labels = "1=Urban employee medical insurance; 2=Urban/rural resident medical insurance; 3=Urban resident medical insurance; 4=New cooperative medical insurance; 5=Government medical insurance; 6=Other"
            status = "问卷类别标签已核；代码本按连续型摘要呈现，发布文件值标签需复核"
            source = "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt (BA017, p.11)"
            mapping_status = "Questionnaire categories verified; release-file value labels still require data-dictionary confirmation"
        elif w in {"2011", "2013"}:
            status = "字段标签已核；代码本呈现多选类别频数，未能从摘录确认未选/否的底层存储码"
            mapping_status = "Field label verified; underlying unselected storage code not confirmed"
            if "Codebook lists category-specific selected responses" not in semantics:
                semantics += " Codebook lists category-specific selected responses but does not establish a safe common numeric No code in this text extract; preserve raw selection fields and verify release formats before recoding."
    elif cid == "insurance_history_2015":
        labels = "1=Yes; 2=No"
        status = "代码本逐值标签已核"
    elif cid in {"outpatient_use", "inpatient_use_past_year"}:
        labels = "1=Yes; 2=No"
        status = "代码本逐值标签已核"
    elif cid == "outpatient_visits_by_facility":
        if "Continuous nonnegative visit count" not in semantics:
            semantics += " Continuous nonnegative visit count (number of visits in the questionnaire recall window); no discrete response categories. Codebook summaries include high values in some waves; inspect raw release special codes and distribution before analysis."
        status = "连续计数；参照期/機構槽位依波次；极值待核"
    elif cid == "inpatient_count_past_year":
        if "Continuous integer count of past-year inpatient episodes" not in semantics:
            semantics += " Continuous integer count of past-year inpatient episodes, asked conditionally after inpatient-care routing; not an ordinal response scale. Codebook maxima vary substantially by wave (including 2,011 in 2011 and 150 in 2018), so verify extreme values and release-specific special codes before analysis."
        status = "连续计数；条件提问；极值待核"
    elif cid == "hospital_nights_last_stay":
        if "Continuous integer count of nights at the most recent hospitalization" not in semantics:
            semantics += " Continuous integer count of nights at the most recent hospitalization, conditional on the hospitalization module; not annual total nights. Codebook summaries show a maximum of 365 in 2013/2018; check extreme values and special codes."
        status = "连续计数（夜数）；条件提问；极值待核"
    elif cid == "pandemic_delayed_care":
        labels = "1=Yes; 2=No"
        status = "2020代码本逐值标签已核；疫情期特异"
    elif cid.startswith("pandemic_"):
        match = re.search(r"_s(\d+)$", code)
        if match:
            labels = f"0=No; {match.group(1)}=Yes (selected response for this item)"
            status = "2020代码本逐字段多选标签已核；条件分母"
        mapping_status = "2020官方代码本/问卷已核；保留条件路由、单波限制和字段特异选择码"
        if cid == "pandemic_delayed_care_service_type":
            semantics = "2020 English Questionnaire DA010: select all service types delayed/not obtained because of COVID-19 impact; asked only after DA009=Yes. For each item, 0=No and the matching option number=Yes. Structural missingness is not No."
        elif cid == "pandemic_outpatient_visit_reason":
            semantics = "2020 English Questionnaire DA011: select-all outpatient-care reasons, asked only among those reporting delayed/not obtained outpatient service. For each item, 0=No and the matching option number=Yes; not a general service-delay reason."
        elif cid == "pandemic_delayed_care_reason":
            semantics = "2020 English Questionnaire DA012: select-all reasons for delay/not obtaining care, asked only after DA009=Yes. For each item, 0=No and the matching option number=Yes."

    if labels and w != "2020":
        mapping_status = "Official value labels transcribed; wave-specific wording/routing and harmonization still require review"
        if semantics.startswith("See source label;"):
            semantics = "Official codebook categories are listed in value_labels; question wording, routing and cross-wave comparability remain wave-specific."
    elif cid in {"outpatient_visits_by_facility", "inpatient_count_past_year", "hospital_nights_last_stay",
                 "healthcare_cost_annual_premium", "healthcare_cost_outpatient_total", "healthcare_cost_outpatient_oop",
                 "healthcare_cost_outpatient_medicine_oop", "healthcare_cost_inpatient_total",
                 "healthcare_cost_inpatient_annual_oop", "healthcare_cost_inpatient_last_stay_total",
        "healthcare_cost_inpatient_annual_oop", "healthcare_cost_inpatient_last_stay_total",
                 "healthcare_cost_inpatient_last_stay_oop", "healthcare_cost_inpatient_medicine_oop",
                 "healthcare_cost_inpatient_nonmedical", "healthcare_cost_outpatient_transport"}:
        mapping_status = "Official wave questionnaire item/route and Codebook label reviewed; release storage, special codes, denominator and analysis eligibility remain pending; not analysis-ready"

    return pd.Series({"mapping_status": mapping_status, "value_labels": labels, "value_label_status": status,
                      "value_label_source": source, "value_semantics": semantics})

extra = df.apply(enrich, axis=1)
for col in extra.columns:
    df[col] = extra[col]
df.to_csv(csv_path, index=False, encoding="utf-8-sig")

items = json.loads(json_path.read_text(encoding="utf-8"))
by_key = {(r.concept_id, r.wave, r.code): r for r in df.itertuples()}
for concept in items:
    for field in concept["source_fields"]:
        r = by_key[(concept["concept_id"], str(field["wave"]), field["code"])]
        field["value_labels"] = r.value_labels
        field["value_label_status"] = r.value_label_status
        field["value_label_source"] = r.value_label_source
        field["value_semantics"] = r.value_semantics
        field["note"] = r.mapping_status
json_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"healthcare mappings={len(df)} with explicit labels={sum(bool(x) for x in df.value_labels)}; continuous semantics={sum(x.startswith('连续') for x in df.value_label_status)}")
