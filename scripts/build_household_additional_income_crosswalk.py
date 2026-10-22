"""Map newly reviewed, wave-specific household income items from CHARLS 2020."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
specs = {
    "ge011": (
        "household_photovoltaic_generation_income_2020",
        "Household income from photovoltaic generation (2020)",
        "Household economic resources",
        "past-year Yuan amount; includes value used at home and electricity sold to the national grid",
        "The 2020 questionnaire explicitly defines the past-year measure as both household-use value and grid-sale revenue. This is a household-level, single-wave measure; do not interpret it as cash income only or combine with general business income.",
    ),
}
rows = []
for code, (cid, label, domain, unit, caveat) in specs.items():
    hit = raw[(raw.wave == "2020") & raw.variable.str.lower().eq(code)]
    if len(hit) != 1:
        raise ValueError(f"Expected one official catalog row for 2020 {code}; found {len(hit)}")
    r = hit.iloc[0]
    rows.append({
        "wave": "2020", "code": code, "concept_id": cid, "concept_label": label,
        "domain": domain, "module": r.module, "source_label": r.variable_label,
        "unit": unit, "construct": "household-level income item",
        "mapping_status": "candidate; official 2020 questionnaire/Codebook item located; route and denominator must be verified in approved data",
        "caveat": caveat, "source_archive": r.source,
        "source_document": "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt",
    })
out = pd.DataFrame(rows)
out.to_csv(AUDIT / "household_additional_income_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
items = [{"concept_id": r.concept_id, "label": r.concept_label, "domain": r.domain,
          "caveat": r.caveat, "source_fields": [{"wave": r.wave, "code": r.code,
          "module": r.module, "source_label": r.source_label, "unit": r.unit,
          "source_document": r.source_document, "mapping_status": r.mapping_status}]}
         for r in out.itertuples(index=False)]
(ROOT / "site-prototype" / "dist" / "household_additional_income_v1.json").write_text(
    json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"additional household income mappings={len(out)}; concepts={out.concept_id.nunique()}")
