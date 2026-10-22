"""Index the wave-specific response-format field for recurrence stroke timing.

This is C-role coding metadata, not a phenotype. Only public variable
inventory and official wave codebook/questionnaire labels are read.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
raw = pd.read_csv(ROOT / "audit/raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
rows = []
for wave in ("2013", "2015", "2018"):
    recs = raw[(raw.wave == wave) & raw.variable.str.lower().eq("da019_w2_2")]
    if recs.empty:
        continue
    rec = recs.iloc[0]
    rows.append({
        "wave": wave,
        "code": rec.variable,
        "concept_id": "stroke_recurrence_timing_unit_metadata",
        "concept_label": "中风复发时间回答单位（编码元数据）",
        "role": "c",
        "domain": "measurement / response-format metadata",
        "module": rec.module,
        "source_label": rec.variable_label,
        "value_labels": "1=Year; 2=Age",
        "mapping_status": "official codebook/questionnaire response-format field; coding metadata only",
        "value_semantics": "Selects how the respondent reported timing for DA019_W2_2_1/_2. It is not a stroke status or outcome and must not be tested as one.",
        "caveat": "Conditional on the prior-stroke return-interview route. 2013 DA019_W2_2_2 stores month; 2015/2018 DA019_W2_2_2 stores age, so preserve wave-specific component definitions.",
        "source_document": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        "source_archive": rec.source,
    })
out = pd.DataFrame(rows)
if len(out) != 3:
    raise SystemExit(f"Expected 3 response-format metadata rows; got {len(out)}")
out.to_csv(ROOT / "audit/stroke_timing_metadata_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"stroke timing metadata mappings={len(out)}; role=C only; no phenotype rows created")
