"""Audit selected child education fields; keep official-source conflicts C-only."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
RAW = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

SOURCE = {
    "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
}
LINKAGE = (
    "The raw inventory lists this code in the wave's Child module and lists ID, childID, and HHmemberID. "
    "Questionnaire/Codebook item menus use numbered family-information slots, with no official one-to-one "
    "crosswalk to the Child record field. Retain as a candidate and validate field identity, coding, "
    "respondent joins, and missing-link semantics in the authorized release. Child records are clustered "
    "within respondents; preserve the child-level estimand and account for that dependence. No participant "
    "values or Codebook frequencies are used."
)
WIDE_FAMILY_LINKAGE = (
    "The raw inventory lists this field in the wave's Family_Information module, not the Child module. "
    "The questionnaire asks the item for a named child in the numbered offspring roster, but the official "
    "materials reviewed here do not provide a direct release-field-to-childID crosswalk. Keep the child-level "
    "construct provisional; verify the slot/record linkage, respondent joins, coding, and missing-link semantics "
    "in the authorized release. If reshaped to child-level records, retain within-respondent clustering. "
    "No participant values or Codebook frequencies are used."
)

EXPOSURE_SPECS = [
    {
        "wave": "2013", "code": "cb060_w2_1", "module": "Family_Information",
        "concept_id": "offspring_home_school_years_2013",
        "concept_label": "子女私塾/家塾就读年数（2013）",
        "source_label": "How Many Years Did Child Spend in Home School",
        "value_labels": "", "unit": "child-level years of sishu/home schooling; numeric",
        "status": "official raw inventory Family_Information field; questionnaire/Codebook continuous-item candidate; child-slot linkage pending",
        "caveat": "Asked only after the highest-education item selects sishu/home school (CB060=3); the questionnaire routes past this item for other education categories. Verify special values and exact link to the named child in the authorized release; Codebook extrema are not validity thresholds.",
    },
    {
        "wave": "2013", "code": "cb058", "concept_id": "offspring_current_school_attendance_2013",
        "concept_label": "子女当前是否在校（2013）", "source_label": "Child is still in school",
        "value_labels": "1=Yes; 2=No", "unit": "child-level binary schooling context",
        "status": "official raw inventory field; questionnaire/Codebook item candidate; exact record-field crosswalk pending",
        "caveat": "The questionnaire skips children younger than 6; No routes past the current-grade question. Preserve age eligibility and skip patterns; skipped fields are not negative responses.",
    },
    {
        "wave": "2013", "code": "cb061", "concept_id": "offspring_primary_school_years_2013",
        "concept_label": "子女小学就读年数（2013）", "source_label": "How many years did child spend in primary school",
        "value_labels": "", "unit": "child-level years of primary schooling; numeric",
        "status": "official raw inventory field; questionnaire/Codebook continuous-item candidate; exact record-field crosswalk pending",
        "caveat": "Numeric follow-up in the age/schooling-history branch. Verify item eligibility, numeric storage, and special values in the authorized release; Codebook extrema are not validity thresholds.",
    },
    {
        "wave": "2013", "code": "cb062", "concept_id": "offspring_additional_schooling_years_2013",
        "concept_label": "子女最高教育层级后追加就读年数（2013）", "source_label": "How many additional years of schooling child received after the selected education level",
        "value_labels": "", "unit": "child-level additional schooling years; numeric",
        "status": "official raw inventory field; questionnaire/Codebook continuous-item candidate; exact record-field crosswalk pending",
        "caveat": "Numeric follow-up after the selected schooling category. Preserve the parent-item route; verify numeric storage and special values in the authorized release; Codebook extrema are not validity thresholds.",
    },
]

CONFLICT_SPECS = [
    {
        "wave": "2013", "code": "cb059", "concept_id": "child_schooling_grade_source_conflict_2013",
        "concept_label": "子女当前在校年级字段来源冲突（2013，仅元数据）",
        "source_label": "Level of schooling/grade",
        "caveat": "The questionnaire asks the current enrolled schooling level/grade. In the extracted Codebook slot labels, value 4 is assigned to both primary grade 3 and primary grade 4, leaving a coding conflict. Keep C-only with no response labels or E/P association until the official field-level code mapping is resolved.",
    },
    {
        "wave": "2015", "code": "cb052_w3_1", "concept_id": "child_literacy_or_education_source_conflict_2015",
        "concept_label": "子女识字/教育字段来源冲突（2015，仅元数据）",
        "source_label": "Whether child is literate (raw inventory label)",
        "caveat": "The official questionnaire asks whether the child is literate (Yes/No), while the extracted Codebook numbered-slot label describes highest education level and lists an 11-category attainment menu. Keep C-only with no response labels or E/P association until the official field-level code mapping is resolved.",
    },
]

def make_row(spec: dict, role: str) -> dict:
    wave, code = spec["wave"], spec["code"]
    module = spec.get("module", "Child")
    found = RAW[(RAW.wave == wave) & RAW.module.str.lower().eq(module.lower()) & RAW.variable.str.lower().eq(code)]
    if found.empty:
        raise SystemExit(f"Missing official raw-catalog Child field: {wave}/{code}")
    rec = found.iloc[0]
    linkage = WIDE_FAMILY_LINKAGE if module == "Family_Information" else LINKAGE
    return {
        "wave": wave, "code": code, "concept_id": spec["concept_id"],
        "concept_label": spec["concept_label"],
        "domain": "family and intergenerational context" if role == "e" else "measurement metadata",
        "subcategory": "child education and schooling context" if role == "e" else "child education questionnaire/Codebook source conflict",
        "module": module, "source_label": spec["source_label"],
        "mapping_status": spec["status"] if role == "e" else "C-only source identity/coding conflict; do not use as an E/P analytic field until adjudicated",
        "unit": spec.get("unit", "child record field; no analytic unit assigned while source conflict is unresolved"),
        "value_labels": spec.get("value_labels", ""),
        "value_label_status": (
            "official questionnaire/Codebook yes-no categories reviewed; frequencies omitted; direct Child-field alignment pending"
            if spec.get("value_labels") else "continuous numeric measure reviewed; special-value and direct field alignment validation pending"
        ) if role == "e" else "withheld because questionnaire and Codebook field meanings/codes conflict",
        "value_label_source": SOURCE[wave], "construct": spec["concept_label"],
        "value_semantics": "child-level schooling context; not the respondent's own education" if role == "e" else "unresolved source meaning; not an E/P candidate",
        "caveat": f"{spec['caveat']} {linkage}", "source_archive": f"{rec.source}; official questionnaire/Codebook context",
    }

exposures = pd.DataFrame([make_row(spec, "e") for spec in EXPOSURE_SPECS])
conflicts = pd.DataFrame([make_row(spec, "c") for spec in CONFLICT_SPECS])
for name, tab in (("child_education_context_crosswalk_v1.csv", exposures), ("child_education_source_conflict_crosswalk_v1.csv", conflicts)):
    if tab.duplicated(["wave", "code"]).any():
        raise SystemExit(f"Duplicate wave/code in {name}")
    tab.to_csv(AUDIT / name, index=False, encoding="utf-8-sig")
print(f"child schooling-context E candidates={len(exposures)}; unresolved C-only source conflicts={len(conflicts)}; frequencies excluded")
