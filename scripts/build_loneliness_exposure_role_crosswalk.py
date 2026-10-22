"""Add an evidence-based exposure role for loneliness items already in the P catalog."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
source = pd.read_csv(ROOT / "audit/mood_item_variable_mapping_v1.csv", dtype=str).fillna("")
selected = source[source["concept_id"].isin({"mood_lonely", "affect_lonely_yesterday"})].copy()
symptoms = pd.read_csv(ROOT / "audit/health_symptom_variable_mapping_v1.csv", dtype=str).fillna("")
affect = symptoms[symptoms["concept_id"].eq("affect_lonely_yesterday")].copy()
if not affect.empty:
    affect["value_semantics"] = affect["value_labels"]
    selected = pd.concat([selected, affect], ignore_index=True, sort=False)
selected["domain"] = "Social relationships / mental health"
selected["caveat"] = (
    "Dual-role candidate: subjective loneliness may be studied as a social/mental-health exposure, "
    "while the same item is also a phenotype. Do not model an item against itself or another score "
    "that contains it; same-wave association does not establish temporal direction. CES-D loneliness "
    "and the 2013 yesterday-affect item use distinct wording/response scales; retain original wave codes."
)
selected["mapping_status"] = (
    "officially reviewed item-level response labels; dual E/P role candidate; preserve wave-specific scale"
)
selected["value_semantics"] = selected["value_labels"]
selected["source_archive"] = "CHARLS official questionnaire/codebook metadata"
selected = selected[[
    "concept_id", "concept_label", "domain", "wave", "code", "module", "source_label",
    "mapping_status", "value_semantics", "caveat", "value_labels", "value_label_source", "source_archive"
]]
out = ROOT / "audit/loneliness_exposure_role_mapping_v1.csv"
selected.to_csv(out, index=False, encoding="utf-8-sig")
print(f"loneliness dual-role exposure candidates={selected.concept_id.nunique()}; mappings={len(selected)}")
