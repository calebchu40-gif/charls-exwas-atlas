from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit" / "blood_biomarker_crosswalk_v1.csv"
WEB = ROOT / "site-prototype" / "dist" / "blood_biomarkers_v1.json"

# Names and units follow the official 2011 Blood Data User Guide and 2015 Blood Data Release Note.
ANALYTES = [
    ("blood_wbc", "白细胞计数", "血常规", "qc1_vb002", "bl_wbc", "1000 cells/μL", "白细胞计数；与2015 bl_wbc对应。"),
    ("blood_hemoglobin", "血红蛋白", "血常规", "qc1_vb004", "bl_hgb", "g/dL", "血红蛋白浓度；与2015 bl_hgb对应。"),
    ("blood_hematocrit", "红细胞压积", "血常规", "qc1_vb005", "bl_hct", "%", "红细胞压积；与2015 bl_hct对应。"),
    ("blood_mcv", "平均红细胞体积", "血常规", "qc1_vb006", "bl_mcv", "fL", "MCV；与2015 bl_mcv对应。"),
    ("blood_platelets", "血小板计数", "血常规", "qc1_vb009", "bl_plt", "10^9/L", "血小板计数；与2015 bl_plt对应。"),
    ("blood_triglycerides", "甘油三酯", "血脂", "newtg", "bl_tg", "mg/dL", "2015发布说明标注高值截顶至500 mg/dL，并提供截顶标记。"),
    ("blood_creatinine", "肌酐", "肾功能", "newcrea", "bl_crea", "mg/dL", "肌酐；与2015 bl_crea对应。"),
    ("blood_bun", "血尿素氮", "肾功能", "newbun", "bl_bun", "mg/dL", "BUN；与2015 bl_bun对应。"),
    ("blood_hdl", "高密度脂蛋白胆固醇", "血脂", "newhdl", "bl_hdl", "mg/dL", "HDL-C；与2015 bl_hdl对应。"),
    ("blood_ldl", "低密度脂蛋白胆固醇", "血脂", "newldl", "bl_ldl", "mg/dL", "LDL-C；与2015 bl_ldl对应。"),
    ("blood_total_cholesterol", "总胆固醇", "血脂", "newcho", "bl_cho", "mg/dL", "总胆固醇；与2015 bl_cho对应。"),
    ("blood_glucose", "血糖", "糖代谢", "newglu", "bl_glu", "mg/dL", "血糖；须同时保留是否空腹字段，不应默认均为空腹采血。"),
    ("blood_uric_acid", "尿酸", "肾/代谢", "newua", "bl_ua", "mg/dL", "尿酸；与2015 bl_ua对应。"),
    ("blood_cystatin_c", "胱抑素C", "肾功能", "cystatinc", "bl_cysc", "mg/L", "2011指南说明为采血者中的年龄分层子样本检测；不可按全体血样参与者处理。"),
    ("blood_crp", "C反应蛋白", "炎症", "newcrp", "bl_crp", "mg/L", "CHARLS血检发布说明称CRP/高敏CRP；分析前需以对应波次实验室文档确认检测定义。"),
    ("blood_hba1c", "糖化血红蛋白", "糖代谢", "newhba1c", "bl_hbalc", "%", "糖化血红蛋白；与2015 bl_hbalc对应。"),
]

# Same unit/name across waves is not evidence of longitudinal assay equivalence.
# CHARLS changed blood collection/transport/assay procedures between 2011 and 2015.
CROSS_WAVE_NOTE = (
    "2011与2015虽有同名且同单位字段，但CHARLS 2015血检论文记录了采集、运输和检测流程改进，"
    "同单位不证明原始测量可直接纵向比较；未经字段级实验室校准验证，按波次分别分析。"
    "总胆固醇、HDL-C、hsCRP和HbA1c另有与HRS家族研究之间的跨实验室校准工作，"
    "这不等于CHARLS公开原始字段已自动完成2011/2015校正。"
)
ROLE_BOUNDARY = (
    "这是内部临床/生理生物标志物，不是外部环境化学暴露。为支持宽口径ExWAS目录，将官方文件确认的血液分析物列为可选E及P候选；E仅表示内部生物标志物候选，不是模型纳入批准。"
    "同波横断面配对只能解释为非方向性关联；正式模型须预先说明估计目标、时间顺序/生物学依据和血检子样本资格，使用波次专用血检权重，排除同概念自配对，并按波次分别分析，除非完成字段级校准。"
)

