"""Index official household sale-proceeds allocation option fields; preserve unresolved coding."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
options = {
    1: "Deposits in bank account", 2: "Everyday living expenses",
    3: "Buying new houses", 4: "Medical expenditure",
    5: "Other important expenses", 6: "Transfer to children",
    7: "Transfer to parents", 8: "Transfer to relatives",
    9: "Other / specify usage",
}
rows = []
for r in raw.itertuples(index=False):
    wave, code = str(r.wave), str(r.variable).lower()
    m = re.fullmatch(r"ha026_w2_5_(\d+)_s([1-9])", code)
    if wave not in {"2013", "2015"} or not m:
        continue
    property_slot, option = m.groups()
    option = int(option)
    questionnaire = f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt"
    codebook = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    rows.append({
        "wave": wave, "code": code, "concept_id": "house_sale_proceeds_allocation_category_2013_2015",
        "concept_label": "Use category for proceeds from sale of a household residential property (2013-2015)",
        "domain": "household economic resources and asset transactions",
        "module": str(r.module), "source_label": str(r.variable_label),
        "unit": "option-coded field; questionnaire asks corresponding percentage of sale proceeds, but this released field's percent storage is not established",
        "value_labels": f"1={options[option]}; source option index s{option} (response direction unverified)",
        "value_label_status": "questionnaire menu transcribed; codebook option-coded field identity located; DO NOT ANALYZE until option-slot and percent storage are reconciled",
        "value_label_source": f"{questionnaire}; {codebook}",
        "source_archive": str(r.source), "property_slot": property_slot, "option_index": f"s{option}",
        "mapping_status": "exploratory household-level candidate; conditionally asked after a property-sale route; DO NOT ANALYZE pending released-field coding and denominator review",
        "reference_period": "distribution of proceeds from sale of an individual household residential property",
        "caveat": "This is not general household income or routine expenditure. The questionnaire asks respondents to report percentages by use category, while the public variable catalog/codebook lists option-indexed fields by property slot and does not identify a corresponding percentage value field. Do not interpret a slot as a percentage, assume blank means not selected, or combine property slots. Preserve the property index and verify the approved release before analysis. The free-text other-use description is not included.",
    })
out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"]).sort_values(["wave", "property_slot", "option_index"])
out.to_csv(AUDIT / "household_sale_proceeds_allocation_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"sale-proceeds allocation mappings={len(out)}; waves={out.groupby('wave').size().to_dict()}; property slots={sorted(out.property_slot.unique()) if len(out) else []}")
