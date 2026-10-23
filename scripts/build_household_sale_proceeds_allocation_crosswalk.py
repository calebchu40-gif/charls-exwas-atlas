"""Index CHARLS property-sale proceeds use selectors and distinct percent fields.

Only metadata is read. The candidate mappings remain locked from analysis until
release-level coding, routing, denominator, and property-slot checks are done.
"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
options = {
    "a": "Deposits in bank account", "b": "Everyday living expenses",
    "c": "Buying new houses", "d": "Medical expenditure",
    "e": "Other important expenses", "f": "Transfer to children",
    "g": "Transfer to parents", "h": "Transfer to relatives",
    "j": "Other specified usage",
}
rows = []
for r in raw.itertuples(index=False):
    wave, code = str(r.wave), str(r.variable).lower()
    if wave not in {"2013", "2015"}:
        continue
    selector = re.fullmatch(r"ha026_w2_5_(\d+)_s([1-9])", code)
    percent = re.fullmatch(r"ha026_w2_5([a-hj])_(\d+)_", code)
    if selector:
        property_slot, option_index = selector.groups()
        rows.append({
            "wave": wave, "code": code,
            "concept_id": "house_sale_proceeds_allocation_category_2013_2015",
            "concept_label": "Use category for proceeds from sale of a household residential property (2013-2015)",
            "domain": "household economic resources and asset transactions",
            "module": str(r.module), "source_label": str(r.variable_label),
            "unit": "option-indexed source field; not a percentage value",
            "value_labels": "",
            "value_label_status": "questionnaire defines the use-category menu; Codebook labels option-indexed source fields; selector response direction and link to separate percentage fields require release-level QA; DO NOT ANALYZE",
            "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
            "source_archive": str(r.source), "property_slot": property_slot,
            "option_index": f"s{option_index}",
            "mapping_status": "exploratory household-level metadata candidate; conditional property-sale route; DO NOT ANALYZE pending source identity, coding, and denominator review",
            "reference_period": "use category for proceeds from sale of an individual household residential property",
            "caveat": "This option-indexed field is not the percentage amount. Do not infer selection from blanks, pair slots by name alone, combine property slots, or interpret codebook summaries as participant-level analysis data. Confirm release identity, routing, and the corresponding percent field before analysis. Other-use text is excluded.",
        })
    elif percent:
        option, property_slot = percent.groups()
        rows.append({
            "wave": wave, "code": code,
            "concept_id": "house_sale_proceeds_allocation_percent_2013_2015",
            "concept_label": "Percentage of household property sale proceeds by use category (2013-2015)",
            "domain": "household economic resources and asset transactions",
            "module": str(r.module), "source_label": str(r.variable_label),
            "unit": "% of proceeds from sale of the indexed household residential property",
            "value_labels": "",
            "value_label_status": "numeric percentage field explicitly listed in official Codebook; category, property-slot linkage, release identity, valid range/special codes, and routed denominator require authorized-release QA; DO NOT ANALYZE",
            "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
            "source_archive": str(r.source), "property_slot": property_slot,
            "option_index": option,
            "mapping_status": "exploratory household-level numeric candidate; conditionally asked by property-sale route; distinct from general income; DO NOT ANALYZE pending authorized-release identity, coding, and denominator review",
            "reference_period": "allocation percentage for a use of proceeds from sale of an individual household residential property",
            "caveat": "Questionnaire and Codebook identify separate percentage fields by use category and property slot. Do not sum across properties, assume all category percentages form a complete 100% composition, or compare waves until release identity, category linkage, special codes, range, routing, and denominator are verified. Codebook summaries are not analysis results.",
        })

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"]).sort_values(["wave", "concept_id", "property_slot", "option_index"])
if out.empty or out[out.concept_id.eq("house_sale_proceeds_allocation_percent_2013_2015")].shape[0] != 54:
    raise SystemExit("Expected 54 official percentage fields across 2013 and 2015; inspect the raw metadata catalog")
out.to_csv(AUDIT / "household_sale_proceeds_allocation_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
counts = out.groupby(["concept_id", "wave"]).size().to_dict()
print(f"sale-proceeds mappings={len(out)}; concept-wave counts={counts}")
