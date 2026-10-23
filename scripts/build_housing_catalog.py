"""Build a wave-specific housing code-to-indicator lookup for the prototype."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
mapping = pd.read_csv(ROOT / "audit/housing_exposure_variable_mapping_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
labels = pd.read_csv(ROOT / "audit/housing_value_label_review_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
owner_labels = pd.read_csv(ROOT / "audit/housing_current_owner_relation_labels_2018_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
food = pd.read_csv(ROOT / "audit/food_environment_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
cooking = pd.read_csv(ROOT / "audit/cooking_fuel_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
assets = pd.read_csv(ROOT / "audit/household_asset_exposure_mapping_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
raw = pd.read_csv(ROOT / "audit/raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
label_map = {(r.wave, r.code.lower()): (r.value_labels, r.value_label_status, r.value_label_source) for r in labels.itertuples(index=False)}
label_map.update({(r.wave, r.code.lower()): (r.value_labels, r.value_label_status, r.value_label_source) for r in owner_labels.itertuples(index=False)})
rows = []
for r in mapping.itertuples(index=False):
    source = raw[(raw.wave == r.wave) & (raw.variable.str.lower() == r.code.lower())]
    if source.empty:
        raise SystemExit(f"Unmatched source field: {r.wave} {r.code}")
    vlabels, status, ref = label_map.get((r.wave, r.code.lower()), ("", "not yet reviewed", ""))
    rows.append({
        "wave": r.wave, "code": r.code, "concept_id": r.concept_id,
        "concept_label": r.concept_label, "domain": r.domain, "module": r.module,
        "source_label": r.source_label, "value_labels": vlabels,
        "value_label_status": status, "value_label_source": ref,
        "mapping_status": r.mapping_status, "construct": r.construct, "caveat": r.caveat,
        "source_archive": r.source_archive,
    })
# Include the already-audited dwelling/environment fields that the broader
# housing crosswalk deliberately skipped to avoid duplicate E/P assignments.
housing_domains = {"Housing environment", "Housing environment/accessibility",
                   "Housing environment/basic services", "Indoor environment"}
for r in food[food.domain.isin(housing_domains)].itertuples(index=False):
    code = r.code.lower()
    vlabels, status, ref = label_map.get((r.wave, code), (r.code_value_labels, r.mapping_status, "audit/food_environment_crosswalk_v1.csv"))
    rows.append({
        "wave": r.wave, "code": r.code, "concept_id": r.concept_id,
        "concept_label": r.concept_label, "domain": r.domain, "module": r.module,
        "source_label": r.source_label, "value_labels": vlabels,
        "value_label_status": status or "not yet reviewed", "value_label_source": ref,
        "mapping_status": r.mapping_status, "construct": r.concept_label, "caveat": r.caveat,
        "source_archive": "audit/food_environment_crosswalk_v1.csv; official wave questionnaires/codebooks",
    })
# Fuel values are stored one category per row in their dedicated crosswalk.
for (wave, code), group in cooking.groupby(["wave", "raw_variable"]):
    source = raw[(raw.wave == wave) & (raw.variable.str.lower() == str(code).lower())]
    if source.empty:
        continue
    rec = source.iloc[0]
    fuel_labels = "; ".join(f"{x.raw_code}={x.codebook_label}" for x in group.itertuples(index=False) if x.raw_code and x.codebook_label)
    vlabels, status, ref = label_map.get((wave, str(code).lower()), (fuel_labels, "Official codebook response labels reviewed", "audit/cooking_fuel_crosswalk_v1.csv; official wave codebooks"))
    rows.append({
        "wave": wave, "code": code, "concept_id": "cooking_fuel_main",
        "concept_label": "家庭主要烹饪燃料", "domain": "housing and built environment",
        "module": rec.module, "source_label": rec.variable_label,
        "value_labels": vlabels, "value_label_status": status,
        "value_label_source": ref, "mapping_status": "official wave-specific cooking fuel crosswalk",
        "construct": "Nominal household cooking fuel category", "caveat": "Fuel codes are wave-specific nominal categories; do not treat numeric codes as an ordered dose.",
        "source_archive": "audit/cooking_fuel_crosswalk_v1.csv; official wave codebooks",
    })
# Household durables belong in the same searchable household assets index.
# Keep ownership responses and current-value fields separate, with their
# wave-specific coding and household-level interpretation attached.
for r in assets.itertuples(index=False):
    rows.append({
        "wave": r.wave, "code": r.code, "concept_id": r.concept_id,
        "concept_label": r.concept_label, "domain": r.domain, "module": r.module,
        "source_label": r.source_label, "value_labels": r.value_labels,
        "value_label_status": r.value_label_status,
        "value_label_source": r.value_label_source,
        "mapping_status": r.mapping_status, "construct": r.construct,
        "caveat": r.caveat, "source_archive": r.source_archive,
        "unit": r.unit,
    })
rows = list({(x["wave"], x["code"].lower(), x["concept_id"]): x for x in rows}.values())
out = ROOT / "site-prototype/dist/housing_catalog_v1.json"
out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"housing lookup rows={len(rows)}; official value labels={sum(bool(x['value_labels']) for x in rows)}")
