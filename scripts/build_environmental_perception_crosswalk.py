"""Map the 2018 self-reported air-quality perception item from public metadata."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
catalog = pd.read_csv(ROOT / "audit/raw_variable_catalog_v1.csv", dtype=str).fillna("")
hit = catalog[(catalog.wave.astype(str) == "2018") & catalog.variable.str.lower().eq("dc046_w4")]
if hit.empty:
    raise ValueError("2018 dc046_w4 not found in the public variable catalog")
rows = []
for r in hit.drop_duplicates(["module", "variable", "variable_label"]).itertuples():
    rows.append({
        "concept_id": "self_reported_air_quality_satisfaction",
        "concept_label": "本人报告的空气质量满意度",
        "domain": "主观环境感知",
        "wave": "2018",
        "code": r.variable,
        "module": r.module,
        "source_label": r.variable_label,
        "value_labels": "1=Completely satisfied; 2=Very satisfied; 3=Somewhat satisfied; 4=Not very satisfied; 5=Not at all satisfied",
        "value_label_source": "sources_official/CHARLS_2018_Codebook_extracted.txt",
        "questionnaire_reference": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; DC046_W4",
        "mapping_status": "2018 questionnaire wording and codebook response categories verified; candidate perception exposure",
        "caveat": "单波个人主观感知，不能等同于环境监测的空气污染浓度；方向为满意度递减，分析时需保留原始有序类别并预先定义尺度。",
    })
out = pd.DataFrame(rows)
out.to_csv(ROOT / "audit/environmental_perception_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"environmental perception mappings={len(out)}; concepts={out.concept_id.nunique()}")
