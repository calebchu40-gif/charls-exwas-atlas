"""Build metadata-only mappings for chronic-disease awareness/timing/treatment items."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
concepts = pd.read_csv(AUDIT / "chronic_disease_concept_crosswalk_v2.csv", dtype=str, encoding="utf-8-sig").fillna("")
legacy = {str(r["2011_2018.Question.Index"]): r for _, r in concepts.iterrows()}
wave20 = {str(r["2020.Question.Index"]): r for _, r in concepts.iterrows()}
DISEASE_ZH = {
    "hypertension": "高血压", "dyslipidemia": "血脂异常",
    "diabetes_high_blood_sugar": "糖尿病/高血糖", "cancer": "癌症/恶性肿瘤",
    "chronic_lung_disease": "慢性肺病", "liver_disease": "肝病",
    "heart_disease": "心脏病", "stroke": "中风", "kidney_disease": "肾病",
    "digestive_disease": "胃/消化系统疾病", "emotional_psychiatric": "情绪/神经/精神问题",
    "memory_related_disease": "记忆相关疾病", "arthritis_rheumatism": "关节炎/风湿病",
    "asthma": "哮喘", "parkinsons": "帕金森病",
}

def codebook_value_labels(path: Path) -> dict[str, str]:
    """Extract code-label pairs only; never carry codebook frequencies into the atlas."""
    text = path.read_text(encoding="utf-8")
    blocks: dict[str, list[str]] = {}
    current = ""
    for line in text.splitlines():
        header = re.match(r"^[•·]?\s*([a-z][a-z0-9_ ]*?)\s*:\s*.*$", line.strip(), re.I)
        if header:
            current = re.sub(r"\s+", "_", header.group(1).strip().lower())
            blocks[current] = []
        elif current:
            blocks[current].append(line.strip())
    labels = {}
    for source_code, lines in blocks.items():
        pairs = []
        for line in lines:
            clean = re.sub(r"\\n(?:Page\s+\d+\s*)?(?:\d+\s+)?CHARLS.*$", "", line, flags=re.I).strip()
            match = re.match(r"^(\d+)\s+(.+)$", clean)
            if not match:
                continue
            response_code, label = match.groups()
            # 2013/2015 codebooks often put frequency and percent on the same
            # line as the selected option. Strip that aggregate information.
            label = re.sub(r"\s+\d[\d,]*\s+\d+(?:\.\d+)?\s*$", "", label).strip()
            label = label.rstrip(" ,;")
            if label.lower() != "total" and label:
                pairs.append(f"{response_code}={label}")
        if pairs:
            labels[source_code] = "; ".join(pairs)
    return labels


official_wave_labels = {
    wave: codebook_value_labels(ROOT / "sources_official" / f"CHARLS_{wave}_Codebook_extracted.txt")
    for wave in ("2011", "2013", "2015", "2018")
}
official_2020_awareness_labels = codebook_value_labels(ROOT / "sources_official/CHARLS_2020_Codebook_extracted.txt")
rows = []
def add(rec, domain, construct, subtype, concept_id, label, caveat):
    value_labels = ""
    value_status = "official variable metadata mapped; item-level value labels/routing review pending"
    value_source = ""
    wave_code = str(rec.wave)
    field_code = str(rec.variable).lower()
    if construct == "disease awareness" and wave_code == "2011" and field_code.rstrip("_") in official_wave_labels[wave_code]:
        value_labels = official_wave_labels[wave_code][field_code.rstrip("_")].replace("Dont know", "Don't know")
        value_source = "sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt"
        value_status = "official 2011 Codebook response categories transcribed; frequencies omitted; self-awareness route retained; release coding and eligible denominator require validation"
    elif construct == "disease awareness" and wave_code == "2020" and field_code in official_2020_awareness_labels:
        value_labels = official_2020_awareness_labels[field_code]
        value_source = "sources_official/CHARLS_2020_Codebook_extracted.txt; sources_official/CHARLS_2020_Questionnaire_English_extracted.txt"
        value_status = "official 2020 Codebook response categories transcribed; frequencies omitted; self-awareness route retained; release coding and eligible denominator require validation"
    elif wave_code == "2020" and field_code.startswith("da002_"):
        value_labels = "1=Better; 2=Worse; 3=About the same; 99=Did not have this disease at the prior interview"
        value_source = "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt"
        value_status = "official 2020 questionnaire/Codebook response labels reviewed; prior-wave route retained; frequencies excluded"
    elif str(rec.wave) in {"2013", "2015", "2018"} and str(rec.variable).lower().startswith("zda008_"):
        value_labels = "1=Yes; 2=No; 3=Don't know" if str(rec.wave) == "2013" else "1=Yes"
        value_source = f"sources_official/CHARLS_{rec.wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{rec.wave}_Codebook_extracted.txt"
        value_status = "official codebook response labels; prior-wave self-awareness/preload route retained; frequencies excluded"
    elif str(rec.wave) in {"2013", "2015", "2018"} and str(rec.variable).lower().startswith("da008_w2_1_"):
        value_labels = "1=Exam after disease attack; 2=Exam after illness; 3=Work-unit exam; 4=Community exam; 5=CHARLS physical exam; 6=Other"
        value_source = f"sources_official/CHARLS_{rec.wave}_Codebook_extracted.txt"
        value_status = "official response labels reviewed from wave-specific codebook; awareness-option labels; conditional disease route retained; frequencies excluded"
    if construct == "reported disease control" and wave_code in official_wave_labels and field_code in official_wave_labels[wave_code]:
        value_labels = official_wave_labels[wave_code][field_code]
        value_source = f"sources_official/CHARLS_{wave_code}_Codebook_extracted.txt; sources_official/CHARLS_{wave_code}_Questionnaire_extracted.txt"
        value_status = f"official {wave_code} Codebook response categories transcribed; frequencies omitted; disease-specific route retained; release coding and eligible denominator require validation"
    elif construct == "reported disease change since prior interview" and wave_code in official_wave_labels and field_code in official_wave_labels[wave_code]:
        value_labels = official_wave_labels[wave_code][field_code]
        value_source = f"sources_official/CHARLS_{wave_code}_Codebook_extracted.txt; sources_official/CHARLS_{wave_code}_Questionnaire_extracted.txt"
        value_status = f"official {wave_code} Codebook response categories transcribed; frequencies omitted; prior-interview recall route retained; release coding and eligible denominator require validation"
    if construct == "reported disease treatment" and wave_code in official_wave_labels and field_code in official_wave_labels[wave_code]:
        value_labels = official_wave_labels[wave_code][field_code]
        value_source = f"sources_official/CHARLS_{wave_code}_Codebook_extracted.txt; sources_official/CHARLS_{wave_code}_Questionnaire_extracted.txt"
        if wave_code == "2018":
            value_status = "official 2018 Codebook response categories transcribed; frequencies omitted; questionnaire route retained; respondent release coding and eligible denominator require validation"
        else:
            value_status = f"official {wave_code} Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE"
    rows.append({
        "wave": rec.wave, "code": rec.variable, "concept_id": concept_id,
        "concept_label": label, "domain": domain, "module": rec.module,
        "source_label": rec.variable_label, "mapping_status": "official variable metadata mapped; item-level value labels/routing review pending",
        "construct": construct, "subtype": subtype, "caveat": caveat,
        "value_labels": value_labels, "value_label_status": value_status,
        "value_label_source": value_source,
        "source_archive": rec.source,
    })

for rec in raw.itertuples(index=False):
    wave, code, label = str(rec.wave), str(rec.variable).lower(), str(rec.variable_label)
    if wave not in {"2011", "2013", "2015", "2018", "2020"} or "health_status" not in str(rec.module).lower():
        continue
    row = None
    # Reuse the disease concept's official item index; 2020 inserts Parkinson's at 13.
    if wave == "2020":
        m = re.match(r"(?:da004|da003)_(\d+)_", code)
        row = wave20.get(m.group(1)) if m else None
        if code.startswith("da002_"):
            # 2020 DA002 is a prior-wave comparison, not current disease
            # prevalence. Its index must follow the 2020 disease list (which
            # inserts Parkinson's) and stay in a distinct longitudinal concept.
            m = re.match(r"da002_(?:1_)?(\d+)_", code)
            row = wave20.get(m.group(1)) if m else None
    else:
        m = re.match(r"(?:da008|da009)_(?:[12]_)?(\d+)_", code)
        if code.startswith("da008_w2_1_"):
            m = re.match(r"da008_w2_1_(\d+)_", code)
        if code.startswith("zda008_") and wave in {"2013", "2015", "2018"}:
            m = re.fullmatch(r"zda008_(1|5|11)_", code)
        # DA009 has explicit year/age components in all waves; the disease index
        # is the final numeric component for DA009_1_i / DA009_2_i.
        if code.startswith("da009_"):
            m = re.match(r"da009_[12]_(\d+)_", code)
        if code.startswith("da010_w4_"):
            m = re.match(r"da010_w4_(\d+)__s", code)
        elif code.startswith("da010_w2_1_"):
            m = re.match(r"da010_w2_1_(\d+)_", code)
        elif code.startswith("da010_w2_2_"):
            m = re.match(r"da010_w2_2_(\d+)_", code)
        elif code.startswith("da010_") and not code.startswith("da010_w"):
            m = re.match(r"da010_(\d+)_s", code)
        row = legacy.get(m.group(1)) if m else None
    if row is None and wave != "2020":
        # Some treatment and control fields use a disease name or response slot
        # rather than the DA007 disease index in the variable name.
        disease_aliases = [
            (r"hypertension|blood pressure", "1"), (r"dyslipid", "2"),
            (r"diabetes|blood sugar|sugar", "3"), (r"cancer|malignant tumor", "4"),
            (r"chronic lung", "5"), (r"liver disease", "6"),
            (r"heart (?:problems|disease)", "7"), (r"stroke", "8"),
            (r"kidney", "9"), (r"digestive|stomach", "10"),
            (r"emotional|psychiatric|nervous", "11"), (r"memory", "12"),
            (r"arthritis|rheumatism", "13"), (r"asthma", "14"),
        ]
        for pattern, idx in disease_aliases:
            if re.search(pattern, label, re.I):
                row = legacy.get(idx)
                break
    if row is None:
        continue
    disease = str(row["Concept.ID"]).removesuffix("_diagnosis")
    disease_label = DISEASE_ZH.get(disease, disease)
    caveat = "Wave-specific source item; preserve route, special missing codes, and interview eligibility. This is not the physician-diagnosis indicator."

    if wave == "2011" and code.startswith("da008_") or wave in {"2013", "2015", "2018"} and (code.startswith("da008_") or code.startswith("zda008_")) or wave == "2020" and code.startswith("da004_"):
        prior_note = " This Z-prefixed field records prior-wave known-disease status/preload and is route-limited; missing values are not No." if code.startswith("zda008_") else ""
        awareness_note = " DA008_W2_1 records how the respondent knew about the indexed disease; it is not disease status. Disease index follows the wave-specific DA007 item index."
        add(rec, "chronic disease ancillary", "disease awareness", "prior-wave self-known disease" if prior_note else "self-known disease", f"self_awareness_{disease}", f"自知疾病状态：{disease_label}", caveat + " Awareness/self-knowledge is distinct from a doctor diagnosis; only diseases actually asked in that wave are represented." + awareness_note + prior_note)
        if code.startswith("da008_w2_1_"):
            rows[-1]["mapping_status"] = "official DA007 disease-index mapping and codebook response options reviewed; conditional route and eligibility remain to verify"
        if prior_note: rows[-1]["mapping_status"] = "official prior-wave self-awareness/preload field; categories and return-interview routing retained"
    elif code.startswith("da009_") and ("diagnos" in label.lower() or label.strip().lower() in {"year", "age"}):
        subtype = "year" if re.match(r"da009_1_\d+_", code) else "age" if re.match(r"da009_2_\d+_", code) else "time response; inspect questionnaire branch"
        if subtype in {"year", "age"}:
            subtype_label = "年份" if subtype == "year" else "年龄"
            add(rec, "chronic disease ancillary", "reported diagnosis/knowledge time", subtype, f"reported_{subtype}_first_known_{disease}", f"自报首次诊断/知悉{disease_label}的{subtype_label}", caveat + " Reported first diagnosis/knowledge time is not biological disease onset; year and age remain separate concepts.")

    if wave == "2020" and code.startswith("da002_"):
        prior_known = bool(re.match(r"da002_1_\d+_", code))
        concept = f"reported_interval_change_prior_known_{disease}" if prior_known else f"reported_interval_change_{disease}"
        label_prefix = "自报上次访问时已知病种的状况变化" if prior_known else "自报医生诊断病种的状况变化"
        add(rec, "chronic disease ancillary", "reported disease change since prior interview", "self-rated longitudinal change", concept, f"{label_prefix}：{disease_label}", caveat + " 2020 DA002 compares with the prior interview; it is not same-wave disease prevalence. Code 99 means the disease was not present at the prior interview and must not be recoded as improvement, worsening, or no disease.")

    # Treatment routes vary by wave, so map only fields whose own label explicitly
    # identifies treatment/medicine and whose disease index was recoverable above.
    # 2011 DB020 is an ADL/IADL functional-difficulty item (difficulty taking
    # medication because of health/memory problems), not a disease-treatment
    # response. Keep its functional mapping in the core crosswalk only.
    treatment_label = re.search(r"treatment|medicine|medication|taking treatments", label, re.I)
    none_option_2011 = wave == "2011" and code.startswith("da010_") and "none of the above" in label.lower()
    if not (wave == "2011" and code == "db020") and (treatment_label or none_option_2011):
        none_note = " This is the 2011 disease-specific 'none of the above' option (official Codebook option index 4); retain as a response-option field within the existing treatment concept, not as a separate outcome. The selected/unselected storage and eligible denominator remain unverified without permitted respondent-data checks; DO NOT ANALYZE until validated." if none_option_2011 else ""
        add(rec, "chronic disease ancillary", "reported disease treatment", "wave-specific treatment response", f"reported_treatment_{disease}", f"自报{disease_label}治疗方式", caveat + " Treatment items are disease-specific, multi-select in some waves, and route-limited; response options are not assumed harmonized." + none_note)
        if wave == "2018" and code in official_wave_labels[wave]:
            rows[-1]["mapping_status"] = "official 2018 Codebook response categories transcribed; questionnaire routing/time frame retained; release coding and routed denominator require validation"
        elif wave in {"2011", "2013", "2015"} and code in official_wave_labels[wave]:
            rows[-1]["mapping_status"] = f"official {wave} Codebook selected-option identity mapped; unselected response storage and routed denominator unverified; DO NOT ANALYZE"
        if none_option_2011:
            rows[-1]["mapping_status"] = "official 2011 Codebook item/option identity mapped; response storage and eligible denominator pending validation; DO NOT ANALYZE"

    if re.search(r"under control|generally control", label, re.I):
        disease_id = disease
        add(rec, "chronic disease ancillary", "reported disease control", "current control", f"reported_control_{disease_id}", f"自报{DISEASE_ZH[disease_id]}控制情况", caveat + " Asked only for specified conditions; not an objective biomarker or a diagnosis indicator.")
    elif not (wave == "2020" and code.startswith("da002_")) and re.search(r"compared to (?:z)?iwtime|compared with.*(?:last|previous)|compared to last", label, re.I):
        add(rec, "chronic disease ancillary", "reported disease change since prior interview", "self-rated interval change", f"reported_interval_change_{disease}", f"自报上次访谈以来{disease_label}变化", caveat + " Longitudinal recall item; do not interpret as same-wave disease status.")

# Explicit option fields whose labels omit the disease/treatment keyword but
# whose wave codebook places them within the hypertension/psychiatric modules.
lookup = {(str(r.wave), str(r.variable).lower()): r for r in raw.itertuples(index=False)}
def add_explicit(wave, code, concept, label, subtype, value_labels, note, source):
    rec = lookup.get((wave, code.lower()))
    if rec is None:
        return
    add(rec, "chronic disease ancillary", "reported disease treatment", subtype,
        concept, label, note)
    rows[-1]["value_labels"] = value_labels
    rows[-1]["value_label_status"] = "official wave codebook category verified; selected option only; frequencies excluded"
    rows[-1]["value_label_source"] = source
    rows[-1]["mapping_status"] = "official option field mapped to disease-specific treatment concept; route and nonselection storage remain explicit"
    if wave == "2011" and rows[-1]["construct"] == "reported disease treatment":
        rows[-1]["value_label_status"] = "official 2011 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE"
        rows[-1]["mapping_status"] = "official 2011 Codebook selected-option identity mapped; unselected response storage and routed denominator unverified; DO NOT ANALYZE"

add_explicit("2011", "da011s3", "reported_treatment_hypertension", "自报高血压治疗方式",
             "none-of-the-above treatment option", "3=None of the above (selected option; unselected storage code not inferred)",
             "2011 hypertension treatment list's explicit none-of-the-above option. Use with the other option fields; this is not a standalone population-level No without the eligible hypertension denominator.",
             "sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt")
add_explicit("2011", "da020s2", "reported_treatment_emotional_psychiatric", "自报情绪/精神问题治疗方式",
             "antidepressant medication option", "2=Taking antidepressants (selected option; unselected storage code not inferred)",
             "2011 emotional/psychiatric treatment option. Conditional on the mental-health disease route; codebook gives the selected-option category and does not establish a safe unselected-value code.",
             "sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt")

# 2011 additional diabetes/cancer/stroke treatment choices. The questionnaire
# lists yes/no probes, but the Codebook excerpt exposes option-index categories
# and frequencies rather than respondent-level yes/no storage. Make searchable
# links while explicitly blocking analysis until the authorized release confirms
# selected and unselected values and the routed denominator.
review_source_2011 = "sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"
review_route_2011 = {
    "da014": "Conditional on DA007=3 (diabetes/high blood sugar); current treatment.",
    "da018": "Conditional on DA007=4 (cancer/malignant tumor); treatment in the past two years.",
    "da019": "Conditional on DA007=8 (stroke); current treatment for stroke or its complications.",
}
review_choices_2011 = [
    ("da014s3", "reported_treatment_diabetes_high_blood_sugar", "自报糖尿病/高血糖治疗方式", "3=Taking insulin injections (Codebook option index; response storage unverified)"),
    ("da014s4", "reported_treatment_diabetes_high_blood_sugar", "自报糖尿病/高血糖治疗方式", "4=None of the above (Codebook option index; response storage unverified)"),
    ("da018s3", "reported_treatment_cancer", "自报癌症/恶性肿瘤治疗方式", "3=Chemotherapy (Codebook option index; response storage unverified)"),
    ("da018s4", "reported_treatment_cancer", "自报癌症/恶性肿瘤治疗方式", "4=Surgery (Codebook option index; response storage unverified)"),
    ("da018s5", "reported_treatment_cancer", "自报癌症/恶性肿瘤治疗方式", "5=Radiation therapy (Codebook option index; response storage unverified)"),
    ("da018s6", "reported_treatment_cancer", "自报癌症/恶性肿瘤治疗方式", "6=None of the above (Codebook option index; response storage unverified)"),
    ("da019s3", "reported_treatment_stroke", "自报中风治疗方式", "3=Physical therapy (Codebook option index; response storage unverified)"),
    ("da019s4", "reported_treatment_stroke", "自报中风治疗方式", "4=Acupuncture and moxibustion (Codebook option index; response storage unverified)"),
    ("da019s5", "reported_treatment_stroke", "自报中风治疗方式", "5=Occupational therapy (Codebook option index; response storage unverified)"),
    ("da019s6", "reported_treatment_stroke", "自报中风治疗方式", "6=None of the above (Codebook option index; response storage unverified)"),
]
for code, concept, label, option_label in review_choices_2011:
    family = code[:5]
    add_explicit("2011", code, concept, label,
                 "wave-specific treatment response; option index only",
                 option_label,
                 review_route_2011[family] + " The official questionnaire asks each option as Yes/No, but the Codebook lists this option index and aggregate frequencies. Do not interpret the option index as an answer, infer No from an unselected slot, or analyze until permitted respondent data/release documentation verifies storage and the routed denominator.",
                 review_source_2011)
    rows[-1]["value_label_status"] = "official 2011 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE"
    rows[-1]["mapping_status"] = "official 2011 questionnaire/codebook option identity mapped; respondent-level storage and routed denominator require authorized-data validation; DO NOT ANALYZE"

# Recurrent stroke and its most recent event timing are conditional longitudinal
# outcomes among return respondents with a prior stroke; do not merge with
# current-wave stroke prevalence or with first-diagnosis time.
stroke_routes = {
    "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
    "2018": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt",
}
for wave, source in stroke_routes.items():
    route = "Conditional reinterview module for respondents with prior stroke; DA019_W2_1 asks whether a doctor diagnosed another stroke since the previous interview. Do not merge with all-cohort stroke prevalence."
    add_explicit(wave, "da019_w2_1", "reported_recurrent_stroke_since_prior_interview", "自报上次访谈以来中风复发",
                 "doctor-diagnosed recurrent stroke", "1=Yes; 2=No", route, source)
    for code, concept, label, subtype, caveat in [
        ("da019_w2_2_1", "reported_most_recent_stroke_year", "自报最近一次中风年份", "year of most recent stroke",
         "Asked after a positive recurrent-stroke route; year is not first-ever diagnosis year."),
        ("da019_w2_2_2", "reported_most_recent_stroke_month" if wave == "2013" else "reported_most_recent_stroke_age",
         "自报最近一次中风月份" if wave == "2013" else "自报最近一次中风年龄",
         "month of most recent stroke" if wave == "2013" else "age at most recent stroke",
         "Wave-specific timing component; 2013 records month, while 2015/2018 record age. Do not harmonize these as the same measure."),
    ]:
        add_explicit(wave, code, concept, label, subtype, "", route + " " + caveat, source)
        rows[-1]["value_label_status"] = "continuous year/month/age component; verify release-specific special codes and eligible range"
        rows[-1]["value_label_source"] = source
        rows[-1]["mapping_status"] = "official questionnaire/codebook item mapped; conditional recurrence timing component, not first-diagnosis time"

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "chronic_disease_ancillary_variable_mapping_v1.csv", index=False, encoding="utf-8-sig")
summary = (out.groupby(["construct", "subtype", "concept_id", "concept_label"], dropna=False)
           .agg(waves=("wave", lambda x: ",".join(sorted(set(x)))), source_fields=("code", "size"), source_codes=("code", lambda x: ";".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "chronic_disease_ancillary_concept_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"ancillary mappings={len(out)}; concepts={out.concept_id.nunique()}; constructs={out.construct.nunique()}")
