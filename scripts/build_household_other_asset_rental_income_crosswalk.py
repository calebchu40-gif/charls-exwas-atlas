"""Map the wave-specific other-household-asset rental income items."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

def source(wave: str, code: str) -> dict:
    hit = raw[(raw.wave.astype(str) == wave) & raw.variable.str.lower().eq(code.lower())]
    if len(hit) != 1:
        raise ValueError(f"Expected one catalog row for {wave} {code}; found {len(hit)}")
    r = hit.iloc[0]
    return {"wave": wave, "code": code.lower(), "module": r.module,
            "source_label": r.variable_label, "source_archive": r.source}

amount_rows = []
for wave in ("2011", "2013", "2015", "2018"):
    rec = source(wave, "ha064_1")
    rec.update({"concept_id": "household_other_asset_rental_income_amount",
                "concept_label": "家庭其他非住房/非土地资产租赁收入金额",
                "domain": "Household economic resources", "construct": "household-level income amount",
                "unit": "Yuan; retain wave-specific reference period and route",
                "mapping_status": "candidate; official wave questionnaire/Codebook item located; eligible route and denominator require validation in approved data",
                "caveat": "This amount is conditional on the wave-specific HA064/GE014 item. The 2018 questionnaire explicitly refers to income in the past year; the 2011/2013/2015 amount stems and 2020 GE014_1 stem do not explicitly state the same reference period. Preserve original wave and do not pool, annualize, or impute zero without a prespecified rule.",
                "source_document": ("sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt" if wave == "2011" else f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt")})
    amount_rows.append(rec)
rec = source("2020", "ge014_1")
rec.update({"concept_id": "household_other_asset_rental_income_amount_2020",
            "concept_label": "家庭其他非住房/非土地资产租赁收入金额（2020）",
            "domain": "Household economic resources", "construct": "household-level income amount",
            "unit": "Yuan; response amount in the conditional GE014 rental-income route",
            "mapping_status": "candidate; official 2020 questionnaire/Codebook item located; eligible route and denominator require validation in approved data",
            "caveat": "GE014_1 follows the household rental-income question about trees, fixed capital, durables or livestock, excluding housing and land. The amount stem does not explicitly state a reference period; preserve it as wave-specific and do not label annual or impute zero outside the route.",
            "source_document": "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt"})
amount_rows.append(rec)
amount = pd.DataFrame(amount_rows)
amount.to_csv(AUDIT / "household_other_asset_rental_income_amount_crosswalk_v1.csv", index=False, encoding="utf-8-sig")

status_rows = []
for wave, code in (("2018", "ha064"), ("2020", "ge014")):
    rec = source(wave, code)
    rec.update({"concept_id": "household_other_asset_rental_income_status_2018_2020",
                "concept_label": "家庭其他非住房/非土地资产租赁收入状态",
                "domain": "Household economic resources", "construct": "household-level rental-income status",
                "unit": "categorical; preserve wave-specific official response labels",
                "value_labels": "2018: 1=Yes; 2=No; 997=Don't know; 999=Refused. 2020: 1=Yes; 2=No; 997=Don't know; 999=Refused (Codebook); preserve source wording and validate released-data coding.",
                "mapping_status": "candidate; official questionnaire/Codebook item located; route and denominator require validation in approved data",
                "caveat": "Both items concern other household assets such as trees, fixed capital, durables or livestock, excluding housing and land. Preserve the distinct wave-specific time reference and labels; do not infer household-level non-rental from structural skips.",
                "source_document": f"sources_official/CHARLS_{wave}_Questionnaire" + ("_English" if wave == "2020" else "") + f"_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"})
    status_rows.append(rec)
status = pd.DataFrame(status_rows)
status.to_csv(AUDIT / "household_other_asset_rental_income_status_crosswalk_v1.csv", index=False, encoding="utf-8-sig")

# HA064 in 2011-2015 is a response/unit gate (1=Yuan, 2=Not applicable),
# whereas 2018/2020 HA064/GE014 is a categorical yes/no/unknown status item.
selector_rows = []
for wave in ("2011", "2013", "2015"):
    rec = source(wave, "ha064")
    rec.update({"concept_id": "household_other_asset_rental_income_unit_selector_2011_2015",
                "concept_label": "家庭其他资产租赁收入金额/适用性选择器（2011–2015）",
                "role": "c", "domain": "measurement metadata",
                "construct": "response-format and applicability metadata",
                "unit": "Codebook: 1=Yuan amount response; 2=Not applicable; verify released-data storage before interpreting",
                "mapping_status": "C-only measurement metadata candidate; official Codebook item located; do not use as an exposure without respondent-level validation",
                "caveat": "The older HA064 field is not the same response format as 2018/2020 yes/no status. Keep as a selector/applicability marker; do not label 1 as a binary rental-income status or infer No from skips.",
                "source_document": ("sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt" if wave == "2011" else f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt")})
    selector_rows.append(rec)
selector = pd.DataFrame(selector_rows)
selector.to_csv(AUDIT / "household_other_asset_rental_income_selector_metadata_v1.csv", index=False, encoding="utf-8-sig")

def domain_json(frame: pd.DataFrame) -> list[dict]:
    items = []
    for cid, group in frame.groupby("concept_id", sort=False):
        first = group.iloc[0]
        items.append({"concept_id": cid, "label": first.concept_label, "domain": first.domain,
                      "caveat": first.caveat,
                      "source_fields": [{"wave": r.wave, "code": r.code, "module": r.module,
                                         "source_label": r.source_label, "unit": r.unit,
                                         "source_document": r.source_document,
                                         "mapping_status": r.mapping_status,
                                         "value_labels": "" if pd.isna(r.get("value_labels", "")) else str(r.get("value_labels", ""))}
                                        for _, r in group.iterrows()]})
    return items

(ROOT / "site-prototype" / "dist" / "household_other_asset_rental_income_v1.json").write_text(
    json.dumps(domain_json(pd.concat([amount, status], ignore_index=True)), ensure_ascii=False, indent=2), encoding="utf-8")
print(f"other asset rental income: amount={len(amount)} rows/{amount.concept_id.nunique()} concepts; status={len(status)} rows; C selectors={len(selector)}")
