"""Map reviewed parent-level marital and ethnicity context fields.

These are parent-roster records, not respondent-level fields. No respondent
aggregation is performed here; relationship filters remain explicit metadata.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
RAW = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str,
                  encoding="utf-8-sig").fillna("")

PARENT_GATE = (
    "Parent module is a long roster, not one row per respondent. Link by respondent ID and parentID. "
    "For 2013 also require ca003=1 (biological parent); for 2015 parentID=1 is respondent's biological "
    "father and parentID=2 is respondent's biological mother. Do not include spouse's parents, in-laws, "
    "step/adoptive parents or other relatives. Preserve question routing and structural missingness. "
    "These are discovery candidates only; any respondent-level analysis requires a prespecified relation-specific estimand."
)

MARITAL_LABELS_2013 = (
    "1=Married with my mother; 2=Married, but not with my mother; 3=Separated; "
    "4=Divorced; 5=Widowed; 6=Never married; 7=Cohabitated"
)
ETHNIC_STATUS_2015 = "1=Yes; 2=No"
ETHNIC_GROUPS_2015 = (
    "1=Hui; 2=Zhuang; 3=Uighur; 4=Man; 5=Yi; 6=Tibetan; 7=Miao; "
    "8=Mongol; 9=Dai; 10=Tujia; 11=Lahu; 12=Other"
)

SPECS = [
    {
        "wave": "2013", "code": "ca010",
        "concept_id": "respondent_biological_father_current_marital_status_2013",
        "concept_label": "受访者生父当前婚姻状态（2013）",
        "source_label": "Father Current Marital Status",
        "relation": "parentID=1 (Father); ca003=1 (Biological Parent)",
        "value_labels": MARITAL_LABELS_2013,
        "semantics": "Father's current marital status reported by respondent; common-law marriage is counted as married per questionnaire interviewer note.",
        "caveat": "Single-wave parent/family-context measure. The questionnaire asks about the father's current status, not the respondent's own marital history or a retrospective childhood exposure.",
    },
    {
        "wave": "2015", "code": "ca024_w3",
        "concept_id": "respondent_biological_father_ethnic_minority_status_2015",
        "concept_label": "受访者生父是否属于少数民族（2015）",
        "source_label": "R's Biological Father Belongs To Ethnic Minorities",
        "relation": "parentID=1 (Biological Father)",
        "value_labels": ETHNIC_STATUS_2015,
        "semantics": "Binary parent-record status; only respondent's biological father record.",
        "caveat": "Single-wave, parent-record-level family-background proxy. Keep unknown, refusals and structural skips distinct; no respondent-level aggregation is defined.",
    },
    {
        "wave": "2015", "code": "ca024_w3",
        "concept_id": "respondent_biological_mother_ethnic_minority_status_2015",
        "concept_label": "受访者生母是否属于少数民族（2015）",
        "source_label": "R's Biological Mother Belongs To Ethnic Minorities",
        "relation": "parentID=2 (Biological Mother)",
        "value_labels": ETHNIC_STATUS_2015,
        "semantics": "Binary parent-record status; only respondent's biological mother record.",
        "caveat": "Single-wave, parent-record-level family-background proxy. Keep unknown, refusals and structural skips distinct; no respondent-level aggregation is defined.",
    },
    {
        "wave": "2015", "code": "ca024_w3_1",
        "concept_id": "respondent_biological_father_ethnic_group_2015",
        "concept_label": "受访者生父少数民族类别（2015）",
        "source_label": "Which Ethnic Minority Does Parent Belong To",
        "relation": "parentID=1 (Biological Father); conditional on ca024_w3=1",
        "value_labels": ETHNIC_GROUPS_2015,
        "semantics": "Nominal minority-group category, asked only after parent minority-status Yes.",
        "caveat": "Conditional and potentially sparse nominal categories; never interpret codes as ordered or continuous. Low-frequency categories require analytic-cell and disclosure review before any model or public result.",
    },
    {
        "wave": "2015", "code": "ca024_w3_1",
        "concept_id": "respondent_biological_mother_ethnic_group_2015",
        "concept_label": "受访者生母少数民族类别（2015）",
        "source_label": "Which Ethnic Minority Does Parent Belong To",
        "relation": "parentID=2 (Biological Mother); conditional on ca024_w3=1",
        "value_labels": ETHNIC_GROUPS_2015,
        "semantics": "Nominal minority-group category, asked only after parent minority-status Yes.",
        "caveat": "Conditional and potentially sparse nominal categories; never interpret codes as ordered or continuous. Low-frequency categories require analytic-cell and disclosure review before any model or public result.",
    },
]

rows = []
for spec in SPECS:
    wave, code = spec["wave"], spec["code"]
    hit = RAW[(RAW.wave == wave) & RAW.module.str.lower().eq("parent") &
              RAW.variable.str.lower().eq(code.lower())]
    if len(hit) != 1:
        raise SystemExit(f"Expected one Parent source row for {wave}/{code}, found {len(hit)}")
    source = hit.iloc[0]
    questionnaire = (f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt"
                     if wave != "2020" else "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt")
    codebook = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    rows.append({
        "wave": wave,
        "code": code,
        "concept_id": spec["concept_id"],
        "concept_label": spec["concept_label"],
        "domain": "early-life and family socioeconomic context",
        "subcategory": "parent marital and ethnic context",
        "module": "Parent",
        "source_label": spec["source_label"],
        "mapping_status": "discovery candidate; official questionnaire and Codebook identity/categories reviewed; relation-filtered parent linkage required",
        "unit": "parent roster record; respondent ID + parentID linkage required",
        "value_labels": spec["value_labels"],
        "value_label_status": "official questionnaire and Codebook categories reviewed; frequency counts omitted",
        "value_label_source": f"{questionnaire}; {codebook}",
        "construct": f"{spec['semantics']} Relation filter: {spec['relation']}.",
        "value_semantics": "Categorical parent-record measure; retain relation, wave, route and source codes; do not aggregate across parents or mix with respondent-level fields.",
        "caveat": f"{spec['caveat']} {PARENT_GATE}",
        "source_archive": f"{source.source}; {questionnaire}; {codebook}",
    })

out = pd.DataFrame(rows)
if out.duplicated(["wave", "code", "concept_id"]).any():
    raise SystemExit("Duplicate parent context concept mapping")
out.to_csv(AUDIT / "parent_marital_ethnicity_crosswalk_v1.csv", index=False,
           encoding="utf-8-sig")
print(f"parent marital/ethnicity mappings={len(out)}; concepts={out.concept_id.nunique()}")
