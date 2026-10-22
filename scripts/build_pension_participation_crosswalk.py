"""Build reviewed 2011 pension participation mappings from official CHARLS docs.

Metadata-only. Never reads respondent-level records or codebook frequencies.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str,
                  encoding="utf-8-sig").fillna("")
raw = raw[(raw.wave == "2011") & raw.variable.str.lower().isin(
    ["fn038", *(f"fn039s{i}" for i in range(1, 7)), "fn071", "fn079"])]
by_code = {r.variable.lower(): r for r in raw.itertuples(index=False)}

common_caveat = (
    "2011 baseline pension participation construct. Do not conflate with current "
    "pension receipt, benefit amounts, contribution status, or the separate "
    "government/institution and firm basic pension question. Respondent-level "
    "analysis eligibility and missingness must follow the official route."
)
rows = []
def add(code, concept, label, construct, semantics, value_labels="", caveat=common_caveat):
    r = by_code[code]
    rows.append({
        "wave": "2011", "code": code, "concept_id": concept,
        "concept_label": label, "domain": "social protection",
        "module": r.module, "source_label": r.variable_label,
        "source_item": "FN038" if code == "fn038" else "FN039 multi-select",
        "construct": construct, "unit": "CNY/month" if code == "fn079" else "categorical",
        "value_labels": value_labels, "value_semantics": semantics,
        "mapping_status": "official 2011 questionnaire and codebook reviewed; candidate mapping",
        "caveat": caveat,
        "source_archive": r.source,
        "official_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    })

add("fn038", "pension_nonbasic_program_participation_any",
    "是否参加至少一种非机关/企业基本养老保险项目",
    "Participation in at least one listed pension program",
    "1=Yes; 2=No. Question explicitly excludes government/institution pension and firms' basic pension. A No response routes past FN039 to FN071.",
    "1=Yes; 2=No")

types = {
    1: "Supplemental pension insurance of the firm",
    2: "Commercial pension",
    3: "Rural pension",
    4: "Residents' pension",
    5: "Urban residents' pension",
    6: "Other pension",
}
for i, name in types.items():
    add(f"fn039s{i}", "pension_participation_type_multi_select",
        "参保养老金项目类型（多选）", "Selected pension program type",
        f"Selected option {i}=Yes for {name}; empty/unobserved is not coded as No without route evidence.",
        f"{i}={name}",
        common_caveat + " FN039 is asked following FN038 Yes. Structural skips must not be counted as non-participation for individual types.")

add("fn071", "new_rural_social_pension_participation",
    "是否参加新型农村社会养老保险（新农保）",
    "Participation in New Rural Social Pension Insurance",
    "1=Yes; 2=No. Yes routes to FN073; No routes to the multi-select non-participation reasons FN072.",
    "1=Yes; 2=No",
    "2011 baseline, plan-specific participation. Do not combine automatically with generic rural/residents pension type or benefit receipt; preserve route and plan definition.")

add("fn079", "pension_monthly_benefit_amount", "每月养老金领取金额",
    "Monthly pension benefit amount after starting New Rural Social Pension receipt",
    "Continuous amount in CNY/month; asked only after FN077=Yes. Preserve official missing codes and do not replace missing with zero.",
    "", "Plan-specific New Rural Social Pension monthly benefit. FN079 is asked only after FN077=Yes; benefit recipients are a selected denominator and are not equivalent to all participants.")

out = AUDIT / "pension_participation_crosswalk_v1.csv"
new_concept_rows = [row for row in rows if row["code"] != "fn079"]
pd.DataFrame(new_concept_rows).to_csv(out, index=False, encoding="utf-8-sig")
summary = pd.DataFrame([
    {"concept_id": "pension_nonbasic_program_participation_any", "fields": 1,
     "codes": "fn038", "interpretation": "binary gate; excludes government/institution and firms' basic pension"},
    {"concept_id": "pension_participation_type_multi_select", "fields": 6,
     "codes": "fn039s1-fn039s6", "interpretation": "six distinct checkbox options; only selected-option codes are affirmative; blank is not No"},
    {"concept_id": "new_rural_social_pension_participation", "fields": 1,
     "codes": "fn071", "interpretation": "plan-specific participation gate; Yes/No routes differ"},
])
summary.to_csv(AUDIT / "pension_participation_summary_v1.csv", index=False, encoding="utf-8-sig")
# FN072 is already mapped by the pension catalog builder. Enrich its metadata
# in place to make the questionnaire routing explicit without duplicating rows.
pension_path = AUDIT / "pension_exposure_variable_mapping_v1.csv"
pension = pd.read_csv(pension_path, dtype=str, encoding="utf-8-sig").fillna("")
mask = pension.code.str.lower().str.match(r"fn072s[1-9]") & pension.wave.eq("2011")
pension.loc[mask, "caveat"] = pension.loc[mask, "caveat"].map(
    lambda value: (value + " Asked only after FN071=No; the denominator is nonparticipants. "
                   "An unasked/blank option is not evidence that the reason is absent.").strip())
# Add the officially confirmed monthly benefit field to the existing concept;
# repair the garbled display label across that concept's pension rows.
fn079 = pd.DataFrame([r for r in rows if r["code"] == "fn079"])
if len(fn079):
    pension = pd.concat([pension, fn079], ignore_index=True).drop_duplicates(
        ["wave", "code", "concept_id"], keep="last")
pension.loc[pension.concept_id.eq("pension_monthly_benefit_amount"), "concept_label"] = "每月养老金领取金额"
pension.to_csv(pension_path, index=False, encoding="utf-8-sig")
print(f"Wrote {len(new_concept_rows)} mappings for new concepts to {out}; enriched {int(mask.sum())} existing FN072 rows and added fn079 to an existing benefit concept")