# 2011 Blood Users' Guide, printed p.7 (PDF p.12), Table 2. These are
# wave-specific assay metadata and must never be copied into 2015 rows.
# The guide calls the final column "Detection limits"; preserve that wording
# as a reported range rather than reinterpreting it as an analytical LOD.
ASSAY_METADATA_2011 = {
    "blood_crp": ("Immunoturbidimetric assay", "<1.3%", "<5.7%", "0.1–20 mg/L"),
    "blood_hba1c": ("Boronate affinity HPLC", "1.90%", "2.10%", "0–40%"),
    "blood_total_cholesterol": ("Enzymatic colorimetric test", "0.80%", "1.70%", "3–800 mg/dL"),
    "blood_hdl": ("Enzymatic colorimetric test", "1.00%", "1.30%", "3–120 mg/dL"),
    "blood_ldl": ("Enzymatic colorimetric test", "0.70%", "1.20%", "3–400 mg/dL"),
    "blood_triglycerides": ("Enzymatic colorimetric test", "1.50%", "1.80%", "4–1000 mg/dL"),
    "blood_bun": ("Enzymatic UV method with urease", "<4.4%", "<4.1%", "5–100 mg/dL"),
    "blood_creatinine": ("Rate-blanked and compensated Jaffe method", "<1.6%", "<2.1%", "0.1–25 mg/dL"),
    "blood_glucose": ("Enzymatic colorimetric test", "0.90%", "1.80%", "2–450 mg/dL"),
    "blood_uric_acid": ("UA Plus method", "1.10%", "1.90%", "up to 20 mg/dL"),
    "blood_cystatin_c": ("Particle-enhanced turbidimetric assay", "<5%", "<5%", "0.5–8 mg/L"),
}
ASSAY_SOURCE_2011 = "CHARLS 2011 Blood Data Users' Guide, printed p.7 (PDF p.12), Table 2"
ASSAY_SOURCE_2015 = "CHARLS Followup 2015 Blood Data Release Note (VersionID 20190620), Table 1; no analyte-specific assay method/CV/detection-range fields reported"
UNIT_SOURCE = {
    "blood_wbc": {"2011": "in thousands", "2015": "1000"},
    "blood_hemoglobin": {"2011": "g/dL", "2015": "g/dL"},
    "blood_hematocrit": {"2011": "%", "2015": "%"},
    "blood_mcv": {"2011": "not stated in CBC summary table", "2015": "fl"},
    "blood_platelets": {"2011": "10^9/L", "2015": "10^9/L"},
}

