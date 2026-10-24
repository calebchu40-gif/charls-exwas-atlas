"""Audit the two routed Wave-3 child-level health/function phenotype candidates."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
RAW = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

LINKAGE = (
    "The official raw variable inventory lists ID, childID, and HHmemberID in both Child modules. "
    "This is a child-level phenotype candidate linked to the respondent, not a respondent phenotype. "
    "Validate childID uniqueness, respondent joins, and missing-link semantics in the authorized release. "
    "Children are clustered within respondents; any analysis must preserve the child-level estimand and "
    "account for within-respondent dependence. These outcomes are only observed on their routed ages."
)
SPECS = [
    {
        "code": "cb063_w3_1",
        "concept_id": "offspring_health_status_2015",
        "concept_label": "16岁以下子女自评健康（代理报告，2015）",
        "source_label": "Child's health status",
        "value_labels": "1=Very good; 2=Good; 3=Fair; 4=Poor; 5=Very poor",
        "caveat": "2015 questionnaire routes children younger than 16 to this item. Proxy-reported child health; preserve the five ordered categories and child-level outcome unit. " + LINKAGE,
    },
    {
        "code": "cb063_w3_6",
        "concept_id": "offspring_self_care_ability_2015",
        "concept_label": "60岁以上子女自理能力（2015）",
        "source_label": "Whether child can take care of him/herself",
        "value_labels": "1=Yes; 2=No",
        "caveat": "2015 questionnaire asks only children older than 60; this is a child-level functional outcome, not the CHARLS respondent's ADL/IADL phenotype. Preserve the age-gated denominator. " + LINKAGE,
    },
]
rows = []
for spec in SPECS:
    found = RAW[(RAW.wave == "2015") & RAW.module.str.lower().eq("child") & RAW.variable.str.lower().eq(spec["code"])]
    if found.empty:
        raise SystemExit(f"Missing official raw-catalog Child field: 2015/{spec['code']}")
    rec = found.iloc[0]
    rows.append({
        "wave": "2015", "code": spec["code"], "concept_id": spec["concept_id"],
        "concept_label": spec["concept_label"], "domain": "health and symptoms",
        "subcategory": "child health and functioning", "module": "Child",
        "source_label": spec["source_label"],
        "mapping_status": "official 2015 questionnaire/Codebook phenotype candidate; child-level linked record; routed denominator and clustered analysis required",
        "unit": "child-level outcome; ID + childID linked record",
        "value_labels": spec["value_labels"],
        "value_label_status": "official 2015 questionnaire/Codebook response categories reviewed; frequencies omitted",
        "value_label_source": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
        "construct": spec["concept_label"] + "; proxy/child response as specified by questionnaire; retain childID linkage.",
        "value_semantics": "child-level ordered/binary health and function status; not respondent phenotype; model child clustering within ID and use age-routed denominator",
        "caveat": spec["caveat"], "source_archive": f"{rec.source}; official questionnaire/Codebook",
    })

out = pd.DataFrame(rows)
out.to_csv(AUDIT / "child_phenotype_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"child-level phenotype mappings={len(out)}; concepts={out.concept_id.nunique()}; no participant values/frequencies used")
