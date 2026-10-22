"""Map household agricultural production, stock values, and activity net income."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

SPECS = {
    "household_crop_forestry_production_value": (
        "Household past-year crop and forestry production value",
        "Total value of crops and forestry products produced in the past year; Yuan.",
        "2011 asks total production including sold and self-consumed products in GB005; 2013/2015/2018 use GB005_1. It is a production-value measure, not cash receipts or net farm income. Preserve the household financial-respondent route and wave-specific special values.",
        {"2011": ["gb005"], "2013": ["gb005_1"], "2015": ["gb005_1"], "2018": ["gb005_1"]},
    ),
    "household_crop_forestry_home_consumption_value": (
        "Household value of home-consumed crop and forestry products",
        "Value consumed by household; Yuan; asked in 2013/2015/2018.",
        "A subset of total crop/forestry production value in the corresponding questionnaire; do not add to the total production value. No 2011 counterpart was located in the questionnaire/codebook.",
        {"2013": ["gb005_2"], "2015": ["gb005_2"], "2018": ["gb005_2"]},
    ),
    "household_livestock_aquatic_current_stock_value": (
        "Current household livestock and aquatic-life value",
        "Current household stock value; Yuan.",
        "Current value of livestock/aquatic life held by the household. This is a point-in-time stock estimate, distinct from last year's stock, production, or sales/use flow.",
        {"2011": ["gb008"], "2013": ["gb008"], "2015": ["gb008"], "2018": ["gb008"]},
    ),
    "household_livestock_aquatic_prior_year_stock_value": (
        "Household livestock and aquatic-life value at the same time last year",
        "Prior-year point-in-time stock value; Yuan.",
        "Retrospective household stock estimate at the same time in the preceding year; do not subtract from current stock or interpret it as annual income/change without reconciling respondent recall and values.",
        {"2011": ["gb009"], "2013": ["gb009"], "2015": ["gb009"], "2018": ["gb009"]},
    ),
    "household_livestock_aquatic_purchase_expenditure": (
        "Past-year household expenditure on purchasing livestock and aquatic life",
        "Household expenditure in the past year; Yuan.",
        "Past-year purchase expenditure for new livestock and aquatic life, separately measured from current/prior stock values and the value sold or consumed. It is an agricultural input/purchase flow, not livestock sales or net farm income.",
        {"2011": ["gb010"], "2013": ["gb010"], "2015": ["gb010"], "2018": ["gb010"]},
    ),
    "household_livestock_aquatic_sold_or_consumed_value": (
        "Past-year value of household livestock and aquatic life sold or consumed",
        "Past-year value; Yuan.",
        "This combines sold and household-consumed value, not sales revenue alone. The 2018 questionnaire explicitly excludes livestock byproducts; retain that scope caveat and do not add the separately asked byproduct value.",
        {"2011": ["gb011"], "2013": ["gb011_1"], "2015": ["gb011_1"], "2018": ["gb011_1"]},
    ),
    "household_livestock_byproduct_production_value": (
        "Past-year value of household livestock byproducts produced",
        "Past-year production value including self-consumption; Yuan.",
        "Includes products such as milk, wool/cashmere/skins, and eggs; value includes sold and self-consumed production. This is distinct from livestock/aquatic animals themselves and their stock or sold/consumed value.",
        {"2011": ["gb012"], "2013": ["gb012_1"], "2015": ["gb012_1"], "2018": ["gb012_1"]},
    ),
    "household_self_employment_activity_net_income": (
        "Net income earned by household members from each self-employment activity",
        "Yuan per listed activity; past-year net income excluding fixed-capital costs.",
        "Asked separately for each listed activity. For joint activities with non-household members, the questionnaire requests only the net income earned by household members. Slot suffixes identify repeated activities, not independent standardized exposure types; do not sum slots or treat absent slots as zero without checking roster linkage and routing.",
        {"2011": ["gc005_1_", "gc005_2_", "gc005_3_"],
         "2013": ["gc005_1_", "gc005_2_", "gc005_3_", "gc005_4_"],
         "2015": ["gc005_1_", "gc005_2_", "gc005_3_"],
         "2018": ["gc005_1_", "gc005_2_", "gc005_3_", "gc005_4_"]},
    ),
}

rows = []
for cid, (label, unit, caveat, waves) in SPECS.items():
    for wave, codes in waves.items():
        for code in codes:
            hit = raw[(raw.wave == wave) & raw.variable.str.lower().eq(code)]
            if len(hit) != 1:
                raise ValueError(f"Expected one official catalog row for {wave} {code}; found {len(hit)}")
            r = hit.iloc[0]
            docs = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
            if wave == "2011":
                docs = "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; " + docs
            else:
                docs = f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; " + docs
            rows.append({
                "wave": wave, "code": code, "concept_id": cid, "concept_label": label,
                "domain": "Household agricultural production and economic resources",
                "module": r.module, "source_label": r.variable_label, "unit": unit,
                "mapping_status": "candidate; official questionnaire/Codebook item located; household route, special values, and eligible denominator require verification in approved data",
                "caveat": caveat + " Household-level measure; do not treat as individual income or combine with a different value period/construct.",
                "source_archive": r.source, "source_document": docs,
            })

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "household_agricultural_production_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
items = []
for cid, (label, unit, caveat, _) in SPECS.items():
    fs = out[out.concept_id.eq(cid)]
    items.append({"concept_id": cid, "label": label, "domain": "Household agricultural production and economic resources",
                  "caveat": caveat, "source_fields": [{"wave": r.wave, "code": r.code,
                  "module": r.module, "source_label": r.source_label, "unit": r.unit,
                  "source_document": r.source_document, "mapping_status": r.mapping_status}
                  for r in fs.itertuples(index=False)]})
(ROOT / "site-prototype" / "dist" / "household_agricultural_production_v1.json").write_text(
    json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"household agricultural-production mappings={len(out)}; concepts={out.concept_id.nunique()}")
