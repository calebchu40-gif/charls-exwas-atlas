"""Map conditional past-year household land-rental income by land type."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
LAND = {
    "1": ("cultivated_land", "耕地出租收入"),
    "2": ("forest_land", "林地出租收入"),
    "3": ("pasture_land", "牧场出租收入"),
    "4": ("pond_land", "水塘出租收入"),
}
rows = []
for wave in ("2011", "2013", "2015", "2018"):
    for slot, (key, label) in LAND.items():
        code = f"ha060_{slot}_"
        hit = raw[(raw.wave.astype(str) == wave) & raw.variable.str.lower().eq(code)]
        if len(hit) != 1:
            raise ValueError(f"Expected one source catalog row for {wave} {code}; found {len(hit)}")
        r = hit.iloc[0]
        doc = ("sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
               if wave == "2011" else f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt")
        if wave == "2018":
            concept_id = f"respondent_spouse_past_year_land_rental_income_{key}_2018"
            concept_label = f"主要受访者及配偶过去一年{label}"
            caveat = "The 2018 questionnaire explicitly limits this household-land rent amount to the main respondent and spouse, unlike the earlier household wording; keep separate and do not pool until respondent/household scope is reviewed. The item is conditional on the HA054 land-type loop and HA058=Yes. Structural skips, nonresponse and not-in-universe are not zero. Preserve the past-year period, nominal Yuan, source wave, and land-slot mapping; validate special codes before analysis."
        else:
            concept_id = f"household_past_year_land_rental_income_{key}"
            concept_label = f"家庭过去一年{label}"
            caveat = "Household land-rental amount in nominal Yuan over the past year. It is conditional on the land-type loop selected in HA054 and an affirmative HA058 rent-out response. Keep the four land types separate; structural skips, nonresponse and not-in-universe are not zero. Treat as household-level context, not respondent personal income. Preserve the exact wave and source code; check special values and land-slot mapping against the approved release dictionary before analysis."
        if wave == "2011" and slot == "1":
            caveat += " The 2011 Codebook reports a minimum of -200 Yuan for this field; meaning unresolved from summary statistics, so preserve raw values and do not interpret or recode negative values without authorized dictionary/data validation."
        rows.append({
            "wave": wave, "code": code, "concept_id": concept_id,
            "concept_label": concept_label, "domain": "household income and material resources",
            "module": r.module, "source_label": r.variable_label,
            "unit": ("Yuan for main respondent and spouse in past year" if wave == "2018" else "Yuan per household in past year"), "value_semantics": (f"conditional past-year respondent/spouse rental-income amount from {label}" if wave == "2018" else f"conditional past-year household rental-income amount from {label}"),
            "mapping_status": "official questionnaire/Codebook item identity matched; candidate concept; selected-land and HA058 routes remain conditional",
            "caveat": caveat, "source_archive": r.source, "source_document": doc,
        })

out = pd.DataFrame(rows)
out.to_csv(AUDIT / "land_rental_income_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
items = []
for cid, group in out.groupby("concept_id", sort=False):
    first = group.iloc[0]
    items.append({"concept_id": cid, "label": first.concept_label, "domain": first.domain,
                  "caveat": first.caveat,
                  "source_fields": [{"wave": r.wave, "code": r.code, "module": r.module,
                                     "source_label": r.source_label, "unit": r.unit,
                                     "source_document": r.source_document,
                                     "mapping_status": r.mapping_status} for _, r in group.iterrows()]})
(ROOT / "site-prototype" / "dist" / "land_rental_income_v1.json").write_text(
    json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"land-rental income mappings={len(out)}; concepts={out.concept_id.nunique()}; waves={sorted(out.wave.unique())}")