rows = []
for concept, label, domain, v11, v15, unit, note in ANALYTES:
    for wave, variable, module, source_status in [
        ("2011", v11, "Blood_Assays", "Official Blood source identity verified; field key is present in protected Blood-file header; target/weight applicability, valid-value limits, special codes, and any transformation remain under review"),
        ("2015", v15, "Blood_Data_2015_Independent_Release", "Official archive is present in protected local intake; metadata-only preflight completed; participant records were not reviewed"),
    ]:
        assay = ASSAY_METADATA_2011.get(concept) if wave == "2011" else None
        assay_status = (
            "2011 guide reports analyte-specific metadata"
            if assay else
            "2011 guide reports CBC collection at county laboratories but not analyte-specific method/CV/range"
            if wave == "2011" else
            "2015 release note reports variable definitions/units only; assay method/CV/range not reported there; do not inherit 2011 values"
        )
        unit_source = UNIT_SOURCE.get(concept, {}).get(wave, unit)
        rows.append({
            "concept_id": concept, "concept_label": label, "domain": domain, "wave": wave,
            "variable": variable, "module": module, "unit": unit, "value_semantics": note,
            "collection_scope": "静脉血实验室检测；波次参与及具体检测资格按血检文件/官方说明核对",
            "weight_field": "bloodweight" if wave == "2011" else "Blood_weight",
            "source_status": source_status,
            "source_unit_text": unit_source,
            "assay_method": assay[0] if assay else "",
            "within_assay_cv": assay[1] if assay else "",
            "between_assay_cv": assay[2] if assay else "",
            "guide_reported_detection_range": assay[3] if assay else "",
            "assay_metadata_status": assay_status,
            "assay_metadata_source": ASSAY_SOURCE_2011 if assay else ASSAY_SOURCE_2015 if wave == "2015" else "CHARLS 2011 Blood Data Users' Guide, printed p.13 (PDF p.19), CBC summary; analyzer method/CV/range not specified",
            "cross_wave_comparability": CROSS_WAVE_NOTE,
            "role_boundary": ROLE_BOUNDARY,
            "source_document": "CHARLS 2011 Blood Data Users' Guide; CHARLS Followup 2015 Blood Data Release Note (VersionID 20190620)",
        })

for wave, variable, label, desc, weight, status in [
    ("2011", "qc1_va003", "是否空腹", "采血是否空腹；用于解释血糖/甘油三酯等，不是疾病表型。", "bloodweight", "Official Blood source identity verified; field key is present in protected Blood-file header; 2011 fasting response codes remain undocumented in reviewed official sources."),
    ("2015", "bl_fasting", "是否空腹", "采血是否空腹；用于解释血糖/甘油三酯等，不是疾病表型。", "Blood_weight", "Official archive is present in protected local intake; metadata-only preflight completed; participant records were not reviewed"),
    ("2015", "bl_top_coding_tg", "甘油三酯截顶标记", "指示原始甘油三酯超过500 mg/dL后是否按500截顶；质量/处理标记，不是独立表型。", "Blood_weight", "Official archive is present in protected local intake; metadata-only preflight completed; participant records were not reviewed"),
]:
    rows.append({"concept_id": "blood_collection_metadata", "concept_label": label, "domain": "采血/质量标记", "wave": wave,
                 "variable": variable, "module": "Blood_Assays" if wave == "2011" else "Blood_Data_2015_Independent_Release", "unit": "—",
                 "value_semantics": desc, "collection_scope": "采血参与者元数据", "weight_field": weight,
                 "cross_wave_comparability": "按波次保留采血状态/处理标记；不可把空腹或截顶标记缺失解释为否。",
                 "role_boundary": "采样/处理元数据(C)，不作为暴露或表型进入关联配对。",
                 "source_unit_text": "—", "assay_method": "", "within_assay_cv": "", "between_assay_cv": "",
                 "guide_reported_detection_range": "", "assay_metadata_status": "采样/处理元数据；不适用",
                 "assay_metadata_source": "CHARLS wave-specific blood documentation",
                 "source_status": status, "source_document": "CHARLS 2011 Blood Data Users' Guide; CHARLS Followup 2015 Blood Data Release Note (VersionID 20190620)"})

for row in rows:
    if row["concept_id"] == "blood_cystatin_c" and row["wave"] == "2011":
        row["cross_wave_comparability"] += (
            " 2011指南称该项只测量全部70岁及以上血样参与者和70岁以下随机子样本；"
            "尚未核实bloodweight是否另行校正此检测子样本，不能假设其自动覆盖该抽样。"
        )

with OUT.open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)
WEB.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {len(rows)} rows: {OUT} and {WEB}")
