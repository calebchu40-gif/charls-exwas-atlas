"""Map general-schooling history fields with official wave-specific routing notes.

Metadata only: never reads respondent microdata or imports codebook frequencies.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

DOCS = {
    "2011": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
    "2018": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt",
}

SPECS = {
    "primary_grade_completed": {
        "label": "小学阶段完成年级",
        "fields": {"2011": ["bd002"], "2013": ["bd002"]},
        "unit": "grade (1–6)", "semantics": "highest completed grade in primary school",
        "values": "1–6=completed primary-school grade (official questionnaire range)",
        "caveat": "Conditional item: 2011 is routed when BD001=2; 2013 when BD001=3 or BD001_W2_4=3. Keep structural skips distinct from missing responses; this is not total years of schooling.",
    },
    "additional_schooling_years_after_attained_level": {
        "label": "所选最高学历之后的额外受教育年数",
        "fields": {"2011": ["bd003"], "2013": ["bd003"]},
        "unit": "years", "semantics": "additional schooling years after the level selected in BD001",
        "values": "Continuous years; 2011/2013 questionnaire defines the response in years",
        "caveat": "Conditional on attained-education category (2011 BD001≥4; 2013 BD001 or BD001_W2_4≥5). Interviewer instruction says count years required for the grade rather than extra elapsed years from repeated/skipped grades. This is not total schooling years and should not be added mechanically to another education measure.",
    },
    "age_started_formal_schooling": {
        "label": "开始正规/正式上学年龄",
        "fields": {"2011": ["bd005"], "2013": ["bd005"]},
        "unit": "years of age", "semantics": "age at which respondent began formal schooling",
        "values": "1–120 years; questionnaire soft-check flags values below 6 or above 11",
        "caveat": "In 2013, reinterview participants with nonmissing prior BD005 are routed past the question; missing prior values are re-asked and new interviews are asked. Preserve interview route and structural skips; do not impute skipped values.",
    },
    "age_stopped_schooling": {
        "label": "停止上学年龄（完成学业年龄）",
        "fields": {"2011": ["bd006"], "2013": ["bd006"], "2015": ["bd006"], "2018": ["bd006"]},
        "unit": "years of age", "semantics": "age when respondent finished/stopped schooling; source wording is wave-specific",
        "values": "2011/2013/2015: questionnaire range 1–120; 2018: 0–120, with 0 explicitly recorded if never attended school",
        "caveat": "The 2011/2013/2015 interviewer note distinguishes stopping schooling from finishing elementary school. 2018 asks age at finishing the highest education level and explicitly records 0 if never attended; the 2018 education-history block is routed to new interviews and selected reinterview education-update routes. Preserve these wording/route differences; do not assume strict measurement equivalence.",
    },
    "schooling_years_after_highest_credential": {
        "label": "最高学历后的继续受教育年数（波次更新题）",
        "fields": {"2015": ["bd002_w3"], "2018": ["bd002_w3"]},
        "unit": "years", "semantics": "years of schooling after the referenced highest-education level; wave-specific update item",
        "values": "Continuous years; 2015 codebook reports numeric summary fields and 2018 questionnaire explicitly says record 0 if no further schooling (no frequencies imported)",
        "caveat": "Keep separate from BD003: 2015 asks years at school after the highest level changed from last wave; 2018 asks years after BD001_W2_4 and explicitly allows 0 for no further schooling. Conditional/route and reference-level differences mean no pooled recode is asserted.",
    },
    "traditional_home_schooling_years": {
        "label": "私塾/家塾教育年数",
        "fields": {"2013": ["bd002_w2_1"]},
        "unit": "years", "semantics": "years spent in sishu/home school",
        "values": "Continuous years; 2013 official codebook reports a numeric measure (frequencies omitted)",
        "caveat": "2013 questionnaire routes this item when the selected education level is sishu/home school (BD001 or BD001_W2_4=4). It is a single-wave pathway-specific measure, not general years of schooling and not adult education.",
    },
    "educated_youth_send_down_experience": {
        "label": "上山下乡知青经历",
        "fields": {"2018": ["bg005_w4"]},
        "unit": "binary response (official codes retained)", "semantics": "ever participated in the Up to Mountains and Down to the Countryside Movement as an educated youth",
        "values": "1=Yes; 2=No (official 2018 codebook labels)",
        "caveat": "2018 single-wave life-course exposure. Keep separate from its conditional start-year field and the conditional return-to-city item; no cross-wave counterpart is asserted.",
    },
    "educated_youth_send_down_start_year": {
        "label": "上山下乡知青经历开始年份",
        "fields": {"2018": ["bg005_w4_1"]},
        "unit": "calendar year", "semantics": "year of participation in the educated-youth movement",
        "values": "Continuous calendar year; conditional follow-up to BG005_W4",
        "caveat": "Asked only for respondents reporting the experience; structural skips are not No or zero. Treat as an event-date component, not an independent binary exposure.",
    },
    "return_to_city_after_educated_youth": {
        "label": "知青经历后是否回城",
        "fields": {"2018": ["bg006_w4"]},
        "unit": "binary response (official codes retained)", "semantics": "returned to the city after the educated-youth movement",
        "values": "1=Yes; 2=No (official 2018 codebook labels)",
        "caveat": "Conditional follow-up among respondents who reported the educated-youth experience. Retain the selected denominator; an unasked response is not No.",
    },
    "educated_youth_return_to_city_year": {
        "label": "知青经历后回城年份",
        "fields": {"2018": ["bg006_w4_1"]},
        "unit": "calendar year", "semantics": "year of return to the city after the educated-youth movement",
        "values": "Continuous calendar year; conditional follow-up to BG006_W4",
        "caveat": "Only asked after a Yes return-to-city response. Keep as an event-date component, not an independent outcome or exposure; do not impute skipped years.",
    },
}

rows = []
for concept, spec in SPECS.items():
    for wave, codes in spec["fields"].items():
        for code in codes:
            found = raw[(raw.wave == wave) & raw.variable.str.lower().eq(code.lower())]
            if found.empty:
                raise SystemExit(f"Official metadata field absent: {wave} {code}")
            for rec in found.itertuples(index=False):
                rows.append({
                    "wave": wave, "code": code, "concept_id": concept,
                    "concept_label": spec["label"], "domain": "sociodemographic and social context",
                    "module": rec.module, "source_label": rec.variable_label,
                    "unit": spec["unit"], "value_labels": spec["values"],
                    "value_semantics": spec["semantics"],
                    "mapping_status": "official questionnaire and codebook field reviewed; candidate mapping, preserve wave-specific routing",
                    "caveat": spec["caveat"],
                    "source_archive": f"{rec.source}; {DOCS[wave]}",
                })

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "formal_schooling_lifecourse_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
summary = (out.groupby(["concept_id", "concept_label"], dropna=False)
           .agg(waves=("wave", lambda x: ",".join(sorted(set(x)))), mappings=("code", "size"),
                source_codes=("code", lambda x: ";".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "formal_schooling_lifecourse_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"formal schooling concepts={out.concept_id.nunique()} mappings={len(out)}")
