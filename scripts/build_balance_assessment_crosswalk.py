"""Add the 2013 pre-balance health gate (P) and knee-height consent field (C).

Uses only CHARLS public questionnaire/codebook metadata; no respondent records.
"""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RAW=pd.read_csv(ROOT/"audit/raw_variable_catalog_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
SOURCE={}
for code in ("pd001","pk001"):
    x=RAW[(RAW.wave=="2013") & RAW.variable.str.lower().eq(code)]
    if len(x)!=1: raise ValueError(f"Expected one 2013 source field for {code}; got {len(x)}")
    SOURCE[code]=x.iloc[0]

pd_row={
 "concept_id":"balance_test_preventing_health_problems_2013",
 "concept_label":"Recent health conditions that may prevent balance testing (2013)",
 "domain":"physical function","wave":"2013","code":"pd001",
 "source_label":SOURCE["pd001"].variable_label,"module":SOURCE["pd001"].module,
 "source_archive":SOURCE["pd001"].source,
 "note":"Before balance testing, asks whether recent surgery, injury, or another health condition could prevent standing from a chair and balancing. This is a self-reported physical-function/measurement-eligibility candidate, not a diagnosed balance disorder or performance score. Preserve test route and missingness.",
 "mapping_status":"2013 single-wave candidate; official biomarker questionnaire and Codebook field identity, wording, route, and response categories reviewed",
 "value_labels":"1=Yes; 5=No",
 "value_label_status":"official codebook response labels reviewed; questionnaire wording clarifies the physical-function and measurement-gate construct",
 "value_label_source":"sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
}
health_csv=ROOT/"audit/health_symptom_variable_mapping_v1.csv"
health=pd.read_csv(health_csv,dtype=str,encoding="utf-8-sig").fillna("")
health=health[~(health.wave.eq("2013") & health.code.str.lower().eq("pd001"))]
health=pd.concat([health,pd.DataFrame([pd_row])],ignore_index=True)
health.to_csv(health_csv,index=False,encoding="utf-8-sig")

health_json=ROOT/"site-prototype/dist/health_symptoms_v1.json"
concepts=json.loads(health_json.read_text(encoding="utf-8"))
concepts=[c for c in concepts if c.get("concept_id")!=pd_row["concept_id"]]
concepts.append({"concept_id":pd_row["concept_id"],"label":"近期健康问题导致的平衡测试受限（2013）","domain":pd_row["domain"],
 "status":"单波P候选；平衡测试前健康适宜性/功能限制题，不是平衡障碍诊断或平衡测试分数。",
 "caveat":pd_row["note"],"source_fields":[{"wave":"2013","code":"pd001","source_label":pd_row["source_label"],"module":pd_row["module"],"value_labels":pd_row["value_labels"],"value_label_status":pd_row["value_label_status"],"value_label_source":pd_row["value_label_source"],"mapping_status":pd_row["mapping_status"]}]})
health_json.write_text(json.dumps(concepts,ensure_ascii=False,indent=2),encoding="utf-8")

gate={
 "concept_id":"knee_height_measurement_agreement_2013",
 "concept_label":"Knee-height measurement consent/instruction-comprehension gate (2013)",
 "domain":"measurement metadata","wave":"2013","code":"pk001",
 "module":SOURCE["pk001"].module,"source_label":SOURCE["pk001"].variable_label,
 "value_labels":"1=Yes; 5=No",
 "value_semantics":"Whether respondent understands the knee-height measurement instructions and agrees to take the measurement; the actual measurement is QK002.",
 "mapping_status":"C metadata only; official 2013 Biomarker Questionnaire identifies PK001 as instruction comprehension/consent, not knee-height value",
 "caveat":"Exclude from E/P association matrix. It describes eligibility/participation in the measurement protocol; actual knee height is recorded separately in QK002, where 993/999 are special attempt/refusal values.",
 "source_document":"sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
 "source_archive":SOURCE["pk001"].source,
}
pd.DataFrame([gate]).to_csv(ROOT/"audit/biomarker_measurement_gate_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
print("2013 balance-related assessment crosswalk: pd001=P, pk001=C; questionnaire/codebook only")
