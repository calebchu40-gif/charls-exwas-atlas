"""Map additional 2011 New Rural Social Pension Insurance fields.

Official public metadata only; no respondent data or codebook frequencies.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
codes = ["fn073_1", "fn073_2", "fn074_1", "fn074_2", "fn074_3",
         "fn075", "fn076", "fn078_1", "fn078_2"]
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str,
                  encoding="utf-8-sig").fillna("")
raw = raw[(raw.wave == "2011") & raw.variable.str.lower().isin(codes)]
by_code = {r.variable.lower(): r for r in raw.itertuples(index=False)}
missing = sorted(set(codes) - set(by_code))
if missing:
    raise SystemExit(f"missing official raw metadata rows: {missing}")

rows = []

def add(code, concept, label, construct, unit, semantics, caveat, value_labels=""):
    r = by_code[code]
    rows.append({
        "wave": "2011", "code": code, "concept_id": concept,
        "concept_label": label, "domain": "social protection",
        "module": r.module, "source_label": r.variable_label,
        "source_item": "FN073–FN078 New Rural Social Pension Insurance detail",
        "construct": construct, "unit": unit, "value_labels": value_labels,
        "value_semantics": semantics,
        "mapping_status": "2011 questionnaire/CodeBook item reviewed; candidate mapping",
        "caveat": caveat,
        "source_archive": r.source,
        "official_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    })

date_caveat = (
    "Asked in the 2011 NRSP route only. Year and month are separate date components, "
    "not continuous measures; questionnaire permits month=0 when the respondent "
    "cannot recall it. Do not interpret month 0 as January."
)
add("fn073_1", "pension_new_rural_participation_start_date_components",
    "新农保首次参保年月", "Calendar year of first NRSP coverage", "calendar year",
    "Year component; questionnaire range 2008–2011.", date_caveat)
add("fn073_2", "pension_new_rural_participation_start_date_components",
    "新农保首次参保年月", "Month of first NRSP coverage", "month",
    "Month component; 0 is the questionnaire's don't-remember code.", date_caveat)

annual_caveat = (
    "NRSP contribution amount, asked through a plan-specific contribution route. "
    "Preserve the amount form and unit; do not substitute interval bounds or combine "
    "annualized and lump-sum currency values."
)
add("fn074_1", "pension_annual_contribution_amount", "养老金年度缴费金额",
    "NRSP annual contribution amount under annual-payment option", "CNY/year",
    "Annual payment amount for FN074 option 1.", annual_caveat)
add("fn074_2", "pension_lump_sum_contribution_amount", "新农保一次性缴费金额",
    "NRSP lump-sum contribution amount", "CNY",
    "One-time lump-sum amount for FN074 option 2; not an annual amount.", annual_caveat)
add("fn074_3", "pension_annual_contribution_amount", "养老金年度缴费金额",
    "Annual-equivalent contribution amount associated with NRSP lump-sum option", "CNY/year",
    "Annual-equivalent amount reported with FN074 option 2; distinct from the lump-sum total.", annual_caveat)

add("fn075", "pension_required_contribution_years", "领取待遇所需缴费年数",
    "Years of contribution required to receive NRSP benefits", "years",
    "Reported number of years required to pay premiums to receive benefits.",
    "2011 NRSP route only. This is the reported requirement, not years already enrolled or contributed; do not merge with participation duration.")

payer_labels = "1=Self; 2=Children; 3=Other family member or relative; 4=Other"
add("fn076", "pension_contribution_payer_new_rural_social_program_or_current",
    "新农保缴费承担者", "Who pays for NRSP participation", "categorical",
    "Payer source categories listed in the official questionnaire/codebook.",
    "Asked in the 2011 NRSP route; preserve the specified payer categories and route. "
    "Keep payer distinct from payment method and amount, and preserve CHARLS special-missing semantics.",
    value_labels=payer_labels)

add("fn078_1", "pension_benefit_start_date_components", "新农保开始领取待遇年月",
    "Calendar year when NRSP benefit receipt began", "calendar year",
    "Year component; questionnaire range 2008–2011.",
    "Asked only after FN077=Yes. Conditional on having started NRSP benefit receipt; year/month are date components, not continuous measures.")
add("fn078_2", "pension_benefit_start_date_components", "新农保开始领取待遇年月",
    "Month when NRSP benefit receipt began", "month",
    "Month component; 0 is the questionnaire's don't-remember code.",
    "Asked only after FN077=Yes. Conditional on having started NRSP benefit receipt; month 0 means don't remember, not January.")

out = AUDIT / "pension_2011_nrsp_detail_crosswalk_v1.csv"
base = pd.read_csv(AUDIT / "pension_exposure_variable_mapping_v1.csv",
                   dtype=str, encoding="utf-8-sig").fillna("")
canonical_labels = (base[base.concept_id.isin({r["concept_id"] for r in rows})]
                    .drop_duplicates("concept_id").set_index("concept_id").concept_label.to_dict())
for row in rows:
    if row["concept_id"] in canonical_labels:
        row["concept_label"] = canonical_labels[row["concept_id"]]
pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
summary = (pd.DataFrame(rows).groupby(["concept_id", "concept_label"], as_index=False)
           .agg(fields=("code", "size"), source_codes=("code", lambda x: ";".join(x)),
                meaning=("construct", "first")))
summary.to_csv(AUDIT / "pension_2011_nrsp_detail_summary_v1.csv", index=False,
               encoding="utf-8-sig")
print(f"2011 NRSP detail mappings={len(rows)}; concepts={summary.concept_id.nunique()}")
