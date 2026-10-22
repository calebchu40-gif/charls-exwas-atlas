"""Map 2011 anticipated primary source of old-age support.

Metadata-only. Official response labels are recorded; no frequencies or
respondent-level data are used.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str,
                  encoding="utf-8-sig").fillna("")
rec = raw[(raw.wave == "2011") & raw.variable.str.lower().eq("fn080")]
if len(rec) != 1:
    raise SystemExit(f"expected exactly one 2011 fn080 metadata row; found {len(rec)}")
rec = next(rec.itertuples(index=False))
rows = [{
    "wave": "2011", "code": "fn080",
    "concept_id": "anticipated_primary_old_age_support_source",
    "concept_label": "预期主要养老依靠来源",
    "domain": "social protection and social support",
    "module": rec.module, "source_label": rec.variable_label,
    "source_item": "FN080",
    "construct": "Anticipated primary source of support in old age if unable to work",
    "unit": "categorical",
    "value_labels": "1=Children; 2=Savings; 3=Pension or retirement salary; 4=Commercial pension insurance; 5=Other",
    "value_semantics": "Single categorical response about anticipated main support source; not actual support received, pension enrollment, or current benefit receipt.",
    "mapping_status": "2011 questionnaire and CodeBook response labels reviewed; candidate mapping",
    "caveat": "Question asks what the respondent expects to mainly rely on in old age if unable to work. Interpret as subjective anticipated support, not realized support. Asked of all respondents; preserve original nominal categories.",
    "source_archive": rec.source,
    "official_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
}]
out = AUDIT / "old_age_support_expectation_crosswalk_v1.csv"
pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
print("anticipated old-age support mapping=1; new concepts=1")
