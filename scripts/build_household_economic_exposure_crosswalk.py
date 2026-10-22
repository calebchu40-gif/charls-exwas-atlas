"""Map audited household expenditure components without treating them as total SES."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
ses = pd.read_csv(AUDIT / "household_ses_field_coverage_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
known = pd.read_csv(AUDIT / "food_environment_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
known_pairs = {(str(r.wave), str(r.code).lower()) for r in known.itertuples(index=False)}
raw_lookup = {(str(r.wave), str(r.variable).lower()): r for r in raw.itertuples(index=False)}

LABELS = [
    ("communication", r"communication", "household_monthly_communication_expenditure", "家庭月度通讯支出"),
    ("utilities", r"utilities", "household_monthly_utility_expenditure", "家庭月度水电等公用事业支出"),
    ("fuel", r"fuels?", "household_monthly_fuel_expenditure", "家庭月度燃料支出"),
    ("servants", r"servants?|matron|housekeepers?", "household_monthly_domestic_help_expenditure", "家庭月度家政/佣工支出"),
    ("local_transportation", r"local transportation|transportation", "household_monthly_local_transportation_expenditure", "家庭月度市内交通支出"),
    ("entertainment", r"entertainment", "household_monthly_entertainment_expenditure", "家庭月度娱乐支出"),
    ("heating", r"heating", "household_monthly_heating_expenditure", "家庭月度取暖支出"),
    ("clothing", r"clothing|bedding", "household_monthly_clothing_bedding_expenditure", "家庭月度衣物/床上用品支出"),
    ("travel", r"travel|travelling", "household_monthly_travel_expenditure", "家庭月度旅行支出"),
    ("durable_goods_electronics", r"durable goods.*electronics|electronics.*durable goods", "household_monthly_durable_goods_electronics_expenditure", "家庭月度耐用品/电子产品支出"),
    ("durable_goods", r"durable goods|furniture", "household_monthly_durable_goods_expenditure", "家庭月度家具/耐用品支出"),
    ("electronics", r"electronics", "household_monthly_electronics_expenditure", "家庭月度电子产品支出"),
    ("education", r"education|training", "household_monthly_education_expenditure", "家庭月度教育培训支出"),
    ("medical", r"medical", "household_monthly_medical_expenditure", "家庭月度医疗支出"),
    ("fitness", r"fitness", "household_monthly_fitness_expenditure", "家庭月度健身支出"),
    ("beauty", r"beauty", "household_monthly_beauty_expenditure", "家庭月度美容支出"),
    ("repair", r"maintenance|repair|purchase", "household_monthly_purchase_repair_expenditure", "家庭月度购买/维护/维修支出"),
    ("automobiles", r"automobiles?", "household_monthly_automobile_expenditure", "家庭月度汽车支出"),
    ("property_management", r"property management", "household_monthly_property_management_expenditure", "家庭月度物业管理费"),
    ("taxes_fees", r"taxes|fees", "household_monthly_taxes_fees_expenditure", "家庭月度税费支出"),
    ("donations", r"donations?", "household_monthly_donation_expenditure", "家庭月度捐赠支出"),
    ("rent", r"rent", "household_monthly_rent_expenditure", "家庭月度租金支出"),
    ("banquet", r"banquet|wedding", "household_monthly_banquet_wedding_expenditure", "家庭月度宴席/婚礼支出"),
    ("covid_prevention", r"covid.*prevention", "household_monthly_covid_prevention_expenditure", "COVID-19防护月度支出"),
]

def map_label(label: str):
    for _, pattern, concept, zh in LABELS:
        if re.search(pattern, label, re.I):
            return concept, zh
    return None

rows = []
for r in ses.itertuples(index=False):
    wave, code, label, role = str(r.wave), str(r.variable), str(r.label), str(r.candidate_role)
    if (wave, code.lower()) in known_pairs:
        continue
    concept = display = construct = None
    caveat = str(r.scope_note)
    if role == "monthly_component":
        m = map_label(label)
        if m:
            concept, display = m
            construct = "household monthly expenditure component"
    elif role == "monthly_total":
        concept = "household_monthly_total_expenditure_2018" if wave == "2018" else "household_monthly_total_expenditure_2020"
        display = f"{wave}家庭月度总支出"
        construct = "wave-specific monthly total household expenditure"
        caveat += " The 2020 measure is a pandemic-period survey; do not infer a 2018–2020 usual trend without reconciling item coverage and period effects."
    elif role == "weekly_component" and re.search(r"alcohol|tobacco|cigarette", label, re.I):
        concept, display = "household_weekly_alcohol_tobacco_expenditure", "家庭过去一周酒类/烟草支出"
        construct = "household weekly expenditure component"
    elif role == "self_production_indicator":
        concept, display = "household_self_produced_food_indicator", "家庭是否自产农产品供自用"
        construct = "household self-production indicator"
    elif role == "self_produced_food_value":
        concept, display = "household_self_consumed_food_market_value", "家庭自产自用农产品市场估值"
        construct = "household self-produced food value"
    if not concept:
        continue
    source = raw_lookup.get((wave, code.lower()))
    rows.append({
        "wave": wave, "code": code, "concept_id": concept, "concept_label": display,
        "domain": "household economic resources", "module": str(source.module) if source else "Household_Income",
        "source_label": label, "mapping_status": "candidate from audited official household-expenditure field coverage; response values/route comparability review pending",
        "construct": construct, "reference_period": r.reference_period,
        "caveat": caveat + " Household-level measure reported by a financial respondent; household values may repeat across respondent records. Do not interpret as individual income or sum components into total expenditure without a prespecified, wave-specific definition.",
        "source_archive": f"{source.source}; audit/household_ses_field_coverage_v1.csv" if source else "audit/household_ses_field_coverage_v1.csv",
    })

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "household_economic_exposure_mapping_v1.csv", index=False, encoding="utf-8-sig")
summary = (out.groupby(["construct", "concept_id", "concept_label"], dropna=False)
           .agg(waves=("wave", lambda x: ",".join(sorted(set(x)))), source_fields=("code", "size"), source_codes=("code", lambda x: ";".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "household_economic_exposure_concept_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"household economic mappings={len(out)}; concepts={out.concept_id.nunique()}; constructs={out.construct.nunique()}")
