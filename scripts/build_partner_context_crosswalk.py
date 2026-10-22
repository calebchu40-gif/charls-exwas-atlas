"""Map respondent partnership and partner education metadata, without microdata."""
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
    "2020": "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt",
}
MARITAL_VALUES = "1=Married and living with spouse; 2=Married but temporarily not living with spouse; 3=Separated; 4=Divorced; 5=Widowed; 6=Never married (official wave response categories; frequencies omitted)"
EDUCATION_2011 = "1=No formal education; 2=Did not finish primary but literate; 3=Sishu/home school; 4=Elementary; 5=Middle school; 6=High school; 7=Vocational; 8=Two/three-year college; 9=Four-year college (official questionnaire/codebook categories)"
EDUCATION_2013_2015 = "1=No formal education; 2=Did not finish primary but literate; 3=Sishu/home school; 4=Elementary; 5=Middle school; 6=High school; 7=Vocational; 8=Two/three-year college; 9=Four-year college; 10=Master's; 11=Doctoral degree (official questionnaire categories; codebook frequencies omitted)"

SPECS = {
    "cohabiting_partner_status": {
        "label": "是否与伴侣以配偶身份共同生活", "fields": {"2011": ["be002"], "2018": ["be002"], "2020": ["ba012"]},
        "unit": "binary response (official codes retained)",
        "semantics": "current cohabitation with a partner; asked only on unmarried/separated/divorced/widowed routes",
        "values": "1=Yes; 2=No (official questionnaire/codebook labels)",
        "caveat": "2011 asks whether an unmarried respondent is living with a partner; 2018 asks whether the respondent has a mate living together as a couple; 2020 asks whether anyone is living with the respondent as a spouse. The 2011/2018 items follow selected non-currently-married status routes. The available 2020 English questionnaire extraction does not show its triggering route although the codebook denominator is narrower than the full marital-status item; preserve this unresolved eligibility and never infer No from a skip. Exact wording/pathways remain wave-specific.",
    },
    "partner_highest_education": {
        "label": "配偶/伴侣最高受教育程度", "fields": {"2011": ["bf004"], "2013": ["bf004"], "2015": ["bf004"]},
        "unit": "ordinal/categorical education level; preserve original wave categories",
        "semantics": "partner's highest attained education, excluding adult education where specified",
        "values_by_wave": {"2011": EDUCATION_2011, "2013": EDUCATION_2013_2015, "2015": EDUCATION_2013_2015},
        "caveat": "Available only through the spouse/partner information route; not applicable to respondents without a reported spouse/partner and not a respondent-level education measure. Preserve each wave's categories and missing/skip route. This may be a socioeconomic exposure or a confounder depending on the estimand; do not adjust for it automatically. 2018 has no directly equivalent BF004 field in the reviewed catalog.",
    },
    "marital_status_current": {
        "label": "当前婚姻状态", "fields": {"2011": ["be001"], "2013": ["be001"], "2015": ["be001"], "2018": ["be001"], "2020": ["ba011"]},
        "unit": "nominal categorical status; original wave codes retained",
        "semantics": "respondent's current marital status, with temporary spouse absence distinguished from separation",
        "values": MARITAL_VALUES,
        "caveat": "The source categories distinguish temporarily living apart for work/other reasons from separated, divorced, widowed, and never married. Preserve the original six categories and wave-specific wording; do not treat the numeric codes as an ordinal scale or collapse routes without a prespecified estimand.",
    },
}

rows = []
for concept, spec in SPECS.items():
    for wave, codes in spec["fields"].items():
        for code in codes:
            found = raw[(raw.wave == wave) & raw.variable.str.lower().eq(code.lower())]
            if found.empty:
                raise SystemExit(f"Official metadata field missing: {wave} {code}")
            for rec in found.itertuples(index=False):
                rows.append({
                    "wave": wave, "code": code, "concept_id": concept,
                    "concept_label": spec["label"], "domain": "sociodemographic and social context",
                    "module": rec.module, "source_label": rec.variable_label,
                    "unit": spec["unit"], "value_labels": spec.get("values_by_wave", {}).get(wave, spec.get("values", "")),
                    "value_semantics": spec["semantics"],
                    "mapping_status": "official questionnaire and codebook reviewed; candidate mapping, route-specific denominator retained",
                    "caveat": spec["caveat"], "source_archive": f"{rec.source}; {DOCS[wave]}",
                })

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "partner_context_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
summary = (out.groupby(["concept_id", "concept_label"], dropna=False)
           .agg(waves=("wave", lambda x: ",".join(sorted(set(x)))), mappings=("code", "size"),
                source_codes=("code", lambda x: ";".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "partner_context_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"partner context concepts={out.concept_id.nunique()} mappings={len(out)}")
