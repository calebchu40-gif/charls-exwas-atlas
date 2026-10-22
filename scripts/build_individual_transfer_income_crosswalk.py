"""Build wave-aware mappings for respondent individual transfer income.

Uses public variable metadata and official questionnaire/codebook labels only;
never reads respondent-level records or codebook frequency counts.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
raw = raw[raw.module.str.contains("individual_income", case=False, regex=False)].copy()

OPTION_LABELS = {
    1: "Pensions and pension income",
    2: "Unemployment compensation",
    3: "Pension subsidy / pension voucher (wording differs by wave)",
    4: "Workers' compensation",
    5: "Elderly family planning subsidy",
    6: "Medical aid",
    7: "Other government subsidy",
    8: "Social assistance / social income support (wording differs by wave)",
    9: "Other income / social transfer source",
    10: "None of the above",
}

rows: list[dict[str, str]] = []

def add(rec, concept_id: str, concept_label: str, construct: str, unit: str,
        value_semantics: str, caveat: str, status: str) -> None:
    rows.append({
        "wave": str(rec.wave), "code": str(rec.variable).lower(),
        "concept_id": concept_id, "concept_label": concept_label,
        "domain": "social protection and individual transfer income",
        "module": str(rec.module), "source_label": str(rec.variable_label),
        "source_item": "", "construct": construct, "unit": unit,
        "value_labels": "", "value_semantics": value_semantics,
        "mapping_status": status, "caveat": f"{caveat} {value_semantics}",
        "source_archive": str(rec.source),
        "official_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; "
                           "sources_official/CHARLS_2011_Codebook_extracted.txt; "
                           "sources_official/CHARLS_2013_Questionnaire_extracted.txt; "
                           "sources_official/CHARLS_2013_Codebook_extracted.txt; "
                           "sources_official/CHARLS_2015_Questionnaire_extracted.txt; "
                           "sources_official/CHARLS_2015_Codebook_extracted.txt; "
                           "sources_official/CHARLS_2018_Questionnaire_extracted.txt; "
                           "sources_official/CHARLS_2018_Codebook_extracted.txt; "
                           "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; "
                           "sources_official/CHARLS_2020_Codebook_extracted.txt",
    })

for rec in raw.itertuples(index=False):
    wave, code, label = str(rec.wave), str(rec.variable).lower(), str(rec.variable_label)
    if wave not in {"2011", "2013", "2015", "2018", "2020"}:
        continue

    # Multi-response income-source items: their raw code is the indicator key.
    match = re.fullmatch(r"ga003s(\d+)", code)
    if match and wave in {"2011", "2013", "2015"}:
        item = int(match.group(1))
    else:
        match = re.fullmatch(r"ga003_w4_s(\d+)", code) if wave == "2018" else None
        if not match and wave == "2020":
            match = re.fullmatch(r"ga005_s(\d+)", code)
        item = int(match.group(1)) if match else 0
    if item in OPTION_LABELS:
        if wave in {"2018", "2020"}:
            response = f"0=No; {item}=Yes (official item-specific codebook labels)"
            status = "official questionnaire item and codebook response labels reviewed; candidate mapping"
        else:
            response = f"item {item}: {OPTION_LABELS[item]}; 2011–2015 codebook lists affirmative option codes, but does not establish a safe 0/No recode"
            status = "official questionnaire/codebook item mapping reviewed; 2011–2015 nonselection/missing storage must remain unresolved"
        add(
            rec, "individual_transfer_income_source_receipt", "个人转移收入来源/领取类别",
            "multi-response individual transfer-income source item",
            "categorical/multi-response; retain wave-specific code",
            f"Item {item}: {OPTION_LABELS[item]}; wave-specific questionnaire wording is retained in source_label. {response}",
            "Past-year individual transfer-income question. For 2011–2015, a listed affirmative option code is not proof that blank/missing means No; do not binarize absent slots. For 2018/2020, the codebook documents 0=No and option-number=Yes. Option 10 (none) is exclusive by questionnaire instruction. 2020 explicitly includes individual COVID-19 pandemic subsidies among transfers.",
            status,
        )
        rows[-1]["source_item"] = str(item)
        continue

    # Source-specific monetary amounts; omit bracket endpoints, unit selectors,
    # administrative fields, and codebook aliases with no observed source field.
    amount = False
    unit = "prior-year Yuan; exact field interpretation remains wave-specific"
    if wave == "2013" and re.fullmatch(r"ga004_[12]_[1-9]_", code):
        amount = True
        unit = "Yuan/year (ga004_1_*) or Yuan/month (ga004_2_*), as indicated by source code"
    elif wave == "2015" and re.fullmatch(r"ga004_[1-9]_", code):
        amount = True
    elif wave == "2018" and re.fullmatch(r"ga003_w4_[1-9]", code):
        amount = True
    elif wave == "2020" and re.fullmatch(r"ga005_[1-9]", code):
        amount = True
    if amount:
        item_match = re.search(r"(?:ga004_[12]_(\d+)_|ga004_(\d+)_|ga003_w4_(\d+)|ga005_(\d+))$", code)
        item = next((g for g in item_match.groups() if g), "") if item_match else ""
        add(
            rec, "individual_transfer_income_source_amount", "按来源分类的个人转移收入金额",
            "amount received from a specific individual transfer-income source",
            unit,
            f"Source item {item}: {label}; preserve the original time unit and field rather than summing or converting automatically.",
            "Conditional on the transfer-income question and source-specific route. A missing amount is not automatically zero or proof that the source was not received. 2013 separates year/month amounts; 2015 source fields are direct amount fields while codebook year/month aliases are marked No Observations; 2018/2020 ask past-year source amounts in Yuan. Amount categories and source definitions vary by wave. Do not add these fields to pension-module amounts without a prespecified deduplication rule.",
            "official questionnaire and codebook wording reviewed; candidate amount mapping, no respondent values used",
        )
        rows[-1]["source_item"] = str(item)

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "individual_transfer_income_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
(ROOT / "site-prototype" / "dist" / "individual_transfer_income_v1.json").write_text(
    json.dumps(out.to_dict(orient="records"), ensure_ascii=False, indent=2), encoding="utf-8")
summary = (out.groupby(["concept_id", "concept_label", "construct"], dropna=False)
           .agg(mappings=("code", "size"), waves=("wave", lambda x: ",".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "individual_transfer_income_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"individual transfer-income mappings={len(out)}; concepts={out.concept_id.nunique()}; "
      f"receipt={sum(out.concept_id == 'individual_transfer_income_source_receipt')}; "
      f"amount={sum(out.concept_id == 'individual_transfer_income_source_amount')}")
