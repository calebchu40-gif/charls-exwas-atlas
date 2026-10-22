"""Audit and expose the 2020 household COVID-period economic items."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
questionnaire = "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt"
codebook = "sources_official/CHARLS_2020_Codebook_extracted.txt"
doc = f"{questionnaire}; {codebook} (labels only; frequency tables were not used)"
specs = []

def add(code, concept_id, label, value_labels, unit, caveat, status="candidate; questionnaire and Codebook labels reviewed; validate routes and eligible denominator in approved data"):
    specs.append((code, concept_id, label, value_labels, unit, caveat, status))

add("gc007", "covid_agricultural_income_change_2020", "疫情期间家庭农业净收入变化（2020）",
    "1=Decreased; 2=Increased; 3=Unaffected (verify released-data coding)",
    "Household-level categorical change; Chinese New Year to interview",
    "2020 single-wave retrospective attribution to COVID-19. Household-level item; the stem says agricultural net incomes of household members. Preserve original categories, time frame and route; do not treat as a measured causal COVID effect.")
for code, direction, label in [("gc007_1","decreased","疫情期间家庭农业净收入减少金额（2020）"),("gc007_2","increased","疫情期间家庭农业净收入增加金额（2020）")]:
    add(code, f"covid_agricultural_income_{direction}_amount_2020", label, "", "Yuan; conditional on GC007 direction",
        "Conditional amount from Chinese New Year to interview, household-level. Keep decreased and increased amounts separate, retain -1/unknown handling per official rules, and do not set skipped amounts to zero.")
add("gd005", "covid_self_employment_income_change_2020", "疫情期间家庭自雇活动净收入变化（2020）",
    "1=Decreased; 2=Increased; 3=Unaffected (verify released-data coding)",
    "Household-level categorical change; Chinese New Year to interview",
    "2020 single-wave retrospective attribution to COVID-19. Applies to household self-employed activity income; keep distinct from agricultural income and individual employment income.")
for code, direction, label in [("gd005_1","decreased","疫情期间家庭自雇净收入减少金额（2020）"),("gd005_2","increased","疫情期间家庭自雇净收入增加金额（2020）")]:
    add(code, f"covid_self_employment_income_{direction}_amount_2020", label, "", "Yuan; conditional on GD005 direction",
        "Conditional amount from Chinese New Year to interview, household-level. Keep decreased and increased amounts separate; do not set skipped amounts to zero.")
add("gf014", "covid_household_income_expense_adequacy_2020", "疫情期间家庭收入覆盖日常开支难度（2020）",
    "1=Very difficult; 2=Difficult; 3=Easy; 4=Very easy",
    "Household-level ordinal response; COVID outbreak to interview",
    "Single-wave self-report of financial strain, not an income amount. Preserve the ordered four-category response and source direction.")
for i, (code, label) in enumerate([
    ("gf015_s1","疫情期间停止支付房租（2020）"),
    ("gf015_s2","疫情期间停止支付按揭（2020）"),
    ("gf015_s3","疫情期间停止支付水电/公用事业账单（2020）")], 1):
    add(code, f"covid_household_payment_arrears_{i}_2020", label, f"0=No; {i}=Yes",
        "Household-level multiple-response item; COVID outbreak to interview",
        "Single-wave household financial hardship indicator. Questionnaire allows multiple selections; preserve the field-specific route and do not combine with GF014 as though they were one scale.")
add("gf015_s4", "covid_household_payment_arrears_none_option_2020", "疫情期间未停止支付任一账单（2020；互斥选项字段）",
    "0=No; 4=Yes", "Household-level multiple-response routing/none-of-the-above marker",
    "The questionnaire marks option 4 as a conflict with selections 1–3. Preserve as a routing/consistency marker; DO NOT ANALYZE as an independent exposure until released-data encoding and consistency are validated.",
    "DO NOT ANALYZE pending validation of the none-of-the-above conflict and released-data storage")
for i, (code, label) in enumerate([
    ("gf016_s1","疫情期间通过削减开支应对收入不足（2020）"),
    ("gf016_s2","疫情期间通过动用储蓄应对收入不足（2020）"),
    ("gf016_s3","疫情期间通过出售资产应对收入不足（2020）"),
    ("gf016_s4","疫情期间接受亲友帮助应对收入不足（2020）"),
    ("gf016_s5","疫情期间向亲友借款应对收入不足（2020）"),
    ("gf016_s6","疫情期间向银行借款应对收入不足（2020）"),
    ("gf016_s7","疫情期间采用其他方式应对收入不足（2020）")], 1):
    add(code, f"covid_household_income_coping_strategy_{i}_2020", label, f"0=No; {i}=Yes",
        "Household-level multiple-response item; COVID outbreak to interview",
        "Asked only when household income cannot cover daily expenses. Preserve item-level selection and route; do not sum strategies into an unvalidated score.")
add("gf016_s8", "covid_household_income_coping_none_other_conflict_2020", "疫情期间收入不足应对第8选项（GF016；题干与Codebook标签冲突）",
    "Questionnaire: 8=Do nothing; Codebook field label: Others (conflict)",
    "Household-level response/routing marker; coding unresolved",
    "The English questionnaire lists option 8 as Do nothing and flags it as a conflict; the released Codebook labels gf016_s8 as Others. Preserve for traceability only; DO NOT ANALYZE until source encoding and respondent-level meaning are validated.",
    "DO NOT ANALYZE pending resolution of questionnaire-Codebook conflict and released-data storage")
for i, label in enumerate([
    "疫情期间削减开支金额（2020）","疫情期间动用储蓄金额（2020）","疫情期间出售资产所得金额（2020）",
    "疫情期间接受亲友帮助金额（2020）","疫情期间向亲友借款金额（2020）","疫情期间向银行借款金额（2020）",
    "疫情期间其他收入不足应对方式所得金额（2020）"], 1):
    add(f"gf016_{i}", f"covid_household_income_coping_amount_{i}_2020", label, "", "Yuan; conditional on the corresponding GF016 strategy",
        "Asked only when household income cannot cover daily expenses and the corresponding strategy is selected. Amount is from COVID outbreak to interview; retain as seven distinct strategy-specific fields, do not sum or impute structural skips to zero.")

rows = []
for code, cid, label, value_labels, unit, caveat, status in specs:
    hit = raw[(raw.wave == "2020") & raw.variable.str.lower().str.strip().eq(code.lower())]
    if len(hit) != 1:
        raise ValueError(f"Expected one official catalog row for 2020 {code}; found {len(hit)}")
    src = hit.iloc[0]
    rows.append({"wave":"2020","code":code,"concept_id":cid,"concept_label":label,"domain":"Household COVID-period economic conditions",
        "module":src.module,"source_label":src.variable_label,"unit":unit,"construct":"household-level; single-wave COVID-period item",
        "value_labels":value_labels,"mapping_status":status,"caveat":caveat,"source_archive":src.source,"source_document":doc})
out = pd.DataFrame(rows)
out.to_csv(AUDIT / "household_covid_economic_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
items = []
for cid, group in out.groupby("concept_id", sort=False):
    first = group.iloc[0]
    items.append({"concept_id":cid,"label":first.concept_label,"domain":first.domain,"caveat":first.caveat,
        "source_fields":[{"wave":r.wave,"code":r.code,"module":r.module,"source_label":r.source_label,"unit":r.unit,
            "value_labels":r.value_labels,"mapping_status":r.mapping_status,"source_document":r.source_document} for _,r in group.iterrows()]})
(ROOT / "site-prototype" / "dist" / "household_covid_economic_v1.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"household COVID economic mappings={len(out)}; concepts={out.concept_id.nunique()}; do-not-analyze={out.mapping_status.str.startswith('DO NOT ANALYZE').sum()}")
