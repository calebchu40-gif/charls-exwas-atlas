"""Map past-year household Dibao assistance amounts for 2011, 2013 and 2015."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
specs = [("2011", "gd001_c"), ("2013", "gd001"), ("2015", "gd001")]
rows = []
for wave, code in specs:
    hit = raw[(raw.wave == wave) & raw.variable.str.lower().eq(code)]
    if len(hit) != 1:
        raise ValueError(f"Expected exactly one {wave} {code} source row, found {len(hit)}")
    source = hit.iloc[0]
    questionnaire = {
        "2011": "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
        "2013": "CHARLS_2013_Questionnaire_extracted.txt",
        "2015": "CHARLS_2015_Questionnaire_extracted.txt",
    }[wave]
    rows.append({
        "wave": wave, "code": code,
        "concept_id": "household_dibao_assistance_amount_2011_2015",
        "concept_label": "过去一年家户低保补助金额（2011–2015）",
        "domain": "social protection and household material resources",
        "subcategory": "household social assistance and transfers",
        "module": source.module, "source_label": source.variable_label,
        "unit": "Yuan received by the household in the past year",
        "construct": "annual household Dibao assistance amount; not respondent-level income",
        "mapping_status": "official questionnaire and Codebook identify the amount field; wave-specific zero and eligibility routes retained",
        "value_labels": "",
        "value_label_status": "continuous amount; no categorical response labels",
        "value_label_source": f"sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        "caveat": (
            "2011 uses a separate GD001 yes/no receipt gate and GD001_C amount; analyze the amount only under the official route. "
            "2013/2015 GD001 asks the prior-year amount and the questionnaire instructs 0 Yuan when not applicable. "
            "Preserve wave-specific missingness, financial respondent and household linkage; do not assign household amounts to individuals. "
            "No Codebook frequencies or participant-level values are imported."
        ),
        "source_archive": source.source,
        "source_document": f"sources_official/{questionnaire}; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
    })

out = pd.DataFrame(rows)
out.to_csv(AUDIT / "household_dibao_amount_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"household Dibao amount mappings={len(out)}; concepts={out.concept_id.nunique()}")
