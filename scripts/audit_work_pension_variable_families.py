"""Summarize work/pension field families from official variable metadata only."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
raw = pd.read_csv(ROOT / "audit/raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
raw = raw[raw.variable.str.lower().str.match(r"^(fn|fm|zf)")].copy()
raw["prefix"] = raw.variable.str.lower().str.extract(r"^(fn|fm|zf)", expand=False)

def classify(row: pd.Series) -> str:
    if row["prefix"] == "fn":
        return "pension enrollment/receipt/benefit components; one source family, not one concept per code"
    if row["prefix"] == "fm":
        return "retirement and position-exit history; route/status details remain wave-specific"
    if "work" in row.module.lower() or "retire" in row.module.lower() or "lastiw" in row.variable_label.lower() or "last interview" in row.variable_label.lower():
        return "prior-interview work/retirement preload; exclude from current-wave E/P screen pending longitudinal definition"
    return "non-work ZF-prefixed field; assess under its actual module separately"

raw["family_review"] = raw.apply(classify, axis=1)
catalog = pd.read_csv(ROOT / "audit/charls_atlas_candidate_fields_v0.csv", dtype=str, encoding="utf-8-sig").fillna("")
catalog_keys = set(catalog["Source.Wave"].astype(str) + "|" + catalog["Variable.Name"].str.lower())
rows = []
for (wave, module, prefix, review), group in raw.groupby(["wave", "module", "prefix", "family_review"], dropna=False):
    codes = sorted(set(group.variable.str.lower()))
    present = sum(f"{wave}|{code}" in catalog_keys for code in codes)
    action = ("include as pension E candidate" if prefix == "fn" else
              "include as retirement E candidate" if prefix == "fm" else
              "exclude prior-interview preload from current E/P" if "prior-interview" in review else
              "outside reviewed work family")
    rows.append({
        "wave": wave, "module": module, "field_prefix": prefix,
        "source_field_code_count": len(codes), "codes_present_in_EP_catalog": present,
        "catalog_action": action, "review_note": review,
        "example_codes": ";".join(codes[:8]),
    })
out = pd.DataFrame(rows).sort_values(["field_prefix", "wave", "module"])
out.to_csv(ROOT / "audit/work_pension_variable_family_review_v1.csv", index=False, encoding="utf-8-sig")
print(out.groupby(["field_prefix", "catalog_action"]).source_field_code_count.sum().to_string())
