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

# The 2011 baseline questionnaire asks the respondent about a father, then
# instructs the interviewer to repeat the parent section for the respondent's
# mother and both in-laws. The metadata-only field inventory contains four
# repeated CA009 slots, but the suffix-to-relative linkage is not documented in
# the public questionnaire. Keep these as a generic parent-slot candidate and
# do not label them as biological father/mother until the authorized release's
# slot linkage is verified.
PARENT_SLOT_2011 = [f"ca009_{i}_" for i in range(1, 5)]

rows = []
for code in PARENT_SLOT_2011:
    found = RAW[(RAW.wave == "2011") & RAW.module.str.lower().eq("family_information") & RAW.variable.str.lower().eq(code)]
    if found.empty:
        raise SystemExit(f"Missing 2011 parent education source field: 2011/{code}")
    rec = found.iloc[0]
    rows.append({
        "wave": "2011", "code": code,
        "concept_id": "parent_slot_education_2011",
        "concept_label": "亲属记录最高受教育程度（2011；关系槽位待核）",
        "domain": "early-life and family socioeconomic context",
        "module": rec.module, "source_label": rec.variable_label,
        "mapping_status": "discovery candidate only; questionnaire item reviewed; repeated parent-slot suffix-to-relative linkage unresolved; not approved for respondent-level analysis",
        "unit": "repeated parent/in-law slot; relation and respondent linkage must be verified",
        "value_labels": LABELS,
        "value_label_status": "2011 questionnaire lists 11 response options; Codebook lists four generic CA009 parent-education slots but does not map suffixes to relatives; Codebook categories and authorized-release coding not reconciled; frequencies omitted",
        "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
        "construct": "Reported education attainment in a repeated family parent slot; do not interpret as the respondent's own education or as a specific biological parent's education.",
        "value_semantics": "categorical parent-slot education; retain all four source slots separately and do not aggregate or harmonize until slot-to-relative linkage and release coding are verified",
        "caveat": "The 2011 questionnaire defines CA009 as the father's highest education and instructs interviewers to repeat the parent section for the respondent's mother, father-in-law and mother-in-law in that order. The Codebook lists four generic CA009 Parent' Highest Level of Education slots but does not identify which suffix belongs to which relative. The questionnaire lists 11 response options, while the Codebook's slot tables do not establish that every option is present in the released coding. Retain a generic slot identity; do not assign suffixes to relatives, use as a respondent-level exposure, or assume codes 10/11 are available until authorized-release field coding and routing are verified. The four slots are repeated relative records, not four independent exposures. Do not infer skipped parent items as no schooling; Codebook frequencies are omitted and not used.",
        "source_archive": "2011 metadata-only source-field inventory (not included); official baseline household questionnaire",
    })

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
