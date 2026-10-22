"""Map respondent's biological-parent education as a wave-specific early-life SES candidate."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
RAW = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

LABELS = (
    "1=No formal education (illiterate); 2=Did not finish primary school; "
    "3=Sishu/home school; 4=Elementary; 5=Middle; 6=High; 7=Vocational; "
    "8=Two-/three-year college/associate degree; 9=Four-year college/bachelor's; "
    "10=Master's; 11=Doctoral/PhD (where offered)"
)

FIELDS = [
    ("2013", "ca009_1_", "respondent_biological_fathers_education", "父亲最高受教育程度", "Father's Highest Level of Education",
     "Respondent's biological father's reported education; a familial socioeconomic-context proxy, not a respondent education measure.",
     "2013 parent module asks the respondent's father; preserve the father-specific slot. Skip/preload availability depends on prior interview knowledge; do not infer missing as no schooling."),
    ("2013", "ca009_2_", "respondent_biological_mothers_education", "母亲最高受教育程度", "Mother's Highest Level of Education",
     "Respondent's biological mother's reported education; a familial socioeconomic-context proxy, not a respondent education measure.",
     "Preserve the mother-specific slot. Skip/preload availability depends on prior interview knowledge; do not infer missing as no schooling."),
    ("2015", "ca009_1_", "respondent_biological_fathers_education", "父亲最高受教育程度", "R's Biological Father's Highest Level of Education",
     "Respondent's biological father's reported education; a familial socioeconomic-context proxy, not a respondent education measure.",
     "The 2015 parent module routes questions according to whether the biological parent is alive and whether prior information is available; structural skips and missing prior knowledge are not low education."),
    ("2015", "ca009_2_", "respondent_biological_mothers_education", "母亲最高受教育程度", "R's Biological Mother's Highest Level of Education",
     "Respondent's biological mother's reported education; a familial socioeconomic-context proxy, not a respondent education measure.",
     "The 2015 parent module routes questions according to whether the biological parent is alive and whether prior information is available; structural skips and missing prior knowledge are not low education."),
]

rows = []
for wave, code, concept, label, source_label, construct, caveat in FIELDS:
    found = RAW[(RAW.wave == wave) & RAW.variable.str.lower().eq(code.lower())]
    if found.empty:
        raise SystemExit(f"Missing official source field: {wave}/{code}")
    rec = found.iloc[0]
    rows.append({
        "wave": wave, "code": code, "concept_id": concept, "concept_label": label,
        "domain": "early-life and family socioeconomic context", "module": rec.module,
        "source_label": source_label,
        "mapping_status": "candidate early-life family-context exposure; exact biological-parent slot, questionnaire route, and codebook labels reviewed",
        "unit": "", "value_labels": LABELS,
        "value_label_status": "official wave questionnaire and Codebook response categories reviewed; frequency counts omitted",
        "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        "construct": construct,
        "value_semantics": "categorical education attainment; retain wave-specific source codes and harmonize by label only after release-version and route review",
        "caveat": caveat + " Do not merge in-laws, spouse's parents, step/adoptive parents, or sibling slots into the respondent's biological-parent exposure. This is a retrospective proxy for family socioeconomic context, not a direct measure of the respondent's childhood conditions.",
        "source_archive": f"{rec.source}; official wave questionnaire/codebook",
    })

out = pd.DataFrame(rows)
if out.duplicated(["wave", "code"]).any():
    raise SystemExit("Duplicate wave/code in parent education crosswalk")
out.to_csv(AUDIT / "parent_education_exposure_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"biological-parent education mappings={len(out)}; concepts={out.concept_id.nunique()}")
