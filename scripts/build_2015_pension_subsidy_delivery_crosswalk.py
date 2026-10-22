"""Map 2015 oldest-old pension subsidy delivery form and card/voucher use."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
PAYMENT = {
    "ga004_w3s1": ("1=Cash", "Questionnaire and CodeBook labels agree."),
    "ga004_w3s2": ("2=Card", "Questionnaire and CodeBook labels agree."),
    "ga004_w3s3": (
        "Questionnaire: 3=Voucher; CodeBook: 3=Card; DO NOT ANALYZE until resolved",
        "Questionnaire and CodeBook conflict on option 3. Preserve source conflict; do not infer or recode.",
    ),
}
USE = {
    "ga004_w3_1s1": "1=Life care",
    "ga004_w3_1s2": "2=Domestic service",
    "ga004_w3_1s3": "3=Rehabilitation service",
    "ga004_w3_1s4": "4=Buy food",
    "ga004_w3_1s5": "5=Buy medicine",
    "ga004_w3_1s6": "6=Buy life items",
    "ga004_w3_1s7": "7=Other (specify)",
}

raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
codes = set(PAYMENT) | set(USE)
wave = raw[(raw.wave == "2015") & raw.variable.str.lower().isin(codes)]
by_code = {r.variable.lower(): r for r in wave.itertuples(index=False)}
missing = sorted(codes - set(by_code))
if missing:
    raise SystemExit(f"2015 subsidy delivery fields missing from metadata: {missing}")

questionnaire = "sources_official/CHARLS_2015_Questionnaire.pdf (p. 193)"
codebook = "sources_official/CHARLS_2015_Codebook_extracted.txt (GA004_W3 and GA004_W3_1)"
rows = []
for code, (label, caveat) in PAYMENT.items():
    rec = by_code[code]
    rows.append({
        "concept_id": "old_age_subsidy_payment_mode_2015",
        "concept_label": "高龄老人补助/养老券发放形式（2015）",
        "domain": "Social protection", "wave": "2015", "code": code,
        "module": rec.module, "source_label": rec.variable_label,
        "unit": "categorical multi-select option", "value_labels": label,
        "value_semantics": "Selected response option for payment form of the oldest-old pension subsidy/pension voucher.",
        "source_document": f"{questionnaire}; {codebook}",
        "mapping_status": "questionnaire/codebook reviewed; option 3 conflict marked DO NOT ANALYZE" if code == "ga004_w3s3" else "official questionnaire and CodeBook option label matched; candidate",
        "caveat": "Only asked after GA003 indicates receipt of the oldest-old pension subsidy/pension voucher. This is delivery form, not pension-plan participation or amount. It is check-all-that-apply; an empty option slot is not automatically No. " + caveat,
        "source_archive": rec.source,
    })
for code, label in USE.items():
    rec = by_code[code]
    rows.append({
        "concept_id": "old_age_subsidy_card_voucher_use_2015",
        "concept_label": "高龄老人养老卡/券用途（2015）",
        "domain": "Social protection", "wave": "2015", "code": code,
        "module": rec.module, "source_label": rec.variable_label,
        "unit": "categorical multi-select option", "value_labels": label,
        "value_semantics": "Selected use reported for an old-age subsidy card or voucher.",
        "source_document": f"{questionnaire}; {codebook}",
        "mapping_status": "official questionnaire and CodeBook option label matched; candidate",
        "caveat": "Only asked after GA003 indicates receipt of the subsidy/voucher and payment form is card or voucher. Cash recipients skip this item. Multi-select blank slots are not automatically No; do not combine usage options into separate constructs.",
        "source_archive": rec.source,
    })
pd.DataFrame(rows).to_csv(AUDIT / "pension_subsidy_delivery_2015_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"2015 old-age subsidy delivery mappings={len(rows)}; concepts=2; unresolved questionnaire/CodeBook conflicts=1")
