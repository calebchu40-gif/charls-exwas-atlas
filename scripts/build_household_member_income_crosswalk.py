"""Map household-member salary and pension amount slots without individualizing them."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

RULES = [
    ("household_member_salary_annual", "家户成员年度工资/薪酬金额槽位", r"^ga006_1_\d+_$", "annual wage/salary amount reported for household-member roster slots", "Annual family-member slots vary by wave (2011–2015 and 2020); slot numbers are not a stable person identifier and this is not respondent-level personal income. Do not sum or attribute to the CHARLS respondent without the official household roster linkage and route.", {"2011", "2013", "2015", "2020"}),
    ("household_member_salary_monthly", "家户成员月度工资/薪酬金额槽位", r"^ga006_2_\d+_$", "monthly wage/salary amount reported for household-member roster slots", "Monthly family-member slots vary by wave (2011–2015 and 2020); slot numbers are not a stable person identifier and this is not respondent-level personal income. Do not sum or attribute to the CHARLS respondent without the official household roster linkage and route.", {"2011", "2013", "2015", "2020"}),
    ("household_member_pension_annual", "家户成员年度养老金收入金额槽位", r"^ga008_1_a_\d+_$", "annual pension income amount reported for household-member slots", "2011 household income module only; household-member slot and family financial respondent must be preserved. Not respondent-level pension or a complete household total.", {"2011"}),
    ("household_member_pension_monthly", "家户成员月度养老金收入金额槽位", r"^ga008_1_b_\d+_$", "monthly pension income amount reported for household-member slots", "2011 household income module only; household-member slot and family financial respondent must be preserved. Not respondent-level pension or a complete household total.", {"2011"}),
    ("household_member_pension_subsidy_annual", "家户成员年度养老金补贴金额槽位", r"^ga008_3_a_\d+_$", "annual pension-subsidy amount reported for household-member roster slots; GA007 option 3", "2011 household-member roster field; preserve source slot and household financial respondent. This is pension subsidy (GA007 option 3), distinct from the general pension amount at option 1; not respondent-level income or a household total.", {"2011"}),
    ("household_member_pension_subsidy_monthly", "家户成员月度养老金补贴金额槽位", r"^ga008_3_b_\d+_$", "monthly pension-subsidy amount reported for household-member roster slots; GA007 option 3", "2011 household-member roster field; preserve source slot and household financial respondent. Keep monthly report separate from annual values; do not annualize or sum slots.", {"2011"}),
    ("household_member_other_income_annual", "家户成员年度其他收入金额槽位", r"^ga008_9_a_\d+_$", "annual other-income amount reported for household-member roster slots; GA007 option 9", "2011 household-member roster field for other income sources (including alimony/child support per questionnaire); source slot is not a stable person ID. Do not attribute to respondent or aggregate slots without roster linkage and a prespecified rule.", {"2011"}),
    ("household_member_other_income_monthly", "家户成员月度其他收入金额槽位", r"^ga008_9_b_\d+_$", "monthly other-income amount reported for household-member roster slots; GA007 option 9", "2011 household-member roster field for other income sources; preserve slot and monthly reporting format. Do not annualize or aggregate slots.", {"2011"}),
]

rows = []
for concept, label, pattern, construct, caveat, waves in RULES:
    for rec in raw.itertuples(index=False):
        wave, code = str(rec.wave), str(rec.variable).lower()
        if wave not in waves or not re.fullmatch(pattern, code):
            continue
        if "income" not in str(rec.module).lower():
            continue
        rows.append({
            "wave": wave, "code": rec.variable, "concept_id": concept,
            "concept_label": label, "domain": "household income and material resources",
            "module": rec.module, "source_label": rec.variable_label,
            "mapping_status": "candidate household-member slot mapping from official variable catalog; respondent/roster route review required",
            "construct": construct, "caveat": caveat,
            "source_archive": f"{rec.source}; official wave questionnaire/codebook",
        })

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "household_member_income_mapping_v1.csv", index=False, encoding="utf-8-sig")
summary = (out.groupby(["concept_id", "concept_label"], dropna=False)
           .agg(waves=("wave", lambda x: ",".join(sorted(set(x))),), source_fields=("code", "size"),
                source_codes=("code", lambda x: ";".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "household_member_income_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"household-member income mappings={len(out)}; concepts={out.concept_id.nunique()}")
