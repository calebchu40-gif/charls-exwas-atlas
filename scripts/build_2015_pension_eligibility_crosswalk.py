"""Build 2015 pension eligibility and scheme-status mappings from CHARLS docs.

Metadata-only; codebook frequency tables are deliberately not copied.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
codes = ["fn069_w3", *(f"fn057_w3s{i}" for i in range(1, 5)),
         *(f"fn057_w3_0s{i}" for i in range(1, 4))]
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str,
                  encoding="utf-8-sig").fillna("")
raw = raw[(raw.wave == "2015") & raw.variable.str.lower().isin(codes)]
by_code = {r.variable.lower(): r for r in raw.itertuples(index=False)}
missing = sorted(set(codes) - set(by_code))
if missing:
    raise SystemExit(f"missing official raw metadata rows: {missing}")

rows = []

def add(code, concept, label, construct, values, semantics, caveat):
    rec = by_code[code]
    rows.append({
        "wave": "2015", "code": code, "concept_id": concept,
        "concept_label": label, "domain": "social protection",
        "module": rec.module, "source_label": rec.variable_label,
        "source_item": "FN069_w3" if code == "fn069_w3" else
                       "FN057_w3" if code.startswith("fn057_w3s") else "FN057_w3_0",
        "construct": construct, "unit": "categorical",
        "value_labels": values, "value_semantics": semantics,
        "mapping_status": "2015 questionnaire and CodeBook labels/routes reviewed; candidate mapping",
        "caveat": caveat,
        "source_archive": rec.source,
        "official_source": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
    })

eligibility_values = (
    "1=Yes, have qualification; 2=Yes, other reason; "
    "3=No, participate in government or firm pension; "
    "4=No, local community has not implemented; 5=No, other reason"
)
add("fn069_w3", "pension_residents_scheme_eligibility_status",
    "是否具备居民养老保险参保资格及未获资格原因",
    "Eligibility/status for resident pension insurance",
    eligibility_values,
    "Nominal response categories; only category 1 explicitly means qualified. Category 2 records another affirmative/eligibility route; categories 3–5 are distinct non-eligibility reasons. Do not recode as simple yes/no without a prespecified rule.",
    "2015 Wave 3 only. FN069_w3 is a five-category status, not a general participation variable. Follow-up reason fields fn069_w3_1/_2 are conditional text/detail fields and are not mapped as independent exposures.")

participation = {
    1: "New Rural Social Pension Insurance",
    2: "Residents' Pension",
    3: "Urban Residents' Pension",
    4: "None of the listed pension types",
}
for i, label in participation.items():
    add(f"fn057_w3s{i}", "pension_2015_participation_or_receipt_type",
        "2015年报告参加或领取的养老金类型",
        "Pension type reported as participated in or received",
        f"{i}={label}",
        f"Selected option {i} identifies: {label}. The questionnaire wording combines participation or receipt; retain that combined construct and do not equate it with a clean current-enrollment indicator.",
        "2015 Wave 3 only. Multi-select slots. Preserve the questionnaire's combined 'participated in or received' wording, the plan-specific routing, and unselected/structural missing semantics.")

eligible_not_participating = {
    1: "New Rural Social Pension Insurance",
    2: "Residents' Pension",
    3: "Urban Residents' Pension",
}
for i, label in eligible_not_participating.items():
    add(f"fn057_w3_0s{i}", "pension_qualified_but_not_participating_by_scheme",
        "具备资格但未参加的养老保险类型",
        "Qualified but not participating in scheme",
        f"{i}=Qualified but not participating in {label}",
        f"Selected option {i} indicates qualification without participation in {label}; asked only on the FN057_w3=none and FN069_w3 eligible/other-affirmative route.",
        "2015 Wave 3 only. Conditional multi-select. Structural skips outside the eligibility route are not non-participation observations; never infer No from a blank slot.")

out = AUDIT / "pension_eligibility_2015_crosswalk_v1.csv"
pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
summary = (pd.DataFrame(rows).groupby(["concept_id", "concept_label"], as_index=False)
           .agg(fields=("code", "size"), source_codes=("code", lambda x: ";".join(x)),
                meaning=("construct", "first")))
summary.to_csv(AUDIT / "pension_eligibility_2015_summary_v1.csv", index=False,
               encoding="utf-8-sig")
print(f"2015 pension eligibility mappings={len(rows)}; new concepts={summary.concept_id.nunique()}")
