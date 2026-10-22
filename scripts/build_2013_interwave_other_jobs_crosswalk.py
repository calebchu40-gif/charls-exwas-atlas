"""Map 2013 retrospective between-wave other-job items from official metadata."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
ITEMS = {
    "fa006_w2_5": ("interwave_other_job_count", "两轮访谈间其他工作数量", "jobs",
        "Count of other jobs held for at least one month between the prior and current interview.",
        "Excludes work held in the prior interview and work held at the current interview. If 0, the questionnaire skips to FA007; later duration/intensity/income items are structurally skipped, not zero."),
    "fa006_w2_6": ("interwave_other_jobs_months_worked", "两轮访谈间其他工作累计月份", "months",
        "Total number of months worked across the qualifying between-wave other jobs.",
        "Only asked after fa006_w2_5 is positive. Do not infer months from the interview interval or treat a routed skip as zero."),
    "fa006_w2_7": ("interwave_other_jobs_weeks_per_month", "两轮访谈间其他工作每月平均工作周数", "weeks per month",
        "Average weeks worked per month while doing the qualifying between-wave other jobs.",
        "Only asked after fa006_w2_5 is positive. This is not the count of weeks in the whole interview interval."),
    "fa006_w2_8": ("interwave_other_jobs_days_per_week", "两轮访谈间其他工作每周平均工作天数", "days per week",
        "Average days worked per week while doing the qualifying between-wave other jobs.",
        "Only asked after fa006_w2_5 is positive. Keep separate from the weeks-per-month and hours-per-day items; do not derive total hours without a reviewed rule."),
    "fa006_w2_9": ("interwave_other_jobs_hours_per_day", "两轮访谈间其他工作每天平均工作小时数", "hours per day",
        "Average hours worked per day while doing the qualifying between-wave other jobs.",
        "Only asked after fa006_w2_5 is positive. Not a current-work or primary-job hours measure."),
    "fa006_w2_10": ("interwave_other_jobs_monthly_income", "两轮访谈间其他工作月平均收入", "yuan per month",
        "Average monthly earnings from the qualifying between-wave other jobs, with personal income tax and insurance payment excluded per the questionnaire wording.",
        "Only asked after fa006_w2_5 is positive. The questionnaire defines the reference work interval and excludes prior-wave and current jobs. Do not merge with current-job wages or 2018 secondary-job income."),
}

raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
wave = raw[(raw.wave == "2013") & raw.variable.str.lower().isin(ITEMS)]
by_code = {r.variable.lower(): r for r in wave.itertuples(index=False)}
missing = sorted(set(ITEMS) - set(by_code))
if missing:
    raise SystemExit(f"2013 FA006 metadata missing: {missing}")

questionnaire = "sources_official/CHARLS_2013_Questionnaire.pdf (pp. 144-145)"
codebook = "sources_official/CHARLS_2013_Codebook_extracted.txt (p. 729)"
rows = []
for code, (concept_id, label, unit, semantics, caveat) in ITEMS.items():
    rec = by_code[code]
    rows.append({
        "concept_id": concept_id, "concept_label": label, "domain": "Work organization",
        "wave": "2013", "code": code, "module": rec.module, "source_label": rec.variable_label,
        "unit": unit, "value_semantics": semantics,
        "source_document": f"{questionnaire}; {codebook}",
        "mapping_status": "official 2013 questionnaire and codebook item reviewed; candidate; route and analysis eligibility require survey-design review",
        "questionnaire_review": "2013 FA006_w2 retrospective work-history path verified; item-level route retained. See audit/interwave_other_job_mapping_review_2026-10-17.md.",
        "caveat": caveat, "source_archive": rec.source,
    })
pd.DataFrame(rows).to_csv(AUDIT / "interwave_other_job_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"2013 FA006 between-wave other-job measures={len(rows)}; distinct concepts={len({r['concept_id'] for r in rows})}")
