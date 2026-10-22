"""Build the official wave-specific lookup for returning home while away."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUT = AUDIT / "home_return_frequency_crosswalk_v1.csv"

questionnaire_2011 = ROOT / "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"
codebook_2011 = ROOT / "sources_official/CHARLS_2011_Codebook_extracted.txt"
questionnaire_2013 = ROOT / "sources_official/CHARLS_2013_Questionnaire_extracted.txt"
codebook_2013 = ROOT / "sources_official/CHARLS_2013_Codebook_extracted.txt"

texts = {
    "2011_questionnaire": questionnaire_2011.read_text(encoding="utf-8", errors="ignore").replace("\x00", "").lower(),
    "2011_codebook": codebook_2011.read_text(encoding="utf-8", errors="ignore").replace("\x00", "").lower(),
    "2013_questionnaire": questionnaire_2013.read_text(encoding="utf-8", errors="ignore").replace("\x00", "").lower(),
    "2013_codebook": codebook_2013.read_text(encoding="utf-8", errors="ignore").replace("\x00", "").lower(),
}
for key in ("2011_questionnaire", "2011_codebook", "2013_questionnaire", "2013_codebook"):
    if "ba005" not in texts[key]:
        raise SystemExit(f"Official source lacks BA005: {key}")
if "return to this home almost every week" not in texts["2011_questionnaire"]:
    raise SystemExit("2011 questionnaire weekly-return question not verified")
if "go home almost every weekend" not in texts["2013_questionnaire"] or "go home once two weeks" not in texts["2013_questionnaire"]:
    raise SystemExit("2013 questionnaire frequency categories not verified")
if "ba005 : return home every week" not in texts["2011_codebook"]:
    raise SystemExit("2011 CodeBook BA005 entry not found")
if "2 no" not in texts["2011_codebook"].split("ba005 : return home every week", 1)[1][:250]:
    raise SystemExit("2011 CodeBook binary response labels not verified")
if "go home almost every day" not in texts["2013_codebook"] or "go home once two weeks or more" not in texts["2013_codebook"]:
    raise SystemExit("2013 CodeBook ordered response labels not verified")

raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
expected = {"2011": "household_and_community_questionnaire_data.rar", "2013": "CHARLS2013_Dataset.zip"}
rows = []
for wave, questionnaire, codebook, concept_id, concept_label, labels, status, value_status, construct, value_semantics, caveat in [
    (
        "2011", questionnaire_2011, codebook_2011,
        "away_school_work_weekly_home_return_2011", "Weekly home return while away for school/work (2011)",
        "1=Yes; 2=No",
        "questionnaire and CodeBook agree on binary weekly-return item; candidate mapping, denominator and analysis eligibility require review",
        "official questionnaire/CodeBook binary response labels reviewed; frequencies omitted",
        "Whether the respondent attends school or works away from home but usually returns to this household almost every week",
        "Binary weekly-return status; not an ordinal return-frequency scale and not harmonized with 2013",
        "The 2011 baseline questionnaire asks a binary almost-every-week return question and the CodeBook labels it 1=Yes, 2=No. Do not interpret it as the 2013 three-category frequency measure or combine with the 2020 ba005 interview-address type.",
    ),
    (
        "2013", questionnaire_2013, codebook_2013,
        "away_school_work_return_home_frequency", "Return-home frequency while away for school/work (2013)",
        "1=Go home almost every day; 2=Go home almost every weekend; 3=Go home once every two weeks or more",
        "questionnaire and CodeBook response categories reviewed; candidate mapping, denominator and analysis eligibility require review",
        "official questionnaire/CodeBook response labels reviewed; frequencies omitted",
        "Respondent-reported frequency of returning to this household while attending school or work away from home",
        "Three ordered categories for 2013 only; no cross-wave harmonized scale is established",
        "Single-wave candidate for the respondent's return-home frequency while attending school or work away from home. The item does not measure distance, duration away, or current employment. Keep its three original categories; do not combine with the 2011 binary weekly-return item or 2020 ba005.",
    ),
]:
    field = raw[(raw.wave == wave) & (raw.variable.str.lower() == "ba005")]
    if field.empty or field.iloc[0].source != expected[wave]:
        raise SystemExit(f"No unique official source-catalog match for {wave} ba005")
    questionnaire_ref = questionnaire.relative_to(ROOT).as_posix()
    codebook_ref = codebook.relative_to(ROOT).as_posix()
    rows.append({
        "wave": wave,
        "code": "ba005",
        "concept_id": concept_id,
        "concept_label": concept_label,
        "domain": "social determinants",
        "module": "Demographic_Background",
        "source_label": str(field.iloc[0].variable_label),
        "value_labels": labels,
        "value_label_status": value_status,
        "value_label_source": f"{questionnaire_ref}; {codebook_ref}",
        "mapping_status": status,
        "construct": construct,
        "value_semantics": value_semantics,
        "caveat": caveat,
        "source_archive": f"{expected[wave]}; {questionnaire_ref}; {codebook_ref}",
        "questionnaire_source": questionnaire_ref,
    })

frame = pd.DataFrame(rows)
if frame.duplicated(["wave", "code"]).any():
    raise SystemExit("Duplicate home-return frequency wave/code mapping")
frame.to_csv(OUT, index=False, encoding="utf-8-sig")

label_rows = []
for wave, labels, status, source in [
    ("2011", "1=Yes; 2=No", "official questionnaire and CodeBook agree; frequencies omitted", codebook_2011),
    ("2013", "1=Go home almost every day; 2=Go home almost every weekend; 3=Go home once every two weeks or more", "official questionnaire and CodeBook labels reviewed; frequencies omitted", codebook_2013),
]:
    label_rows.append({
        "wave": wave, "code": "ba005", "value_labels": labels,
        "value_label_status": status,
        "value_label_source": source.relative_to(ROOT).as_posix(),
    })
pd.DataFrame(label_rows).to_csv(AUDIT / "home_return_frequency_value_label_review_v1.csv", index=False, encoding="utf-8-sig")
print("Wrote 2 wave mappings for 2 wave-specific candidate concepts; 2011 binary and 2013 ordinal measures remain separate.")
