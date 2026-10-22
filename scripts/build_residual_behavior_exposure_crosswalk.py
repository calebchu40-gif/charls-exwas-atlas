"""Add two reviewed residual behavior/social-environment E candidates.

This metadata-only builder uses official source-variable inventory rows and
does not read respondent-level data or use codebook frequency tables.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

SPECS = {
    "household_meals_provided_to_guests": {
        "label": "Household meals provided to guests in the prior week",
        "module": "household_income",
        "unit": "household person-meals during the prior week",
        "period": "last week",
        "semantics": "continuous count; CHARLS household respondent reports meals provided to guests",
        "caveat": "Household-level social reciprocity/hosting measure, not an individual dietary intake or an environmental pollutant. Keep household level explicit when linking to a respondent; do not split by household member. The questionnaire soft-check threshold is not an analytic validity bound. No categorical value labels are defined.",
        "codes": {"2011": ["ge005"], "2013": ["ge005"], "2015": ["ge005"], "2018": ["ge005"], "2020": ["gf005"]},
        "docs": {
            "2011": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
            "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt",
            "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt",
            "2018": "sources_official/CHARLS_2018_Questionnaire_extracted.txt",
            "2020": "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt",
        },
    },
    "previous_day_sleep_schedule": {
        "label": "Sleep and wake clock-time components on the previous day",
        "module": "Health_Status_and_Functioning",
        "unit": "clock-time components: AM/PM, hour, minute",
        "period": "yesterday / previous-day recall",
        "semantics": "wave-specific time components; do not combine without validating routing and component meaning",
        "caveat": "Single-wave candidate based on prior-day wake and bedtime questions. WB03/WB04 use a 12-hour clock in the questionnaire. The codebook distinguishes AM/PM fields and exact-report hour/minute components, with markedly different completion patterns; preserve every source field and verify routing before deriving clock time. This is not usual sleep timing, sleep duration, or a multi-day average. Codebook frequencies are not sample-size estimates for this project.",
        "codes": {"2013": ["wb03", "wb03_1", "wb03_2", "wb03_3", "wb03_4", "wb04", "wb04_1", "wb04_2", "wb04_3", "wb04_4"]},
        "docs": {"2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt"},
    },
}

rows = []
for concept, spec in SPECS.items():
    for wave, codes in spec["codes"].items():
        for code in codes:
            found = raw[(raw.wave == wave) & raw.variable.str.lower().eq(code.lower())]
            if found.empty:
                raise SystemExit(f"Source field missing from raw catalog: {wave}/{code}")
            for rec in found.itertuples(index=False):
                labels = "1=AM; 2=PM (official codebook response codes)" if code.lower() in {"wb03", "wb04"} else ""
                rows.append({
                    "wave": wave, "code": code, "concept_id": concept,
                    "concept_label": spec["label"], "domain": "behavior and household social context",
                    "module": rec.module, "source_label": rec.variable_label,
                    "unit": spec["unit"], "value_labels": labels,
                    "value_semantics": f"{spec['period']}; {spec['semantics']}",
                    "mapping_status": "candidate exposure mapping; official questionnaire/codebook field identified; route, denominator and derivation review required",
                    "construct": spec["period"], "caveat": spec["caveat"],
                    "source_archive": f"{rec.source}; {spec['docs'][wave]}",
                })

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "residual_behavior_exposure_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"residual behavior/social E concepts={out.concept_id.nunique()} mappings={len(out)}")
print(out.groupby("concept_id").size().to_string())
