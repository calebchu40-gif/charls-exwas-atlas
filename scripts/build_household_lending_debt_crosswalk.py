"""Map household lending, interest receipts and non-mortgage debt fields."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

CONSTRUCTS = {
    "ha069": ("household_has_unrepaid_lending", "家户是否有借出且尚未收回的款项", "reported household status of lending not yet repaid", "categorical response code", "1=Yes; 2=No", "The 2011/2013 questionnaire routes a No response to HA071; retain the status and do not infer missing as No."),
    "ha070": ("household_unrepaid_lending_amount", "家户借出未收回款项总额", "reported amount of household loans still owed to it", "Yuan", "", "Asked only after HA069=Yes. This is household receivable principal, not the respondent's individual asset; preserve conditional missingness and do not replace it with zero."),
    "ha071": ("household_interest_income_from_lending_past_year", "家户过去一年借出款项利息收入", "reported household interest income from loans lent to others in the past year", "Yuan", "", "Past-year household interest income. The questionnaire routes HA069=No to this item, so it is not limited to households with a currently unpaid receivable; preserve nonresponse and any special values."),
    "ha072": ("household_nonmortgage_debt_owed_to_families_individuals_or_work_unit", "家户欠其他家庭、个人或工作单位的非抵押贷款总额", "reported household debt owed to other families, individuals or the work unit, excluding mortgage loans", "Yuan", "", "Household-level outstanding debt; the official item excludes mortgage loans and identifies specified lender types. If the exact amount is not provided, HA073 uses an unfolding-bracket route; do not midpoint-impute or treat bracket responses as exact amounts."),
}
SOURCE = {
    "2011": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Codebook_extracted.txt",
}
rows = []
for rec in raw.itertuples(index=False):
    wave = str(rec.wave)
    code = str(rec.variable).lower()
    if "household_income" not in str(rec.module).lower():
        continue
    if wave in {"2011", "2013"} and code in CONSTRUCTS:
        concept, label, construct, unit, value_labels, caveat = CONSTRUCTS[code]
        rows.append({
            "wave": wave, "code": code, "catalog_role": "e", "concept_id": concept,
            "concept_label": label, "domain": "income, wealth, and material resources",
            "module": rec.module, "source_label": rec.variable_label,
            "mapping_status": "candidate; official household questionnaire/Codebook identity and route reviewed; analysis eligibility pending",
            "construct": construct, "unit": unit, "value_labels": value_labels,
            "value_semantics": "household-level source item; retain original response and wave-specific missingness",
            "value_label_status": "official questionnaire response labels reviewed; frequencies omitted; wave-specific" if value_labels else "continuous amount; Yuan unit verified in official questionnaire",
            "value_label_source": SOURCE[wave], "caveat": caveat, "source_archive": rec.source,
        })
    elif wave == "2015" and code in CONSTRUCTS:
        # The 2015 Codebook lists these legacy fields as No Observations.
        # Keep them searchable as inactive metadata, never as candidate E measures.
        rows.append({
            "wave": wave, "code": code, "catalog_role": "c", "concept_id": "",
            "concept_label": "", "domain": "measurement metadata", "module": rec.module,
            "source_label": rec.variable_label,
            "mapping_status": "inactive legacy field; 2015 official Codebook reports No Observations",
            "construct": "no-observation household lending/debt legacy field", "unit": "",
            "value_labels": "", "value_semantics": "no observed responses reported in official Codebook",
            "value_label_status": "official Codebook reports No Observations",
            "value_label_source": SOURCE[wave],
            "caveat": "C-only metadata; do not treat as zero, a negative response, or an analyzable household measure.",
            "source_archive": rec.source,
        })
    elif (wave == "2011" and code in {f"ha073_{i}" for i in range(1, 7)}) or (wave == "2013" and code in {"ha073_bracket_min", "ha073_bracket_max"}):
        rows.append({
            "wave": wave, "code": code, "catalog_role": "c", "concept_id": "",
            "concept_label": "", "domain": "measurement metadata", "module": rec.module,
            "source_label": rec.variable_label,
            "mapping_status": "unfolding-bracket response/threshold metadata; not an exact debt amount",
            "construct": "fallback debt bracket protocol item", "unit": "official bracket response component",
            "value_labels": "", "value_semantics": "conditional fallback when the exact HA072 amount is not supplied",
            "value_label_status": "official questionnaire route reviewed; component interpretation requires release-version confirmation",
            "value_label_source": SOURCE[wave],
            "caveat": "C-only measurement metadata. The instrument uses an unfolding-bracket route after HA072 nonresponse; do not treat thresholds or bounds as exact debt values, create a midpoint, or count components as separate exposures.",
            "source_archive": rec.source,
        })

out = pd.DataFrame(rows)
out = out.drop_duplicates(["wave", "code", "catalog_role", "concept_id"])
out.to_csv(AUDIT / "household_lending_debt_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
e = out[out.catalog_role.eq("e")]
print(f"household lending/debt: E mappings={len(e)} across {e.concept_id.nunique()} concepts; C legacy/bracket metadata={len(out)-len(e)}")
