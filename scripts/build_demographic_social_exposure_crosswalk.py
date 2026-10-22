"""Map current education, hukou, and marital status source fields by wave."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

SPEC = {
    "education_attainment_current_or_update": {
        "label": "当前最高受教育程度（直接报告/返访更新题）",
        "domain": "education and social position",
        "fields": {"2011": ["bd001"], "2013": ["bd001", "bd001_w2_4"],
                   "2015": ["bd001_w2_4"], "2018": ["bd001_w2_4"], "2020": ["ba010"]},
        "construct": "Current education attainment candidate; source items differ by interview route.",
        "caveat": "2013–2018 update fields can encode no change as a separate response, not a direct education category. Use the audited education derivation and interview-type/previous-wave route; never interpret z* preloads as a same-wave response. 2020 excludes adult education in the current item.",
    },
    "current_hukou_type": {
        "label": "当前户口类别",
        "domain": "education and social position",
        "fields": {"2011": ["bc001"], "2013": ["bc001"], "2015": ["bc002_w3_1"],
                   "2018": ["bc002_w3_1"], "2020": ["ba009"]},
        "construct": "Current registered-household (hukou) type candidate.",
        "caveat": "Response categories and returner/new-interview routes vary by wave. Do not merge raw codes across waves or equate hukou type with actual urban/rural residence; use the audited hukou derivation where appropriate.",
    },
    "current_hukou_location": {
        "label": "当前户口登记地",
        "domain": "education and social position",
        "fields": {"2011": ["bc005"], "2013": ["bc005"], "2018": ["bc002_w3_4"]},
        "construct": "Current hukou location candidate; wave-specific item availability.",
        "caveat": "Location granularity and update route vary. The codebook fields can contain sensitive geographic detail; do not publish geographic values or identifiers, and obtain disclosure review before deriving area-level categories.",
    },
    "prior_interview_hukou_location_relation_2015": {
        "label": "上一轮户口登记地与常住地址关系（2015回顾项）",
        "domain": "education and social position",
        "fields": {"2015": ["bc001_w3_3"]},
        "construct": "Prior-interview hukou-location relation to permanent address; categorical historical context.",
        "labels": "1=Same as permanent address; 16=Another village/neighborhood in permanent address's county/city/district; 17=Abroad",
        "caveat": "The 2015 returner module asks where the hukou was at the last interview relative to the permanent address; preserve the historical time point and wave-specific codes. Do not publish underlying geographic details or treat this as current hukou location.",
    },
    "current_marital_status": {
        "label": "当前婚姻状况",
        "domain": "marital and household status",
        "fields": {"2011": ["be001"], "2013": ["be001"], "2015": ["be001"], "2018": ["be001"]},
        "construct": "Current marital-status response candidate.",
        "caveat": "Only mapped in 2011–2018 source inventory; no 2020 equivalent is asserted. Distinguish marital status from cohabitation and marriage history fields.",
    },
    "prior_wave_education_attainment_2013": {
        "label": "上一轮最高学历（2013回访核对/更正）",
        "domain": "education and social position",
        "fields": {"2013": ["bd001_w2_3"]},
        "construct": "Historical education attainment at the prior interview, reported only on the correction route.",
        "labels": "1=No formal education; 2=Did not finish primary school but can read/write; 3=Sishu/home school; 4=Elementary; 5=Middle; 6=High; 7=Vocational; 8=Two-/three-year college; 9=Four-year college/bachelor; 10=Master; 11=PhD",
        "value_label_source": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
        "mapping_status": "historical-wave education candidate; official 2013 questionnaire categories and correction route reviewed",
        "caveat": "This is the previous-wave education level, asked when the preloaded record is disputed. It is not current 2013 attainment and is structurally route-selected; use only with the official education derivation/route and never combine with bd001_w2_4 as if they were identical response items.",
    },
    "single_marriage_year_2013": {
        "label": "唯一一次婚姻年份（2013条件回顾项）",
        "domain": "marital and household status",
        "fields": {"2013": ["be004_1"]},
        "construct": "Year of marriage for respondents on the BE004 route, whose total reported number of marriages is one.",
        "unit": "calendar year",
        "mapping_status": "conditional marriage-history candidate; official 2013 questionnaire routing and year field reviewed",
        "caveat": "BE004 is asked only when the questionnaire routes through BE003=1; repeat respondents reporting a new marriage since the prior interview route to BE009 instead. This is not a general first-marriage date for all respondents and must remain separate from the BE009 most-recent-marriage date.",
    },
    "single_marriage_month_2013": {
        "label": "唯一一次婚姻月份（2013条件回顾项）",
        "domain": "marital and household status",
        "fields": {"2013": ["be004_2"]},
        "construct": "Month of marriage for respondents on the BE004 route, whose total reported number of marriages is one.",
        "unit": "calendar month",
        "mapping_status": "conditional marriage-history candidate; official 2013 questionnaire routing and month coding reviewed",
        "caveat": "BE004 is asked only when the questionnaire routes through BE003=1; repeat respondents reporting a new marriage since the prior interview route to BE009 instead. Month 0 means month not recalled, not January or a valid month. Keep separate from BE009 most-recent-marriage month.",
    },
}

rows = []
for concept, spec in SPEC.items():
    for wave, codes in spec["fields"].items():
        for code in codes:
            found = raw[(raw.wave == wave) & (raw.variable.str.lower() == code.lower())]
            if found.empty:
                raise SystemExit(f"Missing source field in official metadata: {wave} {code}")
            for rec in found.itertuples(index=False):
                rows.append({
                    "wave": wave, "code": code, "concept_id": concept,
                    "concept_label": spec["label"], "domain": "sociodemographic and social context",
                    "module": rec.module, "source_label": rec.variable_label,
                    "mapping_status": spec.get("mapping_status", "candidate current-state mapping from official wave-variable metadata; route/value review required"),
                    "unit": spec.get("unit", ""),
                    "value_labels": spec.get("labels", ""),
                    "value_label_status": ("official questionnaire and Codebook response labels reviewed" if spec.get("labels") else ""),
                    "value_label_source": spec.get("value_label_source", "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt" if spec.get("labels") else ""),
                    "construct": spec["construct"], "caveat": spec["caveat"],
                    "source_archive": f"{rec.source}; official wave questionnaire/codebook",
                })

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "demographic_social_exposure_mapping_v1.csv", index=False, encoding="utf-8-sig")
summary = (out.groupby(["concept_id", "concept_label"], dropna=False)
           .agg(waves=("wave", lambda x: ",".join(sorted(set(x)))), source_fields=("code", "size"),
                source_codes=("code", lambda x: ";".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "demographic_social_exposure_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"demographic/social mappings={len(out)}; concepts={out.concept_id.nunique()}")
